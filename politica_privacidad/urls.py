from django.urls import path
from .views import PoliticaPrivacidadView

urlpatterns = [
    path('', PoliticaPrivacidadView.as_view(), name='mostrar_politica'),
]
