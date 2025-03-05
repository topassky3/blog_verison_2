from django import forms
from core.models import Podcast

class PodcastForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = ['title', 'description', 'audio', 'cover', 'category']
