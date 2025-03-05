from django.views.generic import ListView
from core.models import Podcast, PodcastCategory

class PodcastListView(ListView):
    model = Podcast
    template_name = "podcast/podcast.html"
    context_object_name = "podcasts"
    paginate_by = 6  # Número de podcasts por página

    def get_queryset(self):
        queryset = Podcast.objects.all().order_by('-created_at')
        # Filtrado opcional por categoría
        category_slug = self.request.GET.get('cat')
        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrega las categorías de podcasts para el filtro
        context['categories'] = PodcastCategory.objects.all().order_by('name')
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
