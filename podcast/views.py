from django.views.generic import TemplateView

class PodcastView(TemplateView):
    template_name = "podcast/podcast.html"
