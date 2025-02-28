from django.urls import path
from .views import TutorialesView, TutorialDetailView

urlpatterns = [
    path('', TutorialesView.as_view(), name='tutoriales_home'),
    path('tutorial/<int:pk>/', TutorialDetailView.as_view(), name='tutorial_detail'),
]
