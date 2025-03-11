from django.urls import path
from .views import GuiaCreateView, GuiaUpdateView, GuiaDeleteView, toggle_publish

urlpatterns = [
    path('crear/', GuiaCreateView.as_view(), name='guia_create'),
    path('editar/<int:pk>/', GuiaUpdateView.as_view(), name='guia_update'),
    path('eliminar/<int:pk>/', GuiaDeleteView.as_view(), name='guia_delete'),
    path('toggle_publish/<int:pk>/', toggle_publish, name='toggle_publish'),
]
