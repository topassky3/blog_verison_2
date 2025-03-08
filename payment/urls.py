from django.urls import path
from .views import paypal_payment, payment_done, payment_cancelled

app_name = "payment"

urlpatterns = [
    path('paypal-payment/<str:plan>/', paypal_payment, name='paypal_payment'),
    path('payment-done/', payment_done, name='payment_done'),
    path('payment-cancelled/', payment_cancelled, name='payment_cancelled'),
]
