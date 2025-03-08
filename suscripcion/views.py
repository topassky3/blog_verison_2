import os
import requests
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponse
from core.models import Subscription


# Vista para mostrar la página de suscripción
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


# Vista para iniciar el flujo OAuth de Patreon
class IniciarPagoView(View):
    def get(self, request, plan):
        # Callback URI EXACTO que usaremos y que debe estar registrado en Patreon:
        callback_url = "https://tucodigocotidiano.yarumaltech.com/suscripcion/auth/patreon/callback"
        CLIENT_ID = os.environ.get("APTREON_CLIENT_ID",
                                   "g_WawYPEVgQ1p2j4H37rpLaLjhwZuR9okxqYSZ4fRrOpOT975PshTu_m5XZLc1j1")
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": callback_url,
            "scope": "identity identity.memberships",  # Ajusta los scopes según tus necesidades
            "state": plan,  # En state enviamos el plan solicitado (Premium o Anual)
        }
        oauth_url = f"https://www.patreon.com/oauth2/authorize?{urlencode(params)}"
        return redirect(oauth_url)


# Vista para manejar el callback de Patreon
class PaymentCallbackView(View):
    CALLBACK_URL = "https://tucodigocotidiano.yarumaltech.com/suscripcion/auth/patreon/callback"

    def get(self, request):
        # Manejo de error (por ejemplo, si el usuario deniega el acceso)
        if "error" in request.GET:
            error = request.GET.get("error")
            error_description = request.GET.get("error_description", "")
            context = {"error": error, "error_description": error_description}
            return render(request, "suscripcion/patreon_error.html", context)

        code = request.GET.get("code")
        plan = request.GET.get("state")  # Recuperamos el plan desde el parámetro state
        if not code:
            return HttpResponse("No se recibió código de autorización.", status=400)

        token_url = "https://www.patreon.com/api/oauth2/token"
        CLIENT_ID = os.environ.get("APTREON_CLIENT_ID",
                                   "g_WawYPEVgQ1p2j4H37rpLaLjhwZuR9okxqYSZ4fRrOpOT975PshTu_m5XZLc1j1")
        CLIENT_SECRET = os.environ.get("APTREON_CLIENT_SECRET",
                                       "aIwCYXgfX0AHIRQ0pxdZuE165bDTA5NuPdO2kByE_aJJLTSsTjga_xVwjfslwN5A")
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
        # Opcional: Puedes utilizar el access_token para obtener información del usuario a través de la API de Patreon

        if request.user.is_authenticated:
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            subscription.plan = plan  # Actualiza el plan (Premium o Anual) según lo recibido
            subscription.active = True
            subscription.save()
            mensaje = "Pago exitoso. Tu suscripción se ha actualizado."
        else:
            mensaje = "Usuario no autenticado. Por favor inicia sesión para completar el proceso."

        return HttpResponse(mensaje)
