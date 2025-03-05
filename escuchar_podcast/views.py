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
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('escuchar_podcast', kwargs={'pk': self.object.pk}) + "#comments"
