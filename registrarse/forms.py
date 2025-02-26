from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import Lector

class LectorCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", required=True)
    last_name = forms.CharField(label="Apellidos", required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)

    class Meta:
        model = Lector
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Lector.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        # Usamos el email como username para garantizar la unicidad
        user.username = user.email
        if commit:
            user.save()
        return user
