from django.urls import path
from .views import TutorialesView

urlpatterns = [
    path('', TutorialesView.as_view(), name='tutoriales_home'),
]
