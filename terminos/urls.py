from django.urls import path
from .views import TerminosView

urlpatterns = [
    path('', TerminosView.as_view(), name='terminos'),
]
