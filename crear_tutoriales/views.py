from django.views.generic import TemplateView

class TutorialCreateTemplateView(TemplateView):
    template_name = 'crear_tutoriales/tutorial_form.html'
