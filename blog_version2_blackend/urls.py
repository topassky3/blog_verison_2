"""
URL configuration for blog_version2_blackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import confirmar_email
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inicio.urls')),
    path('tutoriales/', include('tutoriales.urls')),
    path('guias/', include('guias.urls')),
    path('podcast/', include('podcast.urls')),
    path('suscripcion/', include('suscripcion.urls')),
    path('contacto/', include('contacto.urls')),
    path('login/', include('login.urls')),
    path('registrarse/', include('registrarse.urls')),
    path('olvidar_contraseña/', include('olvidar_contraseña.urls')),
    path('accounts/', include('allauth.urls')),
    path('confirmar-email/<uidb64>/<token>/', confirmar_email, name='confirmar_email'),
    path('perfil/', include('perfil.urls')),
    path('crear_tutoriales/', include('crear_tutoriales.urls')),
    path('tutoriales/', include('leer_tutoriales.urls')),
    path('escuchar-podcast/', include('escuchar_podcast.urls')),
    path('crear_podcast/', include('crear_podcast.urls')),
    path('politica-de-privacidad/', include('politica_privacidad.urls')),
    path('terminos-de-servicio/', include('terminos.urls')),

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment/', include('payment.urls')),
    path('payment/', include('payment.urls')),
    path('buscar/', include('buscador.urls')),
    path('crear_guia/', include('crear_guia.urls')),
    path('leer_guias/', include('leer_guias.urls')),
    path('newsletter/', include('newsletter.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
