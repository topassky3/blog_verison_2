from django.urls import path
from .views import (
    PodcastDetailView,
    toggle_podcast_comment_like,
    toggle_podcast_comment_dislike,
    delete_podcast_comment
)

urlpatterns = [
    path('<int:pk>/', PodcastDetailView.as_view(), name='escuchar_podcast'),
    path('toggle_comment_like/', toggle_podcast_comment_like, name='toggle_podcast_comment_like'),
    path('toggle_comment_dislike/', toggle_podcast_comment_dislike, name='toggle_podcast_comment_dislike'),
    path('delete_comment/', delete_podcast_comment, name='delete_podcast_comment'),
]
