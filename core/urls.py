from django.urls import path
from core.views import confirmar_email

urlpatterns = [
    # Otras rutas...
    path('confirmar-email/<uidb64>/<token>/', confirmar_email, name='confirmar_email'),
]
