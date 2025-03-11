# leer_guias/views.py

from django.views.generic import DetailView
from core.models import Guia

class GuiaDetailView(DetailView):
    model = Guia
    template_name = "leer_guias/guia_detail.html"  # Ruta del template de ejemplo
    context_object_name = "guia"  # Nombre con el que se accederá al objeto en el template
