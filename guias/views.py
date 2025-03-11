from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from core.models import Guia, GuiaCategory


class GuiasView(TemplateView):
    template_name = "guias/guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GuiaCategory.objects.all()

        # Consulta base de guías publicadas ordenadas por fecha de creación
        guias_list = Guia.objects.filter(publicado=True).order_by('-created_at')

        # Filtrado por categoría (se omite si se selecciona "Todos")
        category_slug = self.request.GET.get('category')
        if category_slug and category_slug != 'all':
            guias_list = guias_list.filter(category__slug=category_slug)

        # Filtrado por búsqueda en el título
        search_query = self.request.GET.get('search')
        if search_query:
            guias_list = guias_list.filter(title__icontains=search_query)

        # Paginación: 6 guías por página
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
