# leer_guias/urls.py

from django.urls import path
from .views import GuiaDetailView

urlpatterns = [
    path('guia/<int:pk>/', GuiaDetailView.as_view(), name='guia_detail'),
]
