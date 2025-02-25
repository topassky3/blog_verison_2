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
]

