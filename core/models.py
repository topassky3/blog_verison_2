# core/models.py

from django.contrib.auth.models import User
from django.db import models

class Lector(User):
    # Agrega campos adicionales si lo requieres, por ejemplo:
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Lector'
        verbose_name_plural = 'Lectores'
