from django.urls import path
from .views import VerTutorialesView, TutorialDetailView

urlpatterns = [
    path('ver_tutoriales/', VerTutorialesView.as_view(), name='ver_tutoriales'),
    path('<int:pk>/', TutorialDetailView.as_view(), name='tutorial_detail'),
]
