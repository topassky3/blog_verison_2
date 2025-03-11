# leer_guias/forms.py
from django import forms
from core.models import GuiaComment

class GuiaCommentForm(forms.ModelForm):
    class Meta:
        model = GuiaComment
        fields = ['content', 'rating']
        labels = {
            'content': 'Deja tu comentario:',
            'rating': 'Valoración (opcional):'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe aquí tu comentario sobre la guía...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = False
