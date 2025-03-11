# leer_guias/urls.py
from django.urls import path
from .views import GuiaDetailView
from . import views

urlpatterns = [
    path('guia/<int:pk>/', GuiaDetailView.as_view(), name='guia_detail'),

    # Rutas AJAX para likes, dislikes, borrar, etc. (ver siguiente sección)
    path('toggle_comment_like/', views.toggle_guia_comment_like, name='toggle_guia_comment_like'),
    path('toggle_comment_dislike/', views.toggle_guia_comment_dislike, name='toggle_guia_comment_dislike'),
    path('delete_comment/', views.delete_guia_comment, name='delete_guia_comment'),
]
