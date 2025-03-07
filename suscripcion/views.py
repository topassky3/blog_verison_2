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


import os
import requests
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from core.models import Subscription

# Obtén las credenciales desde variables de entorno o usa los valores por defecto
CLIENT_ID = os.environ.get("APTREON_CLIENT_ID", "g_WawYPEVgQ1p2j4H37rpLaLjhwZuR9okxqYSZ4fRrOpOT975PshTu_m5XZLc1j1")
CLIENT_SECRET = os.environ.get("APTREON_CLIENT_SECRET",
                               "aIwCYXgfX0AHIRQ0pxdZuE165bDTA5NuPdO2kByE_aJJLTSsTjga_xVwjfslwN5A")
# URL del endpoint de autorización OAuth de Patreon
OAUTH_AUTHORIZE_URL = "https://www.patreon.com/oauth2/authorize"


class IniciarPagoView(View):
    def get(self, request, plan):
        # Construir la URL de redirección (callback) que debe estar registrada en el panel de tu cliente
        callback_url = "https://tucodigocotidiano.yarumaltech.com/suscripcion/auth/patreon/callback"
        # Parámetros para el flujo OAuth
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": callback_url,
            "scope": "identity identity.memberships",  # Ajusta los scopes según tus necesidades
            "state": plan,  # Usamos el parámetro state para enviar la información del plan
        }
        oauth_url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        return redirect(oauth_url)


class PaymentCallbackView(View):
    CALLBACK_URL = "https://tucodigocotidiano.yarumaltech.com/auth/patreon/callback"

    def get(self, request):
        code = request.GET.get("code")
        plan = request.GET.get("state")  # El plan se recupera desde state
        if not code:
            return HttpResponse("No se recibió código de autorización.", status=400)

        token_url = "https://www.patreon.com/api/oauth2/token"
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": self.CALLBACK_URL,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(token_url, data=data, headers=headers)
        if response.status_code != 200:
            return HttpResponse("Error al obtener el token de acceso.", status=400)

        token_data = response.json()
        access_token = token_data.get("access_token")
        # Opcional: Puedes usar el access_token para hacer llamadas a la API de Patreon y obtener información del usuario
        if request.user.is_authenticated:
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            subscription.plan = plan  # Actualiza el plan (Premium o Anual) según el parámetro recibido
            subscription.active = True
            subscription.save()
            mensaje = "Pago exitoso. Tu suscripción se ha actualizado."
        else:
            mensaje = "Usuario no autenticado. Por favor inicia sesión para completar el proceso."

        return HttpResponse(mensaje)

