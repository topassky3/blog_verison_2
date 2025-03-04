from django.views.generic import DetailView
from core.models import Podcast

class PodcastDetailView(DetailView):
    model = Podcast
    template_name = "escuchar_podcast/escuchar_podcast.html"
    context_object_name = "podcast"
