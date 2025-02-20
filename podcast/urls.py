from django.urls import path
from .views import PodcastView

urlpatterns = [
    path('', PodcastView.as_view(), name='podcast_home'),
]
