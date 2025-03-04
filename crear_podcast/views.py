from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from core.models import Podcast  # Asegúrate de que el modelo Podcast esté en core.models o en la app correspondiente
from .forms import PodcastForm

class CrearPodcartView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Podcast
    form_class = PodcastForm
    template_name = 'crear_podcast/crear_podcast.html'
    # Cambiamos el success_url para redirigir al perfil del escritor
    success_url = reverse_lazy('escritor_profile')

    def test_func(self):
        # Permitir el acceso solo si el usuario es autenticado y es escritor.
        return self.request.user.is_authenticated and self.request.user.es_escritor

    def form_valid(self, form):
        # Asigna el usuario autenticado como autor del podcast
        form.instance.author = self.request.user
        return super().form_valid(form)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from core.models import Podcast
from .forms import PodcastForm

class PodcastUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Podcast
    form_class = PodcastForm
    template_name = 'crear_podcast/crear_podcast.html'
    success_url = reverse_lazy('escritor_profile')  # Redirige al perfil del escritor tras editar

    def test_func(self):
        # Permite la edición solo si el usuario es autenticado, es escritor y es el autor del podcast
        podcast = self.get_object()
        return self.request.user.is_authenticated and self.request.user == podcast.author and self.request.user.es_escritor
