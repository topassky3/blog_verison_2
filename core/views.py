from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from core.models import Lector

class CoreTemplateView(TemplateView):
    template_name = "core/core.html"

def confirmar_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Lector.objects.get(pk=uid)
    except (Lector.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_confirmado = True
        user.save()
        return render(request, "emails/confirmacion_exitosa.html", {"user": user})
    else:
        return render(request, "emails/confirmacion_fallida.html")
