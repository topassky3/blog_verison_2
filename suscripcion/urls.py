from django.urls import path
from .views import SuscripcionView, IniciarPagoView, PaymentCallbackView

urlpatterns = [
    path('', SuscripcionView.as_view(), name='suscripcion_home'),
    path('pago/<str:plan>/', IniciarPagoView.as_view(), name='iniciar_pago'),
    path('auth/patreon/callback/', PaymentCallbackView.as_view(), name='patreon_callback'),
]
