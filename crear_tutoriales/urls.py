from django.urls import path
from .views import TutorialCreateView, TutorialUpdateView

urlpatterns = [
    path('crear/', TutorialCreateView.as_view(), name='tutorial_create'),
    path('editar/<int:pk>/', TutorialUpdateView.as_view(), name='tutorial_update'),
]
