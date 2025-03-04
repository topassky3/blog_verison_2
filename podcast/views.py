from django.views.generic import ListView
from core.models import Podcast

class PodcastListView(ListView):
    model = Podcast
    template_name = "podcast/podcast.html"
    context_object_name = "podcasts"
