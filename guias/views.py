from django.views.generic import TemplateView
from core.models import GuiaCategory

class GuiasView(TemplateView):
    template_name = "guias/guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GuiaCategory.objects.all()
        # Por el momento no se pasan las guías de la base de datos.
        return context
