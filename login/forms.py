# login/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from core.models import Lector  # Asegúrate de importar tu modelo

class CustomAuthenticationForm(AuthenticationForm):
    fake_recaptcha = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes marcar el captcha.'}
    )

    def confirm_login_allowed(self, user):
        # Llama a la validación original (por ejemplo, para usuarios inactivos)
        super().confirm_login_allowed(user)

        # Si el usuario no tiene el atributo email_confirmado, intentar obtener la instancia Lector
        if not hasattr(user, 'email_confirmado'):
            try:
                user = Lector.objects.get(pk=user.pk)
            except Lector.DoesNotExist:
                raise forms.ValidationError(
                    "Debes confirmar tu correo electrónico antes de iniciar sesión.",
                    code='email_not_confirmed'
                )

        # Ahora se verifica que el correo esté confirmado
        if not user.email_confirmado:
            raise forms.ValidationError(
                "Debes confirmar tu correo electrónico antes de iniciar sesión.",
                code='email_not_confirmed'
            )
