# registrarse/views.py
from django.views.generic import CreateView
from registrarse.forms import LectorCreationForm


class RegistrarseView(CreateView):
    form_class = LectorCreationForm
    template_name = "registrarse/registrarse.html"

    def form_valid(self, form):
        self.object = form.save()
        context = self.get_context_data(form=form)
        context['alert_message'] = "Registro exitoso. Ahora puedes iniciar sesión."
        context['redirect_url'] = "/login"  # URL a la que se redirige en caso de éxito
        return self.render_to_response(context)

    def form_invalid(self, form):
        # Mapeo de nombres de campos a etiquetas en español
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
