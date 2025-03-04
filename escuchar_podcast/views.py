from django.views.generic import TemplateView

class PodcastView(TemplateView):
    template_name = "escuchar_podcast/escuchar_podcast.html"
