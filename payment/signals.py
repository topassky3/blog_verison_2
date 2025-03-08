import logging
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from core.models import Subscription
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    logger.info("IPN recibido: %s", ipn_obj)
    if ipn_obj.payment_status == "Completed":
        try:
            # Se espera que el invoice tenga el formato: "{user_id}-{plan}-{uuid}"
            parts = ipn_obj.invoice.split('-')
            if len(parts) < 3:
                logger.error("Invoice con formato incorrecto: %s", ipn_obj.invoice)
                return
            user_id, plan = parts[0], parts[1]
            logger.info("Invoice parseado: user_id=%s, plan=%s", user_id, plan)
            subscription = Subscription.objects.get(user__id=user_id)
            # Actualiza el plan y establece la fecha de expiración según el plan
            subscription.plan = plan.capitalize()  # Ejemplo: "Premium" o "Anual"
            now = timezone.now()
            if plan.lower() == "premium":
                subscription.expiration_date = now + timedelta(days=30)
            elif plan.lower() == "anual":
                subscription.expiration_date = now + timedelta(days=365)
            subscription.save()
            logger.info("Suscripción actualizada: %s", subscription)
        except Exception as e:
            logger.error("Error al actualizar la suscripción: %s", e)
