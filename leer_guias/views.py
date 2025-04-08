# leer_guias/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404
from django.utils.html import escape

from core.models import Guia, GuiaComment, Lector
from .forms import GuiaCommentForm

class GuiaDetailView(FormMixin, DetailView):
    model = Guia
    template_name = 'leer_guias/guia_detail.html'
    form_class = GuiaCommentForm
    context_object_name = "guia"

    def get_user(self):
        """
        Retorna el usuario autenticado o, si no hay ninguno,
        devuelve al usuario por defecto "electro".
        """
        if self.request.user.is_authenticated:
            return self.request.user
        return get_object_or_404(Lector, username="electro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guia'] = self.object

        # Obtenemos y procesamos los bloques de la guía
        blocks = self.object.blocks.all().order_by('order')
        processed_blocks = []
        for block in blocks:
            content = block.content
            if block.block_type == 'code':
                content = escape(content)
            processed_blocks.append({
                'id': block.id,
                'block_type': block.block_type,
                'content': content,
                'order': block.order,
            })

        total_blocks = len(processed_blocks)

        # Obtenemos el usuario (real o el predeterminado "electro")
        user = self.get_user()

        # Intentamos obtener la suscripción del usuario
        subscription = None
        try:
            subscription = user.subscription
        except Exception:
            pass

        # Si el usuario (real o "electro") tiene plan Básico y no es el autor,
        # limitamos a mostrar solo el 60% de los bloques.
        if user != self.object.author and subscription and subscription.plan == "Básico" and total_blocks > 0:
            visible_count = int(total_blocks * 0.6)
            context['visible_blocks'] = processed_blocks[:visible_count]
            context['mostrar_limite'] = True
        else:
            context['visible_blocks'] = processed_blocks
            context['mostrar_limite'] = False

        # Procesamiento de comentarios (comentarios principales y sus datos)
        top_level_comments = self.object.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments

        if 'form' not in context:
            context['form'] = self.get_form()
        context['effective_user'] = self.get_user()
        return context

    def get_success_url(self):
        # Redirige al mismo detalle de la guía, anclando en #comments
        return reverse('guia_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        # Procesa el POST para crear un comentario
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.guia = self.object
        comment.author = self.request.user  # Se usa el usuario real para el comentario
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
                parent_comment = GuiaComment.objects.get(id=parent_id)
                comment.parent = parent_comment
            except GuiaComment.DoesNotExist:
                pass
        comment.save()
        return super().form_valid(form)


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
