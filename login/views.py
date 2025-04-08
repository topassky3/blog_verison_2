# login/views.py
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
import requests
from allauth.socialaccount.models import SocialToken

from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'login/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('inicio_home')

    def get_success_url(self):
        return reverse_lazy('inicio_home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        context = self.get_context_data(form=form)
        context['alert_message'] = "Inicio de sesión exitoso. Presiona Aceptar para continuar."
        context['redirect_url'] = self.get_success_url()
        return self.render_to_response(context)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        error_list = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_list.append(f"{', '.join(errors)}")
            else:
                error_list.append(f"{field}: {', '.join(errors)}")
        error_text = " ".join(error_list)
        context['alert_message'] = f"Error en el inicio de sesión. {error_text}"
        context['redirect_url'] = self.request.path
        return self.render_to_response(context)


from django.contrib.auth.views import LogoutView
import requests
from allauth.socialaccount.models import SocialToken
from django.conf import settings


class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Revocar el token de Google (si existe)
            try:
                token_obj = SocialToken.objects.get(account__user=request.user, account__provider='google')
                token = token_obj.token
                revoke_url = "https://accounts.google.com/o/oauth2/revoke"
                requests.get(revoke_url, params={'token': token})
            except SocialToken.DoesNotExist:
                pass  # No existe token de Google

            # Revocar el token de GitHub (si existe)
            try:
                github_token_obj = SocialToken.objects.get(account__user=request.user, account__provider='github')
                token = github_token_obj.token

                # Obtén client_id y client_secret de tu configuración
                client_id = settings.SOCIALACCOUNT_PROVIDERS.get('github', {}).get('APP', {}).get('client_id')
                client_secret = settings.SOCIALACCOUNT_PROVIDERS.get('github', {}).get('APP', {}).get('secret')

                if client_id and client_secret:
                    revoke_url = f"https://api.github.com/applications/{client_id}/token"
                    # Para revocar el token, se usa el método DELETE con autenticación básica
                    response = requests.delete(
                        revoke_url,
                        auth=(client_id, client_secret),
                        json={'access_token': token}
                    )
                    # Opcional: puedes verificar que la revocación fue exitosa
                    response.raise_for_status()
            except SocialToken.DoesNotExist:
                pass  # No existe token de GitHub
            except Exception as e:
                # Puedes loguear o gestionar el error según lo requieras
                print("Error al revocar el token de GitHub:", e)

        return super().dispatch(request, *args, **kwargs)
