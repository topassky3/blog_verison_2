# registrarse/views.py

from django.views.generic import CreateView
from registrarse.forms import LectorCreationForm

class RegistrarseView(CreateView):
    form_class = LectorCreationForm
    template_name = "registrarse/registrarse.html"

    def form_valid(self, form):
        # Se guarda el usuario
        self.object = form.save()
        # Preparamos el contexto para el mensaje de éxito
        context = self.get_context_data(form=form)
        context['alert_message'] = "Registro exitoso. Ahora puedes iniciar sesión."
        context['redirect_url'] = "/login"  # Aquí pones la URL de inicio
        return self.render_to_response(context)

    def form_invalid(self, form):
        # Preparamos el contexto para el mensaje de error
        context = self.get_context_data(form=form)
        context['alert_message'] = "Hubo un error durante el registro. Por favor, revisa la información e inténtalo de nuevo."
        context['redirect_url'] = "/registrarse/"  # O la URL que desees para volver a intentar
        return self.render_to_response(context)
