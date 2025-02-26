from django.urls import path
from .views import profile_view

urlpatterns = [
    # Otras rutas...
    path('', profile_view, name='profile'),
]
