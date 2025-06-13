from django.views.generic import DetailView
from core.models import Lector, Tutorial, Guia, Podcast

class AuthorProfileView(DetailView):
    model = Lector
    template_name = 'leer_perfil/profile.html'
    context_object_name = 'author'
    # pk_url_kwarg le dice a DetailView que use 'pk' de la URL para buscar el Lector.

    def get_context_data(self, **kwargs):
        # Llama a la implementación base primero para obtener el contexto
        context = super().get_context_data(**kwargs)

        # self.get_object() nos da el autor (Lector) que se está viendo
        author = self.get_object()

        # Añadimos al contexto las listas de contenido publicado por ese autor
        context['tutorials'] = Tutorial.objects.filter(author=author, publicado=True).order_by('-created_at')
        context['guias'] = Guia.objects.filter(author=author, publicado=True).order_by('-created_at')
        context['podcasts'] = Podcast.objects.filter(author=author, publicado=True).order_by('-created_at')

        return context