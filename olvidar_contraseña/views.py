# olvidar_contraseña/views.py
from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .utils import enviar_correo_reset

User = get_user_model()

class PasswordResetRequestView(View):
    template_name = "olvidar_contraseña/olvidar_contraseña.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        # Obtiene solo el primer usuario con ese email para evitar duplicados.
        user = User.objects.filter(email=email).first()
        if user:
            enviar_correo_reset(request, user)
            alert_message = "Se han enviado las instrucciones para recuperar tu contraseña a tu correo."
            # Por ejemplo, redirige a la página de login luego de aceptar la alerta.
            redirect_url = "/login/"
        else:
            alert_message = "No se encontró un usuario con ese correo."
            redirect_url = "/olvidar_contraseña/password-reset/"
        context = {
            "alert_message": alert_message,
            "redirect_url": redirect_url,
        }
        return render(request, self.template_name, context)


from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'emails/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        # Este método llama a form.save(), que internamente hace:
        # user.set_password(new_password) y user.save()
        form.save()
        return super().form_valid(form)
