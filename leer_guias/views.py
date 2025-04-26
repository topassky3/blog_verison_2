# leer_guias/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.contrib.auth.views import redirect_to_login

from core.models import Guia, GuiaComment, Lector
from .forms import GuiaCommentForm

class GuiaDetailView(FormMixin, DetailView):
    model = Guia
    template_name = 'leer_guias/guia_detail.html'
    form_class = GuiaCommentForm
    context_object_name = "guia"

    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        return get_object_or_404(Lector, username="electro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guia = self.object # Renombrado para claridad
        context['guia'] = guia

        # Obtenemos los bloques originales de la base de datos
        blocks_qs = guia.blocks.all().order_by('order') # QuerySet original

        processed_blocks = [] # Lista para los diccionarios procesados
        for block in blocks_qs: # Iterar sobre los objetos GuiaBlock originales
            content = block.content
            image_url = None # Inicializar la URL de la imagen como None

            if block.block_type == 'code':
                # Decide si necesitas escapar aquí o confías en |safe y highlight.js
                # content = escape(content)
                pass
            elif block.block_type == 'image' and block.image: # Si es imagen Y tiene archivo
                # Obtenemos la URL de la imagen
                image_url = block.image.url

            # Creamos el diccionario para este bloque, AÑADIENDO image_url
            processed_blocks.append({
                'id': block.id,
                'block_type': block.block_type,
                'content': content, # Contenido de texto/code/latex
                'order': block.order,
                'image_url': image_url  # <-- ¡AQUÍ AÑADIMOS LA URL! (será None si no es imagen)
            })

        total_processed_blocks = len(processed_blocks) # Ahora contamos los diccionarios

        user = self.get_user()
        subscription = getattr(user, 'subscription', None)

        context['mostrar_limite'] = False
        # La variable que se pasa a la plantilla AHORA contiene la lista de diccionarios
        visible_blocks_data = processed_blocks

        if user != guia.author and subscription and subscription.plan == "Básico" and total_processed_blocks > 0:
            visible_count = int(total_processed_blocks * 0.6)
            # Cortamos la LISTA de diccionarios
            visible_blocks_data = processed_blocks[:visible_count]
            context['mostrar_limite'] = True

        # Pasamos la lista de diccionarios (completa o cortada) a la plantilla
        context['visible_blocks'] = visible_blocks_data

        # --- Resto del contexto (comentarios, formulario, etc.) ---
        top_level_comments = guia.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments

        if 'form' not in context:
            context['form'] = self.get_form()
        context['effective_user'] = self.get_user()
        # --- Fin del resto del contexto ---

        return context


# leer_guias/views.py (o donde manejes tus vistas AJAX para guías)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import GuiaComment

@login_required
@require_POST
def toggle_guia_comment_like(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id)
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        # Quitar "dislike" si lo tenía
        if user in comment.dislikes.all():
            comment.dislikes.remove(user)
        comment.likes.add(user)
        liked = True

    data = {
        'liked': liked,
        'like_count': comment.likes.count(),
        'dislike_count': comment.dislikes.count()
    }
    return JsonResponse(data)


@login_required
@require_POST
def toggle_guia_comment_dislike(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id)
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        # Quitar "like" si lo tenía
        if user in comment.likes.all():
            comment.likes.remove(user)
        comment.dislikes.add(user)
        disliked = True

    data = {
        'disliked': disliked,
        'dislike_count': comment.dislikes.count(),
        'like_count': comment.likes.count()
    }
    return JsonResponse(data)


@login_required
@require_POST
def delete_guia_comment(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = GuiaComment.objects.get(id=comment_id, author=request.user)
        parent_id = comment.parent.id if comment.parent else None
        comment.delete()
    except GuiaComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado o no tienes permiso para borrarlo.'}, status=404)

    data = {'success': True}
    if parent_id:
        data['parent_id'] = parent_id
    return JsonResponse(data)


from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Guia


class DownloadGuiaCodeFileView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        guia = get_object_or_404(Guia, pk=pk)
        if not guia.code_file:
            raise Http404("No se encontró el archivo de código para esta guía.")

        # Si el usuario tiene el plan Básico, denegamos el acceso
        try:
            subscription = request.user.subscription
        except Exception:
            subscription = None

        if subscription and subscription.plan == "Básico":
            raise PermissionDenied("No tienes permiso para descargar este archivo. Actualiza tu suscripción.")

        return FileResponse(
            guia.code_file.open('rb'),
            as_attachment=True,
            filename=guia.code_file.name
        )
