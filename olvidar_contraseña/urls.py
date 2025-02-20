from django.urls import path
from .views import OlvidarContraseñaView

urlpatterns = [
    path('', OlvidarContraseñaView.as_view(), name='password_reset'),
]
