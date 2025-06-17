from django.urls import path
from .views import GuiaDetailView, DownloadGuiaCodeFileView, load_all_guia_blocks
from . import views

urlpatterns = [
    path('guia/<int:pk>/', GuiaDetailView.as_view(), name='guia_detail'),
    path('download_code/<int:pk>/', DownloadGuiaCodeFileView.as_view(), name='download_guia_code_file'),

    path('guia/<int:guia_id>/load_all_blocks/', load_all_guia_blocks, name='load_all_guia_blocks'),

    # Rutas AJAX para likes, dislikes, borrar, etc.
    path('toggle_comment_like/', views.toggle_guia_comment_like, name='toggle_guia_comment_like'),
    path('toggle_comment_dislike/', views.toggle_guia_comment_dislike, name='toggle_guia_comment_dislike'),
    path('delete_comment/', views.delete_guia_comment, name='delete_guia_comment'),
]
