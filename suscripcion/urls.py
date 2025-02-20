from django.urls import path
from .views import SuscripcionView

urlpatterns = [
    path('', SuscripcionView.as_view(), name='suscripcion_home'),
]
