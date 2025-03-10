from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages  # Importa el framework de mensajes
from .forms import ContactForm
from core.models import Contacto  # Información de contacto del admin

class ContactoView(FormView):
    template_name = "contacto/contacto.html"
    form_class = ContactForm
    success_url = reverse_lazy('contacto_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacto'] = Contacto.objects.first()
        return context

    def form_valid(self, form):
        nombre = form.cleaned_data.get('nombre')
        email = form.cleaned_data.get('email')
        asunto = form.cleaned_data.get('asunto')
        mensaje = form.cleaned_data.get('mensaje')
        full_message = f"De: {nombre}\nEmail: {email}\n\n{mensaje}"

        send_mail(
            subject=asunto,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        # Agrega el mensaje de éxito
        messages.success(self.request, "¡Mensaje enviado exitosamente!")
        return super().form_valid(form)
