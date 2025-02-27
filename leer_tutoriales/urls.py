from django.urls import path
from .views import VerTutorialesView

urlpatterns = [
    path('ver_tutoriales/', VerTutorialesView.as_view(), name='ver_tutoriales'),
]
