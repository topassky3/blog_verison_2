from django.contrib.auth.models import User
from django.db import models


class Lector(User):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_confirmado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Lector'
        verbose_name_plural = 'Lectores'

    @property
    def es_escritor(self):
        """Retorna True si el usuario pertenece al grupo 'Escritor'."""
        return self.groups.filter(name="Escritor").exists()
