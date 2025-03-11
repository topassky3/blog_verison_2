# guias/views.py
from django.views.generic import TemplateView
from core.models import Guia, GuiaCategory

class GuiasView(TemplateView):
    template_name = "guias/guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GuiaCategory.objects.all()
        # Se obtienen las guías publicadas, ordenadas por la fecha de creación (suponiendo que exista un campo created_at)
        context['guias'] = Guia.objects.filter(publicado=True).order_by('-created_at')
        return context
