import uuid
from django.urls import reverse
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
@csrf_exempt
def paypal_payment(request, plan):
    """
    Vista que genera el formulario de pago para el plan seleccionado.
    """
    # Guarda el plan que se intenta pagar en la sesión
    request.session['pending_subscription_plan'] = plan.lower()

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
        # Incluimos un UUID para garantizar que el invoice sea único
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


from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from core.models import Subscription

def payment_done(request):
    """
    Vista que se muestra cuando el pago se realiza con éxito.
    Actualiza la suscripción según el plan que se guardó en sesión.
    Para pruebas, asigna 1 minuto para 'Premium' y 2 minutos para 'Anual'.
    """
    # Recupera el plan pendiente y elimínalo de la sesión
    plan = request.session.pop('pending_subscription_plan', None)

    if plan and request.user.is_authenticated:
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.plan = plan.capitalize()  # "Premium" o "Anual"
            now = timezone.now()
            # Para pruebas, usamos minutos en lugar de días
            if plan == "premium":
                subscription.expiration_date = now + timedelta(days=30)
            elif plan == "anual":
                subscription.expiration_date = now + timedelta(days=365)
            subscription.save()
        except Subscription.DoesNotExist:
            # Si no existe, podrías crearla o loguear el error
            pass

    return render(request, "payment/payment_done.html")

def payment_cancelled(request):
    """
    Vista que se muestra cuando el usuario cancela el pago.
    """
    return render(request, "payment/payment_cancelled.html")
