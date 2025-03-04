from django.urls import path
from .views import CrearPodcartView, PodcastUpdateView

urlpatterns = [
    path('', CrearPodcartView.as_view(), name='crear_podcart'),
    path('<int:pk>/edit/', PodcastUpdateView.as_view(), name='podcast_update'),
]
