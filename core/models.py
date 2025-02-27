from django.contrib.auth.models import AbstractUser
from django.db import models

class Lector(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_confirmado = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)  # Campo para la biografía
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )  # Campo opcional para la imagen de perfil

    class Meta:
        verbose_name = 'Lector'
        verbose_name_plural = 'Lectores'

    @property
    def es_escritor(self):
        """Retorna True si el usuario pertenece al grupo 'Escritor'."""
        return self.groups.filter(name="Escritor").exists()
