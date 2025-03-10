from django.urls import path
from .views import BusquedaView

urlpatterns = [
    path('', BusquedaView.as_view(), name='busqueda'),
]
