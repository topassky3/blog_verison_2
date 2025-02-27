from django.urls import path
from .views import TutorialCreateTemplateView

urlpatterns = [
    path('crear/', TutorialCreateTemplateView.as_view(), name='tutorial_create'),
]
