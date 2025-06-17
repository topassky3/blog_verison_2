# crear_guia/forms.py
from django import forms
from core.models import Guia

class GuiaForm(forms.ModelForm):
    class Meta:
        model = Guia
        # --- AÑADE 'meta_description' A ESTA LISTA ---
        fields = ['title', 'description', 'meta_description', 'category', 'image', 'code_file']
        
        # --- OPCIONAL: AÑADE ETIQUETAS Y AYUDA PARA EL NUEVO CAMPO ---
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'meta_description': 'Meta Descripción (para SEO)',
            'category': 'Categoría',
            'image': 'Imagen Representativa',
            'code_file': 'Código de la Guía (.zip)',
        }
        help_texts = {
            'meta_description': 'Escribe una descripción corta (máx. 165 caracteres) para que aparezca en los resultados de Google.'
        }
        widgets = {
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }