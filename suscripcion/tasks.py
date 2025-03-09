import logging
from celery import shared_task
from django.utils import timezone
from core.models import Subscription

logger = logging.getLogger(__name__)

@shared_task
def revert_expired_subscriptions_task():
    now = timezone.now()
    expired_subs = Subscription.objects.filter(expiration_date__lt=now).exclude(plan="Básico")
    logger.info(f"Se encontraron {expired_subs.count()} suscripciones expiradas.")
    for sub in expired_subs:
        logger.info(f"Revirtiendo la suscripción del usuario {sub.user.id} con expiración {sub.expiration_date}.")
        sub.plan = "Básico"
        sub.expiration_date = None
        sub.save()
        logger.info(f"La suscripción del usuario {sub.user.id} ha sido revertida a Básico.")
