from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm


def paypal_payment(request, plan):
    """
    Vista que genera el formulario de pago para el plan seleccionado.
    """
    # Configura los datos de pago según el plan
    if plan.lower() == "premium":
        amount = "9.99"
        item_name = "Suscripción Premium"
    elif plan.lower() == "anual":
        amount = "99.00"
        item_name = "Suscripción Anual"
    else:
        # En caso de que se invoque algún plan que no requiera pago (p.ej. Básico)
        amount = "0.00"
        item_name = "Suscripción Básica"

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,  # Define esto en settings.py
        "amount": amount,
        "item_name": item_name,
        "invoice": f"{request.user.id}-{plan}",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment:payment_done')),
        "cancel_return": request.build_absolute_uri(reverse('payment:payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "payment/process_payment.html", {"form": form, "plan": plan})


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
