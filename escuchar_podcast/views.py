from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from core.models import Podcast
from core.models import PodcastComment  # Asegúrate de importar el modelo correcto
from .forms import PodcastCommentForm


class PodcastDetailView(FormMixin, DetailView):
    model = Podcast
    template_name = "escuchar_podcast/escuchar_podcast.html"
    context_object_name = "podcast"
    form_class = PodcastCommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Comentarios principales para este podcast
        context['top_level_comments'] = PodcastComment.objects.filter(
            podcast=self.object, parent__isnull=True
        ).order_by('-created_at')

        # Episodios anteriores: filtra por fecha y, si es posible, por la misma categoría
        if self.object.category:
            previous_episodes = Podcast.objects.filter(
                created_at__lt=self.object.created_at,
                category=self.object.category
            ).order_by('-created_at')
        else:
            previous_episodes = Podcast.objects.filter(
                created_at__lt=self.object.created_at
            ).order_by('-created_at')
        context['previous_episodes'] = previous_episodes

        # Incluye el formulario de comentario
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.podcast = self.object  # Asigna el podcast actual
            comment.author = request.user
            # Verifica si se envió un comentario padre
            parent_id = request.POST.get('parent')
            if parent_id:
                try:
                    from core.models import PodcastComment
                    parent_comment = PodcastComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except PodcastComment.DoesNotExist:
                    pass
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('escuchar_podcast', kwargs={'pk': self.object.pk}) + "#comments"

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import PodcastComment

@login_required
@require_POST
def toggle_podcast_comment_like(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = PodcastComment.objects.get(id=comment_id)
    except PodcastComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        # Si el usuario ya dio "no me gusta", se quita
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
def toggle_podcast_comment_dislike(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = PodcastComment.objects.get(id=comment_id)
    except PodcastComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        # Si el usuario ya dio "me gusta", se quita
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
def delete_podcast_comment(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = PodcastComment.objects.get(id=comment_id, author=request.user)
        comment.delete()
    except PodcastComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado o no tienes permiso para borrarlo.'}, status=404)

    return JsonResponse({'success': True})
