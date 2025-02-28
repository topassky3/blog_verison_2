from django.views.generic import TemplateView

class VerTutorialesView(TemplateView):
    template_name = ('leer_tutoriales/mis_tutoriales.html')
