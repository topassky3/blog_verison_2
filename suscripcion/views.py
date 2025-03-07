import os
import requests
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.views import View
from django.http import HttpResponse
from core.models import Subscription

# Obtén las credenciales desde variables de entorno o usa estos valores por defecto
CLIENT_ID = os.environ.get("APTREON_CLIENT_ID", "g_WawYPEVgQ1p2j4H37rpLaLjhwZuR9okxqYSZ4fRrOpOT975PshTu_m5XZLc1j1")
CLIENT_SECRET = os.environ.get("APTREON_CLIENT_SECRET",
                               "aIwCYXgfX0AHIRQ0pxdZuE165bDTA5NuPdO2kByE_aJJLTSsTjga_xVwjfslwN5A")
OAUTH_AUTHORIZE_URL = "https://www.patreon.com/oauth2/authorize"


class IniciarPagoView(View):
    def get(self, request, plan):
        # Callback URI que usaremos y que debe estar registrado en el panel de Patreon
        callback_url = "https://tucodigocotidiano.yarumaltech.com/suscripcion/auth/patreon/callback"
        # Parámetros para iniciar el flujo OAuth
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": callback_url,
            "scope": "identity identity.memberships",  # Ajusta los scopes según lo que necesites
            "state": plan,  # En state enviamos el plan solicitado (Premium o Anual)
        }
        oauth_url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        return redirect(oauth_url)


class PaymentCallbackView(View):
    # Debe coincidir con el callback URL
    CALLBACK_URL = "https://tucodigocotidiano.yarumaltech.com/suscripcion/auth/patreon/callback"

    def get(self, request):
        # Si se deniega el acceso o hay un error, se maneja aquí
        if "error" in request.GET:
            error = request.GET.get("error")
            error_description = request.GET.get("error_description", "")
            context = {"error": error, "error_description": error_description}
            return render(request, "suscripcion/patreon_error.html", context)

        code = request.GET.get("code")
        plan = request.GET.get("state")  # Recuperamos el plan solicitado
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
        # Opcional: Puedes usar el access_token para obtener información del usuario desde la API de Patreon

        if request.user.is_authenticated:
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            subscription.plan = plan  # Actualiza el plan (Premium o Anual)
            subscription.active = True
            subscription.save()
            mensaje = "Pago exitoso. Tu suscripción se ha actualizado."
        else:
            mensaje = "Usuario no autenticado. Por favor inicia sesión para completar el proceso."

        return HttpResponse(mensaje)
