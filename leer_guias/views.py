# leer_guias/views.py
from django.conf import settings  # Necesario para usar settings.LOGIN_URL
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin  # Ya lo usas para DownloadGuiaCodeFileView
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.http import FileResponse, Http404, JsonResponse  # JsonResponse ya estaba
from django.shortcuts import get_object_or_404, redirect  # redirect es necesario
from django.urls import reverse
from django.utils.decorators import method_decorator  # Para decorar métodos en CBV
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
# from django.utils.html import escape # No se usa explícitamente en el fragmento modificado
# from django.contrib.auth.views import redirect_to_login # login_required lo hace automáticamente

from core.models import Guia, GuiaComment, Lector
from .forms import GuiaCommentForm


class GuiaDetailView(FormMixin, DetailView):
    model = Guia
    template_name = 'leer_guias/guia_detail.html'
    form_class = GuiaCommentForm
    context_object_name = "guia"

    def get_user(self):
        """
        Este método parece ser una lógica personalizada para obtener un usuario 'efectivo',
        posiblemente para mostrar contenido o como autor por defecto si el usuario no está logueado.
        Para la autenticación de comentarios, nos basaremos en request.user.is_authenticated.
        """
        if self.request.user.is_authenticated:
            return self.request.user
        # Esta línea podría ser para un perfil de usuario anónimo específico ("electro")
        # o un fallback. Asegúrate de que su propósito sea el deseado.
        return get_object_or_404(Lector, username="electro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guia = self.object
        context['guia'] = guia

        blocks_qs = guia.blocks.all().order_by('order')
        processed_blocks = []
        for block in blocks_qs:
            content = block.content
            image_url = None
            if block.block_type == 'image' and block.image:
                image_url = block.image.url
            processed_blocks.append({
                'id': block.id,
                'block_type': block.block_type,
                'content': content,
                'order': block.order,
                'image_url': image_url
            })

        total_processed_blocks = len(processed_blocks)

        # Usuario efectivo para la lógica de visualización de contenido (ej. límite del 60%)
        # Esto usa tu lógica de get_user(), que puede devolver 'electro' para anónimos.
        effective_user_for_display = self.get_user()
        effective_subscription = getattr(effective_user_for_display, 'subscription', None)

        context['mostrar_limite'] = False
        visible_blocks_data = processed_blocks

        # Lógica para limitar contenido al 60% para usuarios "Básico" que no son autores
        is_author = self.request.user.is_authenticated and self.request.user == guia.author

        if not is_author and \
                effective_user_for_display != guia.author and \
                effective_subscription and effective_subscription.plan == "Básico" and \
                total_processed_blocks > 0:
            visible_count = int(total_processed_blocks * 0.6)
            visible_blocks_data = processed_blocks[:visible_count]
            context['mostrar_limite'] = True

        context['visible_blocks'] = visible_blocks_data

        top_level_comments = guia.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments

        if 'form' not in context:
            context['form'] = self.get_form()

        # effective_user se usa en la plantilla para, por ejemplo, el botón de descarga.
        context['effective_user'] = effective_user_for_display
        return context

    @method_decorator(login_required)  # Redirige a settings.LOGIN_URL por defecto
    def post(self, request, *args, **kwargs):
        # Gracias al decorador @login_required, este método solo se ejecutará
        # si request.user.is_authenticated es True.
        # Si no está autenticado, Django ya habrá redirigido al login.
        self.object = self.get_object()  # Necesario para FormMixin
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.guia = self.object
        comment.author = self.request.user  # El usuario está autenticado aquí

        # Manejar comentario padre para respuestas
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
                comment.parent = GuiaComment.objects.get(id=parent_id)
            except GuiaComment.DoesNotExist:
                form.add_error(None, "La respuesta hace referencia a un comentario que no existe.")
                return self.form_invalid(form)
            except ValueError:  # Si parent_id no es un entero válido
                form.add_error(None, "ID de comentario padre inválido.")
                return self.form_invalid(form)

        comment.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redirige a la misma página de la guía, anclando a la sección de comentarios
        return reverse('guia_detail', kwargs={'pk': self.object.pk}) + '#comments'


# --- Vistas AJAX para likes, dislikes, borrar (ya protegidas con @login_required) ---
@login_required
@require_POST
def toggle_guia_comment_like(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id)
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    liked = False
    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        if user in comment.dislikes.all():
            comment.dislikes.remove(user)
        comment.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': comment.likes.count(),
        'dislike_count': comment.dislikes.count()
    })


