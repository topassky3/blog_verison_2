from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

def generar_token_reset(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def enviar_correo_reset(request, user):
    uid, token = generar_token_reset(user)
    domain = get_current_site(request).domain
    # Si tu app se encuentra bajo un prefijo, inclúyelo en el enlace:
    reset_url = f"http://{domain}/olvidar_contraseña/password-reset-confirm/{uid}/{token}/"

    subject = "Recupera tu contraseña"
    html_message = render_to_string("emails/password_reset_email.html", {
        "user": user,
        "reset_url": reset_url,
    })
    plain_message = (
        f"Hola {user.first_name},\n\n"
        f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n{reset_url}\n\n"
        "Si no solicitaste el cambio, ignora este mensaje."
    )
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )
