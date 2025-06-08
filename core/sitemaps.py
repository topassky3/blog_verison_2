# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime
from .models import Guia, Tutorial, Podcast  # Importa los modelos necesarios

# --- SITEMAPS PARA CONTENIDO DINÁMICO ---

class GuiaSitemap(Sitemap):
    """Sitemap para todas las Guías publicadas."""
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Guia.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # CORRECTO: Coincide con name='guia_detail' de guias/urls.py
        return reverse('guia_detail', kwargs={'pk': obj.pk})

class TutorialSitemap(Sitemap):
    """Sitemap para todos los Tutoriales publicados."""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Tutorial.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # CORRECTO: Coincide con name='tutorial_detail' de tutoriales/urls.py
        return reverse('tutorial_detail', kwargs={'pk': obj.pk})

class PodcastSitemap(Sitemap):
    """Sitemap para todos los Podcasts publicados."""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Podcast.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # CORREGIDO: Ahora usa 'escuchar_podcast' que coincide con el name de podcast/urls.py
        return reverse('escuchar_podcast', kwargs={'pk': obj.pk})


# --- SITEMAP PARA PÁGINAS ESTÁTICAS (YA LO TENÍAS) ---

class StaticViewSitemap(Sitemap):
    """Sitemap para las páginas estáticas principales."""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return [
            'inicio_home', 'tutoriales_home', 'guias_home',
            'podcast_home', 'suscripcion_home', 'contacto_home',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return datetime.now()