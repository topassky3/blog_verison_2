from django.views.generic import TemplateView
from django.db.models import Avg
from core.models import Tutorial, Podcast, Guia

class InicioView(TemplateView):
    template_name = "inicio/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tutoriales destacados
        tutorials_destacados = Tutorial.objects.annotate(
            avg_rating=Avg('comments__rating')
        ).filter(avg_rating__gt=0).order_by('-avg_rating')[:3]

        # Podcasts destacados
        podcasts_destacados = Podcast.objects.annotate(
            avg_rating=Avg('comments__rating')
        ).filter(avg_rating__gt=0).order_by('-avg_rating')[:3]

        # Guías destacadas (suponiendo que en el modelo Guia los comentarios están en related_name="comments")
        guias_destacadas = Guia.objects.annotate(
            avg_rating=Avg('comments__rating')
        ).filter(avg_rating__gt=0).order_by('-avg_rating')[:3]

        context['tutorials_destacados'] = tutorials_destacados
        context['podcasts_destacados'] = podcasts_destacados
        context['guias_destacadas'] = guias_destacadas
        return context
