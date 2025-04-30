from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from core.models import Podcast, PodcastComment, Lector  # Asegúrate de tener importado Lector
from .forms import PodcastCommentForm
from django.contrib.auth.views import redirect_to_login

# Si deseas permitir acceso a usuarios no autenticados, se remueve el login_required o se implementa en cada acción de comentar/likes.
class PodcastDetailView(FormMixin, DetailView):
    model = Podcast
    template_name = "escuchar_podcast/escuchar_podcast.html"
    context_object_name = "podcast"
    form_class = PodcastCommentForm

    def get_effective_user(self):
        """
        Retorna el usuario autenticado o, en su defecto, al usuario por defecto "electro".
        """
        if self.request.user.is_authenticated:
            return self.request.user
        return get_object_or_404(Lector, username="electro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Top-level comments…
        context['top_level_comments'] = PodcastComment.objects.filter(
            podcast=self.object, parent__isnull=True
        ).order_by('-created_at')

        # 1) Solo los episodios con created_at **anterior** al actual
        # 2) Ordenados de más recientes a más antiguos
        # 3) Limitados a 5
        previous_qs = Podcast.objects.filter(
            created_at__lt=self.object.created_at
        ).order_by('-created_at')[:5]

        context['previous_episodes'] = previous_qs

        # Formulario y usuario efectivo…
        if 'form' not in context:
            context['form'] = self.get_form()
        context['effective_user'] = self.get_effective_user()

        return context

    def post(self, request, *args, **kwargs):
        # Si el usuario no está autenticado, redirige a la página de login.
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.podcast = self.object  # Asigna el podcast actual
            # Ahora se usa directamente request.user porque se confirmó la autenticación.
            comment.author = request.user
            parent_id = request.POST.get('parent')
            if parent_id:
                try:
                    parent_comment = PodcastComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except PodcastComment.DoesNotExist:
                    pass
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        # Redirecciona al mismo podcast, anclando en #comments
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


# views.py
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import PodcastComment


@login_required
@require_POST
def delete_podcast_comment(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = PodcastComment.objects.get(id=comment_id, author=request.user)
    except PodcastComment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado o no tienes permiso para borrarlo.'}, status=404)

    # Si el comentario es respuesta, guardamos el id del comentario padre
    parent_id = comment.parent.id if comment.parent else None

    # Borramos el comentario (si es comentario padre, se eliminarán sus respuestas en cascada)
    comment.delete()

    data = {'success': True}
    if parent_id:
        # Obtenemos el nuevo número de respuestas para el comentario padre
        parent_comment = PodcastComment.objects.get(id=parent_id)
        data['parent_id'] = parent_id
        data['replies_count'] = parent_comment.replies.count()

    return JsonResponse(data)
