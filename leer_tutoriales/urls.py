from django.urls import path
from .views import VerTutorialesView, TutorialDetailView, toggle_comment_like, toggle_comment_dislike, delete_comment, DownloadCodeFileView

urlpatterns = [
    path('ver_tutoriales/', VerTutorialesView.as_view(), name='ver_tutoriales'),
    path('<int:pk>/', TutorialDetailView.as_view(), name='tutorial_detail'),
    path('toggle_comment_like/', toggle_comment_like, name='toggle_comment_like'),
    path('toggle_comment_dislike/', toggle_comment_dislike, name='toggle_comment_dislike'),
    path('delete_comment/', delete_comment, name='delete_comment'),
    path('descargar_codigo/<int:pk>/', DownloadCodeFileView.as_view(), name='download_code_file'),
]
