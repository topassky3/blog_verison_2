from django.views.generic import TemplateView, DetailView
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.models import Tutorial, Category

class TutorialesView(TemplateView):
    template_name = "tutoriales/tutoriales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        cat_slug = self.request.GET.get('cat', 'all')

        # Obtenemos los tutoriales publicados y agregamos las anotaciones:
        # - average_rating: Promedio de valoraciones de los comentarios.
        # - comments_count: Total de comentarios.
        tutorial_list = Tutorial.objects.filter(publicado=True).annotate(
            average_rating=Avg('comments__rating'),
            comments_count=Count('comments')
        ).order_by('-created_at')

        # Filtro de búsqueda
        if query:
            tutorial_list = tutorial_list.filter(
                Q(title__icontains=query) |
                Q(duration__icontains=query) |
                Q(level__icontains=query)
            )

        # Filtro por categoría
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

        # Para cada tutorial en la página, calculamos la valoración entera redondeada
        for tutorial in tutorials:
            if tutorial.average_rating is not None:
                tutorial.integer_rating = int(round(tutorial.average_rating))
            else:
                tutorial.integer_rating = 0

        context['tutorials'] = tutorials
        context['categories'] = Category.objects.all()
        context['search_query'] = query
        context['selected_category'] = cat_slug
        return context

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from core.models import Tutorial

@method_decorator(login_required(login_url='/login/'), name='dispatch')
class TutorialDetailView(DetailView):
    model = Tutorial
    template_name = "leer_tutoriales/mis_tutoriales.html"
    context_object_name = "tutorial"
