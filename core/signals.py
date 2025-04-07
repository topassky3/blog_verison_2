from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from core.models import Comment, GuiaComment

@receiver(post_save, sender=Comment)
def notify_tutorial_author(sender, instance, created, **kwargs):
    # Solo enviar la notificación si se creó el comentario (no en las actualizaciones)
    if created:
        tutorial = instance.tutorial
        writer = tutorial.author
        if writer.email:
            subject = f"Nuevo comentario en tu tutorial: {tutorial.title}"
            # Preparamos el contexto para la plantilla
            context = {
                'writer': writer,
                'tutorial': tutorial,
                'comment': instance,
                # Asegúrate de ajustar la URL base según tu dominio o usar request.build_absolute_uri si está disponible
                'url_tutorial': f"https://tucodigocotidiano.yarumaltech.com/leer_tutoriales/{tutorial.pk}/#comments",
            }
            # Renderizamos la plantilla HTML
            html_content = render_to_string("emails/new_comment_notification.html", context)
            # Generamos una versión de texto plano a partir del HTML
            text_content = strip_tags(html_content)
            # Creamos y enviamos el correo con ambas alternativas
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [writer.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()


@receiver(post_save, sender=GuiaComment)
def notify_guia_author(sender, instance, created, **kwargs):
    # Se envía la notificación solo si se creó el comentario (no en actualizaciones)
    if created:
        guia = instance.guia
        writer = guia.author
        if writer.email:
            subject = f"Nuevo comentario en tu guía: {guia.title}"
            # Preparamos el contexto para la plantilla
            context = {
                'writer': writer,
                'guia': guia,
                'comment': instance,
                # Ajusta la URL base a tu dominio o usa métodos para generar la URL completa
                'url_guia': f"https://tucodigocotidiano.yarumaltech.com/leer_guias/guia/{guia.pk}/#comments",
            }
            # Renderizamos la plantilla HTML
            html_content = render_to_string("emails/new_guia_comment_notification.html", context)
            # Generamos una versión en texto plano a partir del HTML
            text_content = strip_tags(html_content)
            # Creamos y enviamos el correo con ambas alternativas
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [writer.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from core.models import PodcastComment  # Asegúrate de que PodcastComment esté importado

@receiver(post_save, sender=PodcastComment)
def notify_podcast_author(sender, instance, created, **kwargs):
    # Enviar la notificación solo si se crea el comentario
    if created:
        podcast = instance.podcast
        writer = podcast.author
        if writer.email:
            subject = f"Nuevo comentario en tu podcast: {podcast.title}"
            # Preparamos el contexto para la plantilla
            context = {
                'writer': writer,
                'podcast': podcast,
                'comment': instance,
                # Ajusta la URL base a tu dominio o usa un método para generar la URL completa
                'url_podcast': f"https://tucodigocotidiano.yarumaltech.com/escuchar-podcast/{podcast.pk}/#comments",
            }
            # Renderizamos la plantilla HTML
            html_content = render_to_string("emails/new_podcast_comment_notification.html", context)
            # Generamos una versión en texto plano a partir del HTML
            text_content = strip_tags(html_content)
            # Creamos y enviamos el correo con ambas alternativas
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [writer.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
