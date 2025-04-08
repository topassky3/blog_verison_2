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

from allauth.socialaccount.models import SocialToken, SocialApp
import requests
import json
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # -----------------------------
            # 1) Revocar token de Google
            # -----------------------------
            try:
                token_obj = SocialToken.objects.get(
                    account__user=request.user,
                    account__provider='google'
                )
                token = token_obj.token
                revoke_url = "https://accounts.google.com/o/oauth2/revoke"
                requests.get(revoke_url, params={'token': token})
            except SocialToken.DoesNotExist:
                pass

            # -----------------------------
            # 2) Revocar token de GitHub
            # -----------------------------
            try:
                # 2.1) Obtener el token del usuario
                github_token_obj = SocialToken.objects.get(
                    account__user=request.user,
                    account__provider='github'
                )
                github_token = github_token_obj.token

                # 2.2) Obtener las credenciales (client_id y secret)
                github_app = SocialApp.objects.get(provider='github')
                client_id = github_app.client_id
                client_secret = github_app.secret

                # 2.3) Construir la URL para revocar
                url = f"https://api.github.com/applications/{client_id}/token"

                # 2.4) Hacer la petición DELETE para revocar el token
                response = requests.delete(
                    url,
                    auth=(client_id, client_secret),
                    data=json.dumps({"access_token": github_token}),
                    headers={'Content-Type': 'application/json'}
                )
                # Opcional: Verificar si la revocación se efectuó con éxito
                # p.ej. if response.status_code == 204: ...
            except (SocialApp.DoesNotExist, SocialToken.DoesNotExist):
                pass

        return super().dispatch(request, *args, **kwargs)
