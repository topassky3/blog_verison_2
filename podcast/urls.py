from django.urls import path
from .views import PodcastListView

urlpatterns = [
    path('', PodcastListView.as_view(), name='podcast_home'),
]
