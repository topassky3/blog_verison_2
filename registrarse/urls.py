from django.urls import path
from .views import RegistrarseView

urlpatterns = [
    path('', RegistrarseView.as_view(), name='registrarse_home'),
]
