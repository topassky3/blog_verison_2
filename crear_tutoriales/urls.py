from django.urls import path
from .views import TutorialCreateView, TutorialUpdateView, TutorialDeleteView, toggle_publish

urlpatterns = [
    path('crear/', TutorialCreateView.as_view(), name='tutorial_create'),
    path('editar/<int:pk>/', TutorialUpdateView.as_view(), name='tutorial_update'),
    path('eliminar/<int:pk>/', TutorialDeleteView.as_view(), name='tutorial_delete'),
    path('toggle_publish/<int:pk>/', toggle_publish, name='toggle_publish'),
]
