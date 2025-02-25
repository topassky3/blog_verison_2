from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings


def generar_token_confirmacion(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def enviar_correo_confirmacion(request, user):
    uid, token = generar_token_confirmacion(user)
    dominio = get_current_site(request).domain
    # Construimos la URL de confirmación (asegúrate de que la ruta exista en urls.py)
    url_confirmacion = f"http://{dominio}/confirmar-email/{uid}/{token}/"

    subject = "Confirma tu correo electrónico"
    message = render_to_string("emails/confirmacion_email.html", {
        "user": user,
        "url_confirmacion": url_confirmacion
    })

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # o DEFAULT_FROM_EMAIL
        [user.email],
        fail_silently=False,
    )
