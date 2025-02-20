from django.urls import path
from .views import CoreTemplateView

urlpatterns = [
    path('', CoreTemplateView.as_view(), name='core_home'),
]