@login_required
@require_POST
def toggle_guia_comment_dislike(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id)
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    disliked = False
    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
    else:
        if user in comment.likes.all():
            comment.likes.remove(user)
        comment.dislikes.add(user)
        disliked = True

    return JsonResponse({
        'disliked': disliked,
        'dislike_count': comment.dislikes.count(),
        'like_count': comment.likes.count()
    })


@login_required
@require_POST
def delete_guia_comment(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id, author=request.user)
        parent_id = comment.parent.id if comment.parent else None  # Para posible lógica de UI
        comment.delete()
        data = {'success': True}
        if parent_id:
            data['parent_id'] = parent_id  # Si es útil para actualizar la UI
        return JsonResponse(data)
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado o no tienes permiso para borrarlo.'}, status=404)


class DownloadGuiaCodeFileView(LoginRequiredMixin, View):  # Ya usa LoginRequiredMixin
    def get(self, request, pk, *args, **kwargs):
        guia = get_object_or_404(Guia, pk=pk)
        if not guia.code_file:
            raise Http404("No se encontró el archivo de código para esta guía.")

        subscription = getattr(request.user, 'subscription', None)

        if subscription and subscription.plan == "Básico" and request.user != guia.author:  # Modificado para permitir al autor
            # raise PermissionDenied("No tienes permiso para descargar este archivo. Actualiza tu suscripción.") # PermissionDenied no está importado
            # Es mejor redirigir o mostrar un mensaje claro. Por ahora, mantenemos la excepción.
            return JsonResponse({'error': 'No tienes permiso para descargar este archivo. Actualiza tu suscripción.'},
                                status=403)

        return FileResponse(
            guia.code_file.open('rb'),
            as_attachment=True,
            filename=guia.code_file.name  # Usa el nombre original del archivo
        )
    
# leer_guias/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from core.models import Guia, Lector  # Asegúrate de que los modelos necesarios estén importados

# ... (tus otras vistas como GuiaDetailView, etc., se quedan como están) ...


# --- NUEVA VISTA PARA CARGAR BLOQUES DE GUÍA VÍA AJAX ---
def load_all_guia_blocks(request, guia_id):
    guia = get_object_or_404(Guia, pk=guia_id)
    blocks_qs = guia.blocks.all().order_by('order')

    # Lógica para determinar el usuario (logueado o anónimo de fallback)
    if request.user.is_authenticated:
        effective_user = request.user
    else:
        # Usamos tu lógica de fallback para el usuario "electro"
        effective_user = get_object_or_404(Lector, username="electro")

    # Lógica para limitar el contenido al 60%
    mostrar_limite = False
    is_author = request.user.is_authenticated and request.user == guia.author
    effective_subscription = getattr(effective_user, 'subscription', None)

    if not is_author and effective_subscription and effective_subscription.plan == "Básico":
        total_blocks = blocks_qs.count()
        if total_blocks > 0:
            visible_count = int(total_blocks * 0.6)
            blocks_qs = blocks_qs[:visible_count]
            mostrar_limite = True

    # Procesar los bloques para enviar como JSON
    blocks_data = []
    for block in blocks_qs:
        block_data = {
            'id': block.id,
            'block_type': block.block_type,
            'content': block.content,
            'order': block.order,
            'image_url': block.image.url if block.block_type == 'image' and block.image else None
        }
        blocks_data.append(block_data)

    return JsonResponse({
        'blocks': blocks_data,
        'mostrar_limite': mostrar_limite
    })