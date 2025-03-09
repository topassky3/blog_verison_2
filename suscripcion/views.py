from django.views.generic import TemplateView
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from core.models import Subscription
from paypal.standard.forms import PayPalPaymentsForm



class SuscripcionView(TemplateView):
    template_name = "suscripcion/suscripcion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                subscription = Subscription.objects.get(user=self.request.user)
                context['subscription'] = subscription
            except Subscription.DoesNotExist:
                context['subscription'] = None
        else:
            context['subscription'] = None
        return context

def paypal_payment(request, plan):
    """
    Vista que genera el formulario de pago para el plan seleccionado.
    """
    # Definir los datos de pago según el plan seleccionado
    if plan.lower() == "premium":
        amount = "9.99"
        item_name = "Suscripción Premium"
    elif plan.lower() == "anual":
        amount = "99.00"
        item_name = "Suscripción Anual"
    else:
        # Si se llega a este caso, el plan Básico no requiere pago
        amount = "0.00"
        item_name = "Suscripción Básica"

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": amount,
        "item_name": item_name,
        "invoice": f"{request.user.id}-{plan}",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment_done')),
        "cancel_return": request.build_absolute_uri(reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "payment/process_payment.html", {"form": form, "plan": plan})


def payment_done(request):
    """
    Vista para indicar que el pago se realizó con éxito.
    """
    return render(request, "payment/payment_done.html")


def payment_cancelled(request):
    """
    Vista para indicar que el pago fue cancelado.
    """
    return render(request, "payment/payment_cancelled.html")
