from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    fake_recaptcha = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes marcar el captcha.'}
    )
