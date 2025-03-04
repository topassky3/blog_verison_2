from django.urls import path
from .views import CrearPodcartView

urlpatterns = [
    path('', CrearPodcartView.as_view(), name='crear_podcart'),
]
