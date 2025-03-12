from django.urls import path
from .views import CrearPodcartView, PodcastUpdateView, toggle_publish

app_name = 'crear_podcast'
urlpatterns = [
    path('', CrearPodcartView.as_view(), name='crear_podcart'),
    path('<int:pk>/edit/', PodcastUpdateView.as_view(), name='podcast_update'),
    path('toggle_publish/<int:pk>/', toggle_publish, name='toggle_publish'),
]
