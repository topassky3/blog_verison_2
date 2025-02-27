from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe una breve biografía...'}),
        }
