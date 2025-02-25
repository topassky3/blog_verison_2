from django.views.generic import CreateView
from registrarse.forms import LectorCreationForm
from core.utils import enviar_correo_confirmacion  # Asegúrate de importar la función

class RegistrarseView(CreateView):
    form_class = LectorCreationForm
    template_name = "registrarse/registrarse.html"

    def form_valid(self, form):
        self.object = form.save()
        # Enviar correo de confirmación al usuario recién registrado
        enviar_correo_confirmacion(self.request, self.object)
        context = self.get_context_data(form=form)
        context['alert_message'] = (
            "Registro exitoso. Se ha enviado un correo de confirmación a tu dirección. "
            "Revisa tu bandeja de entrada y sigue las instrucciones para confirmar tu email."
        )
        context['redirect_url'] = "/login"  # URL a la que se redirige luego de aceptar el mensaje
        return self.render_to_response(context)

    def form_invalid(self, form):
        field_labels = {
            "fullname": "Nombre Completo",
            "email": "Correo Electrónico",
            "password1": "Contraseña",
            "password2": "Confirmar Contraseña",
            "__all__": ""
        }
        error_list = []
        for field, errors in form.errors.items():
            label = field_labels.get(field, field)
            for error in errors:
                if label:
                    error_list.append(f"{label}: {error}")
                else:
                    error_list.append(f"{error}")
        error_message = "Se encontraron los siguientes errores:\n" + "\n".join(error_list)

        context = self.get_context_data(form=form)
        context['alert_message'] = error_message
        context['redirect_url'] = "/registrarse/"  # Redirige de nuevo a la página de registro en caso de error
        return self.render_to_response(context)
