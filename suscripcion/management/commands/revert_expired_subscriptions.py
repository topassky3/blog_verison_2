# suscripcion/management/commands/revert_expired_subscriptions.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Subscription

class Command(BaseCommand):
    help = "Revierte las suscripciones vencidas al plan Básico."

    def handle(self, *args, **options):
        now = timezone.now()
        # Selecciona suscripciones que hayan vencido y no estén ya en 'Básico'
        expired_subs = Subscription.objects.filter(
            expiration_date__lt=now,
        ).exclude(plan="Básico")

        for sub in expired_subs:
            sub.plan = "Básico"
            sub.expiration_date = None
            sub.save()
            self.stdout.write(
                self.style.SUCCESS(f"La suscripción de {sub.user.username} se ha revertido a Básico.")
            )
