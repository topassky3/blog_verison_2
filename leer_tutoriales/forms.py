from django import forms
from core.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'rating']
        labels = {
            'content': 'Deja tu comentario:',
            'rating': 'Valoración (opcional):'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe aquí lo que te gustó del tutorial...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = False
