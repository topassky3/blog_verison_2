from django.views.generic import TemplateView
from django.db.models import Avg
from core.models import Tutorial
from core.models import Podcast

class InicioView(TemplateView):
    template_name = "inicio/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos los tutoriales que tienen al menos una valoración y calculamos el promedio.
        tutorials_destacados = Tutorial.objects.annotate(
            avg_rating=Avg('comments__rating')
        ).filter(avg_rating__gt=0).order_by('-avg_rating')[:3]

        # De forma similar para los podcasts.
        podcasts_destacados = Podcast.objects.annotate(
            avg_rating=Avg('comments__rating')
        ).filter(avg_rating__gt=0).order_by('-avg_rating')[:3]

        context['tutorials_destacados'] = tutorials_destacados
        context['podcasts_destacados'] = podcasts_destacados
        return context
