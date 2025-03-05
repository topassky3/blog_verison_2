from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField("Slug", unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría tutorial"
        verbose_name_plural = "Categorías tutoriales"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Genera el slug automáticamente si no se ha definido
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )
    image = models.ImageField("Imagen Representativa", upload_to='tutorial_images/', null=True, blank=True)
    publicado = models.BooleanField("Publicado", default=False)
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

class Comment(models.Model):
    tutorial = models.ForeignKey(
        'Tutorial',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField("Contenido")
    rating = models.PositiveSmallIntegerField(
        "Valoración",
        choices=[(i, i) for i in range(1, 6)],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_comments',
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Comentario de {self.author} en {self.tutorial}"

from django.db import models
from django.utils.text import slugify

class PodcastCategory(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField("Slug", unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría de Podcast"
        verbose_name_plural = "Categorías de Podcast"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


from django.conf import settings
from django.db import models

class Podcast(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='podcasts',
        verbose_name="Autor"
    )
    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descripción")
    audio = models.FileField("Archivo de Audio", upload_to='podcast_audio/')
    cover = models.ImageField("Portada", upload_to='podcast_covers/', blank=True, null=True)
    category = models.ForeignKey(
        PodcastCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    def __str__(self):
        return self.title

from django.conf import settings
from django.db import models

class PodcastComment(models.Model):
    podcast = models.ForeignKey(
        'Podcast',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Podcast"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='podcast_comments',
        verbose_name="Autor"
    )
    content = models.TextField("Contenido")
    rating = models.PositiveSmallIntegerField(
        "Valoración",
        choices=[(i, i) for i in range(1, 6)],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_podcast_comments',
        blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_podcast_comments',
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Comentario de {self.author} en {self.podcast}"
