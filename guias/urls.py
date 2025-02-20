from django.urls import path
from .views import GuiasView

urlpatterns = [
    path('', GuiasView.as_view(), name='guias_home'),
]
