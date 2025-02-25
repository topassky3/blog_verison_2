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

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                # Si el usuario tiene autenticación social con Google, revocamos el token
                token_obj = SocialToken.objects.get(account__user=request.user, account__provider='google')
                token = token_obj.token
                revoke_url = "https://accounts.google.com/o/oauth2/revoke"
                requests.get(revoke_url, params={'token': token})
            except SocialToken.DoesNotExist:
                pass  # Continúa si no existe el token
        return super().dispatch(request, *args, **kwargs)
