# --- Imports de Django y Python ---
import re
from django.utils.html import escape
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, FileResponse, Http404
from django.views.generic import DetailView, View
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db.models import Count, ExpressionWrapper, IntegerField

# --- Imports de librerías externas ---
import bleach

# --- Imports de tu proyecto ---
from core.models import Guia, GuiaComment, Lector
from .forms import GuiaCommentForm


class GuiaDetailView(FormMixin, DetailView):
    model = Guia
    template_name = 'leer_guias/guia_detail.html'
    form_class = GuiaCommentForm
    context_object_name = "guia"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guia = self.object

        # --- LÓGICA DE PROCESAMIENTO DE BLOQUES CON BLEACH (LA MAGIA) ---
        blocks_qs = guia.blocks.all().order_by('order')
        processed_blocks = []

        def escape_code_content(match):
            # Escapa el contenido encontrado dentro de las etiquetas <code>
            return f"<code>{escape(match.group(1))}</code>"

        for block in blocks_qs:
            content = block.content
            image_url = None

            if block.block_type == 'text':
                # PASO 1: Escapamos primero lo que está dentro de <code>...</code>
                content_with_placeholders = re.sub(
                    r'<code>(.*?)</code>',
                    escape_code_content,
                    block.content,
                    flags=re.DOTALL
                )
                # PASO 2: Limpiamos el resto del HTML con Bleach
                content = bleach.clean(
                    content_with_placeholders,
                    tags=settings.BLEACH_ALLOWED_TAGS,
                    attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
                )
            elif block.block_type == 'image' and block.image:
                image_url = block.image.url

            processed_blocks.append({
                'id': block.id,
                'block_type': block.block_type,
                'content': content,
                'order': block.order,
                'image_url': image_url
            })

        # --- Lógica para limitar contenido ---
        user = self.request.user if self.request.user.is_authenticated else get_object_or_404(Lector,
                                                                                              username="electro")
        is_author = self.request.user.is_authenticated and self.request.user == guia.author
        is_basic_or_anonymous = not self.request.user.is_authenticated or (
                    hasattr(user, 'subscription') and user.subscription.plan == "Básico")

        context['mostrar_limite'] = False
        visible_blocks_data = processed_blocks

        if not is_author and is_basic_or_anonymous and len(processed_blocks) > 0:
            visible_count = max(1, int(len(processed_blocks) * 0.6))
            visible_blocks_data = processed_blocks[:visible_count]
            context['mostrar_limite'] = True

        context['visible_blocks'] = visible_blocks_data

        # --- Lógica para comentarios y formulario ---
        context['top_level_comments'] = guia.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')

        if 'form' not in context:
            context['form'] = self.get_form()

        context['effective_user'] = user
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.guia = self.object
        comment.author = self.request.user
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
                comment.parent = GuiaComment.objects.get(id=parent_id)
            except (GuiaComment.DoesNotExist, ValueError):
                pass
        comment.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
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