from django.urls import path
from .views import profile_view

urlpatterns = [
    # Ruta para el perfil de cualquier usuario
    path('', profile_view, name='profile'),
    # Ruta específica para escritores (puedes redirigir ambos al mismo view o crear uno diferente)
    path('escritor_profile/', profile_view, name='escritor_profile'),
]
