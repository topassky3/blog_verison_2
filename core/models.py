from django.contrib.auth.models import AbstractUser
from django.conf import settings
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

class Tutorial(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutorials',
        verbose_name="Autor"
    )
    title = models.CharField("Título", max_length=200)
    duration = models.CharField("Duración", max_length=50, blank=True, null=True)
    level = models.CharField("Nivel", max_length=50, blank=True, null=True)
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    def __str__(self):
        return self.title

class TutorialBlock(models.Model):
    BLOCK_TYPES = (
        ('text', 'Texto'),
        ('latex', 'LaTeX'),
        ('code', 'Código'),
    )
    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, related_name='blocks'
    )
    block_type = models.CharField("Tipo de Bloque", max_length=10, choices=BLOCK_TYPES)
    content = models.TextField("Contenido")
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_block_type_display()} - Orden: {self.order}"
