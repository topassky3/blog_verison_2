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


# core/views.py

from django.http import HttpResponse, Http404
from .storage import GridFSStorage

def serve_media(request, filename):
    storage = GridFSStorage()
    if not storage.exists(filename):
        raise Http404("Archivo no encontrado")
    file_obj = storage._open(filename)
    # Puedes ajustar content_type según el tipo de archivo; aquí se usa un valor genérico.
    return HttpResponse(file_obj.read(), content_type="application/octet-stream")

