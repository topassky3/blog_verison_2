from django.views.generic import TemplateView
from core.models import Tutorial
from django.views.generic import DetailView

class TutorialesView(TemplateView):
    template_name = "tutoriales/tutoriales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtra solo los tutoriales publicados, ordenándolos (por ejemplo, del más reciente al más antiguo)
        context['tutorials'] = Tutorial.objects.filter(publicado=True).order_by('-created_at')
        return context



class TutorialDetailView(DetailView):
    model = Tutorial
    template_name = "leer_tutoriales/mis_tutoriales.html"
    context_object_name = "tutorial"
