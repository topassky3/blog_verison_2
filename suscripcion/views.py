from django.views.generic import TemplateView
from core.models import Subscription


class SuscripcionView(TemplateView):
    template_name = "suscripcion/suscripcion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context['subscription'] = Subscription.objects.get(user=self.request.user)
            except Subscription.DoesNotExist:
                context['subscription'] = None
        else:
            context['subscription'] = None
        return context
