from django.views.generic import ListView
from django.db.models import Q
from core.models import Podcast, PodcastCategory


class PodcastListView(ListView):
    model = Podcast
    template_name = "podcast/podcast.html"
    context_object_name = "podcasts"
    paginate_by = 6  # Mismo número de elementos por página que en tutoriales

    def get_queryset(self):
        queryset = Podcast.objects.all().order_by('-created_at')

        # 1) Obtener parámetros de categoría y búsqueda
        cat_slug = self.request.GET.get('cat', 'all')
        search_query = self.request.GET.get('q', '')

        # 2) Filtrar por categoría si no es "all"
        if cat_slug != 'all':
            queryset = queryset.filter(category__slug=cat_slug)

        # 3) Filtrar por búsqueda (título o descripción)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos las categorías para generar los enlaces
        context['categories'] = PodcastCategory.objects.all().order_by('name')
        # Pasamos el slug de la categoría y la búsqueda seleccionadas
        context['selected_category'] = self.request.GET.get('cat', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        return context


from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.shortcuts import redirect
from core.models import Podcast

class PodcastDeleteView(DeleteView):
    model = Podcast
    template_name = 'crear_podcast/podcast_confirm_delete.html'
    success_url = reverse_lazy('profile')  # O 'escritor_profile', según convenga

    def dispatch(self, request, *args, **kwargs):
        podcast = self.get_object()
        # Solo el autor puede borrar su podcast
        if not request.user.is_authenticated or request.user != podcast.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
