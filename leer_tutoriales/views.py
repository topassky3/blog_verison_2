from django.views.generic import TemplateView

class VerTutorialesView(TemplateView):
    template_name = ('leer_tutoriales/mis_tutoriales.html')


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from core.models import Tutorial
from .forms import CommentForm

class TutorialDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Tutorial
    template_name = 'leer_tutoriales/mis_tutoriales.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Se asigna la instancia del tutorial con la variable 'tutorial'
        context['tutorial'] = self.object
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def get_success_url(self):
        # Redirige a la misma URL del detalle del tutorial
        return reverse('tutorial_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Obtiene el tutorial actual
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Crea y guarda el comentario asignándole el tutorial y el usuario logueado
        comment = form.save(commit=False)
        comment.tutorial = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

