from django.urls import path
from .views import GuiaCreateView, GuiaUpdateView

urlpatterns = [
    path('crear/', GuiaCreateView.as_view(), name='guia_create'),
    path('editar/<int:pk>/', GuiaUpdateView.as_view(), name='guia_update'),
]
