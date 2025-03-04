from django.urls import path
from .views import PodcastDetailView

urlpatterns = [
    path('<int:pk>/', PodcastDetailView.as_view(), name='escuchar_podcast'),
]
