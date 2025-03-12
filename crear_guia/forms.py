from django import forms
from core.models import Guia

class GuiaForm(forms.ModelForm):
    class Meta:
        model = Guia
        fields = ['title', 'description', 'category', 'image', 'code_file']
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'category': 'Categoría',
            'image': 'Imagen Representativa',
            'code_file': 'Código de la Guía (.zip)',
        }
