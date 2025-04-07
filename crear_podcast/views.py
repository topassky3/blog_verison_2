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

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from core.models import Podcast, Subscriber  # Ajusta si está en otra app

@login_required
@require_POST
def toggle_publish(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk, author=request.user)
    # Alterna el estado de publicación
    podcast.publicado = not podcast.publicado
    podcast.save()

    if podcast.publicado:
        # Enviar correo a los suscriptores
        subscribers = Subscriber.objects.all()  # Filtra si tienes 'active=True'
        recipient_list = [sub.email for sub in subscribers]
        if recipient_list:
            subject = "Nuevo Podcast Publicado en WebDev Blog"
            # Construir la URL absoluta al podcast
            podcast_url = request.build_absolute_uri(f"/escuchar-podcast/{podcast.pk}/")
            # Renderizar el contenido HTML a partir del template
            html_message = render_to_string("emails/new_podcast_email.html", {
                "podcast": podcast,
                "podcast_url": podcast_url,
            })
            plain_message = (
                f"Se ha publicado un nuevo podcast: {podcast.title}.\n"
                f"Escúchalo aquí: {podcast_url}\n\n"
                "¡Gracias por suscribirte a WebDev Blog!"
            )
            # Se utiliza EmailMultiAlternatives para enviar el correo con copia oculta
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],  # Dirección genérica en "to"
                bcc=recipient_list  # Los destinatarios en copia oculta
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

    return JsonResponse({'published': podcast.publicado})
