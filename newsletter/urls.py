from django.urls import path
from .views import SubscribeView, SubscribeSuccessView

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('subscribe/success/', SubscribeSuccessView.as_view(), name='subscribe_success'),
]
