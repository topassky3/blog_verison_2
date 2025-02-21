# registrarse/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import Lector

class LectorCreationForm(UserCreationForm):
    fullname = forms.CharField(label="Nombre Completo", required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)

    class Meta:
        model = Lector
        # Definimos los campos que se mostrarán en el formulario.
        fields = ("fullname", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificamos si ya existe un usuario con ese email
        if Lector.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        # Guardamos la instancia del usuario sin confirmar (commit=False)
        user = super().save(commit=False)
        fullname = self.cleaned_data.get("fullname")
        if fullname:
            nombres = fullname.split(" ", 1)
            user.first_name = nombres[0]
            user.last_name = nombres[1] if len(nombres) > 1 else ""
        user.email = self.cleaned_data.get("email")
        # Usamos el email como username para garantizar que sea único
        user.username = user.email
        if commit:
            user.save()
        return user
