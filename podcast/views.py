from django.views.generic import ListView
from core.models import Podcast, PodcastCategory

class PodcastListView(ListView):
    model = Podcast
    template_name = "podcast/podcast.html"
    context_object_name = "podcasts"

    def get_queryset(self):
        queryset = Podcast.objects.all().order_by('-created_at')
        # Filtrado opcional: si se envía ?cat=slug_de_categoria, filtra los podcasts
        category_slug = self.request.GET.get('cat')
        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrega las categorías específicas de podcasts
        context['categories'] = PodcastCategory.objects.all().order_by('name')
        return context
