# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        # Asegúrate de que estos nombres coincidan con los definidos en las vistas principales de cada app.
        return [
            'inicio_home',       # Vista principal de la app "inicio"
            'tutoriales_home',   # Vista principal de la app "tutoriales" (o la que tenga la URL principal)
            'guias_home',        # Vista principal de la app "guias"
            'podcast_home',      # Vista principal de la app "podcast"
            'suscripcion_home',  # Vista principal de la app "suscripcion"
            'contacto_home',     # Vista principal de la app "contacto"
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Fecha de última modificación (en este ejemplo, 16 mar 2025)
        return datetime(2025, 3, 16)
