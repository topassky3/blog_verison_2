from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
import uuid

@csrf_exempt
def paypal_payment(request, plan):
    """
    Vista que genera el formulario de pago para el plan seleccionado.
    """
    if plan.lower() == "premium":
        amount = "9.99"
        item_name = "Suscripción Premium"
    elif plan.lower() == "anual":
        amount = "99.00"
        item_name = "Suscripción Anual"
    else:
        amount = "0.00"
        item_name = "Suscripción Básica"

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": amount,
        "item_name": item_name,
        # Ahora el invoice tendrá tres partes: user_id, plan y un UUID único
        "invoice": f"{request.user.id}-{plan}-{uuid.uuid4()}",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment:payment_done')),
        "cancel_return": request.build_absolute_uri(reverse('payment:payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    if settings.PAYPAL_TEST:
        endpoint = "https://www.sandbox.paypal.com/cgi-bin/webscr"
    else:
        endpoint = "https://www.paypal.com/cgi-bin/webscr"

    return render(request, "payment/process_payment.html", {"form": form, "plan": plan, "endpoint": endpoint})
def payment_done(request):
    """
    Vista que se muestra cuando el pago se realiza con éxito.
    """
    return render(request, "payment/payment_done.html")


def payment_cancelled(request):
    """
    Vista que se muestra cuando el usuario cancela el pago.
    """
    return render(request, "payment/payment_cancelled.html")
