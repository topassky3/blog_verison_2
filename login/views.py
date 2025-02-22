from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView


class CustomLoginView(LoginView):
    template_name = 'login/login.html'
    success_url = reverse_lazy('inicio_home')

    def get_success_url(self):
        # Forzamos que la URL de redirección sea la de inicio
        return reverse_lazy('inicio_home')

    def form_valid(self, form):
        # Autentica y loguea al usuario
        user = form.get_user()
        login(self.request, user)
        # Preparamos el contexto con el mensaje de alerta y la URL de redirección
        context = self.get_context_data(form=form)
        context['alert_message'] = "Inicio de sesión exitoso. Presiona Aceptar para continuar."
        context['redirect_url'] = self.get_success_url()
        return self.render_to_response(context)

    def form_invalid(self, form):
        # Si el formulario no es válido, preparamos un mensaje de alerta para informar del fallo
        context = self.get_context_data(form=form)

        # Recopilamos los errores de cada campo
        error_list = []
        for field, errors in form.errors.items():
            # Si el error es general (non_field_errors), field vendrá vacío
            if field == '__all__':
                error_list.append(f"{', '.join(errors)}")
            else:
                error_list.append(f"{field}: {', '.join(errors)}")
        error_text = " ".join(error_list)

        # Configuramos el mensaje de alerta
        context['alert_message'] = f"Error en el inicio de sesión. {error_text}"
        # Puedes definir una URL de redirección o dejar que el usuario lo corrija en el mismo formulario
        context['redirect_url'] = self.request.path  # redirige al mismo login para que se intente nuevamente
        return self.render_to_response(context)



class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']
