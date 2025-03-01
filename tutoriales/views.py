from django.views.generic import TemplateView
from core.models import Tutorial, Category
from django.views.generic import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

class TutorialesView(TemplateView):
    template_name = "tutoriales/tutoriales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Parámetros de búsqueda y filtro de categoría
        query = self.request.GET.get('q', '')
        cat_slug = self.request.GET.get('cat', 'all')

        # Obtén todos los tutoriales publicados ordenados
        tutorial_list = Tutorial.objects.filter(publicado=True).order_by('-created_at')

        # Aplica la búsqueda en título, duración o nivel
        if query:
            tutorial_list = tutorial_list.filter(
                Q(title__icontains=query) |
                Q(duration__icontains=query) |
                Q(level__icontains=query)
            )

        # Filtra por categoría si se ha seleccionado una distinta a "all"
        if cat_slug != 'all':
            tutorial_list = tutorial_list.filter(category__slug=cat_slug)

        # Paginación: 6 tutoriales por página
        paginator = Paginator(tutorial_list, 6)
        page = self.request.GET.get('page')
        try:
            tutorials = paginator.page(page)
        except PageNotAnInteger:
            tutorials = paginator.page(1)
        except EmptyPage:
            tutorials = paginator.page(paginator.num_pages)

        context['tutorials'] = tutorials
        context['categories'] = Category.objects.all()  # Para generar las opciones dinámicamente
        context['search_query'] = query  # Para preservar el valor en el input
        context['selected_category'] = cat_slug  # Para marcar la categoría activa
        return context


class TutorialDetailView(DetailView):
    model = Tutorial
    template_name = "leer_tutoriales/mis_tutoriales.html"
    context_object_name = "tutorial"
