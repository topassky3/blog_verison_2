from django import forms
from core.models import PodcastComment

class PodcastCommentForm(forms.ModelForm):
    class Meta:
        model = PodcastComment
        fields = ['content', 'rating']
        labels = {
            'content': 'Deja tu comentario:',
            'rating': 'Valoración (opcional):'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe lo que te gustó del podcast...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = False
