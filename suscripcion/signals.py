# suscripcion/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Lector  # Asegúrate de importar tu modelo de usuario
from core.models import Subscription

@receiver(post_save, sender=Lector)
def crear_suscripcion_basica(sender, instance, created, **kwargs):
    if created:
        # Se crea la suscripción con el plan por defecto "Básico"
        Subscription.objects.create(user=instance)
