from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from core.models import Subscriber
from .forms import SubscriberForm

class SubscribeView(CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'newsletter/subscribe.html'
    success_url = reverse_lazy('newsletter:subscribe_success')

class SubscribeSuccessView(TemplateView):
    template_name = 'newsletter/subscribe_success.html'
