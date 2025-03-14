from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from core.models import Comment

@receiver(post_save, sender=Comment)
def notify_tutorial_author(sender, instance, created, **kwargs):
    # Se envía el correo solo si el comentario es nuevo
    if created:
        tutorial = instance.tutorial
        author = tutorial.author
        if author.email:
            subject = f"Nuevo comentario en tu tutorial: {tutorial.title}"
            # Puedes personalizar el mensaje según necesites e incluso incluir la URL del tutorial
            message = (
                f"Hola {author.get_full_name() or author.username},\n\n"
                "Has recibido un nuevo comentario en tu tutorial.\n"
                "Inicia sesión para verlo y responder si lo deseas.\n\n"
                "Saludos,\n"
                "Tu equipo de WebDev Blog"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [author.email])
