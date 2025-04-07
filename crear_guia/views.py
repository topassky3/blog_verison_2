import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from core.models import Guia, GuiaBlock
from .forms import GuiaForm  # El formulario debe incluir el campo "code_file"

# Vista para crear una nueva Guía
class GuiaCreateView(CreateView):
    model = Guia
    form_class = GuiaForm
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo usuarios autenticados pueden crear una guía
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asignamos el autor
        form.instance.author = self.request.user
        # Si el usuario NO es escritor, ignoramos el archivo subido
        if not self.request.user.es_escritor:
            form.instance.code_file = None
        self.object = form.save()

        # Procesamos los bloques enviados desde el editor (campo oculto "blocks" en formato JSON)
        blocks_json = self.request.POST.get('blocks')
        if blocks_json:
            try:
                blocks_data = json.loads(blocks_json)
                for index, block in enumerate(blocks_data):
                    GuiaBlock.objects.create(
                        guia=self.object,
                        block_type=block.get('type'),
                        content=block.get('content'),
                        order=index
                    )
            except Exception as e:
                # Si ocurre algún error, eliminamos la guía y devolvemos el error en el formulario
                self.object.delete()
                form.add_error(None, 'Error al guardar los bloques de la guía.')
                return self.form_invalid(form)

        # Si la petición es AJAX se devuelve JSON; de lo contrario se redirige a la vista de edición
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'message': 'Guía creada exitosamente.',
                'guia_pk': self.object.pk
            })
        else:
            return redirect('guia_update', pk=self.object.pk)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'errors': form.errors,
                'message': 'Error en el formulario.'
            }, status=400)
        return super().form_invalid(form)


# Vista para actualizar una Guía existente
class GuiaUpdateView(UpdateView):
    model = Guia
    form_class = GuiaForm
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        guia = self.get_object()
        # Solo el autor de la guía puede editarla
        if not request.user.is_authenticated or request.user != guia.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Si el usuario NO es escritor, se mantiene el archivo de código ya existente
        if not self.request.user.es_escritor:
            form.instance.code_file = self.get_object().code_file
        self.object = form.save()

        # Se actualizan los bloques: se eliminan los anteriores y se crean nuevos a partir del JSON enviado
        blocks_json = self.request.POST.get('blocks')
        if blocks_json:
            try:
                blocks_data = json.loads(blocks_json)
                self.object.blocks.all().delete()
                for index, block in enumerate(blocks_data):
                    GuiaBlock.objects.create(
                        guia=self.object,
                        block_type=block.get('type'),
                        content=block.get('content'),
                        order=index
                    )
            except Exception as e:
                form.add_error(None, 'Error al actualizar los bloques de la guía.')
                return self.form_invalid(form)

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Guía actualizada exitosamente.'})
        else:
            return HttpResponse("<script>alert('Guía actualizada.');history.back();</script>")

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'errors': form.errors,
                'message': 'Error en el formulario.'
            }, status=400)
        return super().form_invalid(form)

from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DeleteView
from core.models import Guia


class GuiaDeleteView(DeleteView):
    model = Guia
    template_name = 'crear_guia/guia_confirm_delete.html'

    def get_success_url(self):
        # Redirige al perfil con el fragmento #guides para activar la pestaña de guías
        return reverse_lazy('profile') + "#guides"

    def dispatch(self, request, *args, **kwargs):
        guia = self.get_object()
        # Solo el autor de la guía puede borrarla
        if not request.user.is_authenticated or request.user != guia.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from core.models import Guia, Subscriber

@login_required
@require_POST
def toggle_publish(request, pk):
    guia = get_object_or_404(Guia, pk=pk, author=request.user)
    guia.publicado = not guia.publicado
    guia.save()

    if guia.publicado:
        # Obtenemos todos los suscriptores (puedes filtrar por active=True si lo deseas)
        subscribers = Subscriber.objects.all()
        recipient_list = [sub.email for sub in subscribers]
        if recipient_list:
            subject = "Nueva Guía Publicada en WebDev Blog"
            # Construye la URL absoluta a la guía
            guia_url = request.build_absolute_uri(f"/leer_guias/guia/{guia.pk}/")
            # Renderiza el contenido HTML del email a partir del template
            html_message = render_to_string("emails/new_guide_email.html", {
                "guia": guia,
                "guia_url": guia_url,
            })
            plain_message = (
                f"Se ha publicado una nueva guía: {guia.title}.\n"
                f"Visítala aquí: {guia_url}\n\n"
                "¡Gracias por suscribirte a WebDev Blog!"
            )
            # Enviamos el email usando EmailMultiAlternatives, pasando la lista en bcc
            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Se utiliza una dirección genérica en "to"
                bcc=recipient_list  # Los suscriptores en copia oculta
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

    return JsonResponse({'published': guia.publicado})