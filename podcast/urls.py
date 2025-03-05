from django.urls import path
from .views import PodcastListView, PodcastDeleteView

urlpatterns = [
    path('', PodcastListView.as_view(), name='podcast_home'),
    path('eliminar/<int:pk>/', PodcastDeleteView.as_view(), name='podcast_delete'),
]
