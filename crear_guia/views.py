import json
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from core.models import Guia, GuiaBlock
from .forms import GuiaForm


class GuiaCreateView(CreateView):
    model = Guia
    form_class = GuiaForm
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        blocks_json = self.request.POST.get('blocks', '[]')
        try:
            blocks_data = json.loads(blocks_json)
        except json.JSONDecodeError:
            blocks_data = []

        for idx, blk_data in enumerate(blocks_data):
            block_type = blk_data.get('type')
            content = blk_data.get('content', '')

            if block_type == 'image':
                # El 'content' aquí es el nombre del campo input (ej: 'block_image_12345')
                image_file = self.request.FILES.get(content)
                if image_file:
                    GuiaBlock.objects.create(
                        guia=self.object,
                        block_type='image',
                        image=image_file,
                        content='',  # El contenido de texto está vacío para las imágenes
                        order=idx
                    )
            elif block_type in ['text', 'latex', 'code']:
                GuiaBlock.objects.create(
                    guia=self.object,
                    block_type=block_type,
                    content=content,  # Aquí sí guardamos el contenido de texto
                    order=idx
                )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Guía creada exitosamente.', 'guia_pk': self.object.pk})

        messages.success(self.request, '¡Guía creada exitosamente!')
        return redirect('guia_update', pk=self.object.pk)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return super().form_invalid(form)


class GuiaUpdateView(UpdateView):
    model = Guia
    form_class = GuiaForm
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        guia = self.get_object()
        if not request.user.is_authenticated or request.user != guia.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        blocks_json = self.request.POST.get('blocks', '[]')
        try:
            blocks_data = json.loads(blocks_json)
        except json.JSONDecodeError:
            blocks_data = []

        # Guardar rutas de imágenes antiguas antes de borrar los bloques
        old_images = {str(b.id): b.image for b in self.object.blocks.filter(block_type='image')}
        self.object.blocks.all().delete()

        for idx, blk_data in enumerate(blocks_data):
            block_type = blk_data.get('type')
            content_payload = blk_data.get('content', '')

            if block_type == 'image':
                image_to_save = None
                # Caso 1: Se mantiene una imagen existente
                if content_payload.startswith('keep-'):
                    img_id = content_payload.replace('keep-', '')
                    image_to_save = old_images.get(img_id)
                # Caso 2: Se sube una imagen nueva
                else:
                    image_to_save = self.request.FILES.get(content_payload)

                if image_to_save:
                    GuiaBlock.objects.create(
                        guia=self.object,
                        block_type='image',
                        image=image_to_save,
                        content='',  # El contenido de texto es vacío para imágenes
                        order=idx
                    )
            elif block_type in ['text', 'latex', 'code']:
                GuiaBlock.objects.create(
                    guia=self.object,
                    block_type=block_type,
                    content=content_payload,  # Guardamos el texto
                    order=idx
                )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Guía actualizada exitosamente.'})

        messages.success(self.request, '¡Guía actualizada exitosamente!')
        return redirect('guia_update', pk=self.object.pk)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return super().form_invalid(form)


# Aquí puedes mantener tus otras vistas como GuiaDeleteView y toggle_publish sin cambios.
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