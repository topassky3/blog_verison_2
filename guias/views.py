from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from core.models import Guia, GuiaCategory

class GuiasView(TemplateView):
    template_name = "guias/guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GuiaCategory.objects.all()
        guias_list = Guia.objects.filter(publicado=True).order_by('-created_at')
        # Paginación: 6 guías por página (ajusta si lo necesitas)
        paginator = Paginator(guias_list, 6)
        page = self.request.GET.get('page')
        try:
            guias = paginator.page(page)
        except PageNotAnInteger:
            guias = paginator.page(1)
        except EmptyPage:
            guias = paginator.page(paginator.num_pages)
        context['guias'] = guias
        return context
