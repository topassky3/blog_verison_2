from django import forms

class ContactForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100, required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)
    asunto = forms.CharField(label="Asunto", max_length=200, required=True)
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea, required=True)
