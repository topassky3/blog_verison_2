import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView
from core.models import Tutorial, TutorialBlock, TutorialCarouselImage

class TutorialCreateView(CreateView):
    model = Tutorial
    fields = ['title', 'description', 'meta_description', 'duration', 'level', 'category', 'image', 'code_file']
    template_name = 'crear_tutoriales/tutorial_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Verifica que el usuario esté autenticado y sea escritor
        if not request.user.is_authenticated or not request.user.es_escritor:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print("FILES:", self.request.FILES)
        # Asigna el autor y guarda el tutorial
        form.instance.author = self.request.user
        self.object = form.save()

        # Procesa las imágenes del carrusel
        carousel_images = self.request.FILES.getlist('carousel_images')
        for image in carousel_images:
            TutorialCarouselImage.objects.create(
                tutorial=self.object,
                image=image
            )

        # Procesa los bloques enviados en formato JSON
        blocks_json = self.request.POST.get('blocks')
        if blocks_json:
            try:
                blocks_data = json.loads(blocks_json)
                for index, block in enumerate(blocks_data):
                    TutorialBlock.objects.create(
                        tutorial=self.object,
                        block_type=block.get('type'),
                        content=block.get('content'),
                        order=index
                    )
            except Exception as e:
                self.object.delete()  # Si ocurre un error, elimina el tutorial para evitar inconsistencias
                form.add_error(None, 'Error al guardar los bloques del tutorial.')
                return self.form_invalid(form)

        # Si la petición es AJAX, devuelve JSON con el ID del tutorial
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'message': 'Tutorial creado exitosamente.',
                'tutorial_pk': self.object.pk
            }
            return JsonResponse(data)
        else:
            return redirect('tutorial_update', pk=self.object.pk)

    def form_invalid(self, form):
        # Devuelve errores en JSON si es AJAX
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'errors': form.errors,
                'message': 'Error en el formulario.'
            }, status=400)
        return super().form_invalid(form)


class TutorialUpdateView(UpdateView):
    model = Tutorial
    fields = ['title', 'description', 'meta_description', 'duration', 'level', 'category', 'image', 'code_file']
    template_name = 'crear_tutoriales/tutorial_form.html'

    def dispatch(self, request, *args, **kwargs):
        tutorial = self.get_object()
        # Asegura que solo el autor pueda editar
        if not request.user.is_authenticated or request.user != tutorial.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        # Procesa y actualiza los bloques: se eliminan los anteriores y se crean nuevos
        blocks_json = self.request.POST.get('blocks')
        if blocks_json:
            try:
                blocks_data = json.loads(blocks_json)
                self.object.blocks.all().delete()
                for index, block in enumerate(blocks_data):
                    TutorialBlock.objects.create(
                        tutorial=self.object,
                        block_type=block.get('type'),
                        content=block.get('content'),
                        order=index
                    )
            except Exception as e:
                form.add_error(None, 'Error al actualizar los bloques del tutorial.')
                return self.form_invalid(form)

        # Procesa nuevas imágenes del carrusel (si se subieron)
        carousel_images = self.request.FILES.getlist('carousel_images')
        for image in carousel_images:
            TutorialCarouselImage.objects.create(
                tutorial=self.object,
                image=image
            )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'message': 'Tutorial actualizado exitosamente.'
            }
            return JsonResponse(data)
        else:
            return HttpResponse("<script>alert('Tutorial actualizado.');history.back();</script>")

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'errors': form.errors,
                'message': 'Error en el formulario.'
            }, status=400)
        return super().form_invalid(form)

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.shortcuts import redirect
from core.models import Tutorial

class TutorialDeleteView(DeleteView):
    model = Tutorial
    template_name = 'crear_tutoriales/tutorial_confirm_delete.html'
    success_url = reverse_lazy('profile')  # Redirige al perfil tras borrar

    def dispatch(self, request, *args, **kwargs):
        tutorial = self.get_object()
        # Solo el autor puede borrar su tutorial
        if not request.user.is_authenticated or request.user != tutorial.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from core.models import Tutorial, Subscriber

@login_required
@require_POST
def toggle_publish(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk, author=request.user)
    # Alterna el estado de publicación
    tutorial.publicado = not tutorial.publicado
    tutorial.save()

    # Si se acaba de publicar el tutorial, enviamos el email a los suscriptores
    if tutorial.publicado:
        # Obtener todos los suscriptores activos (puedes aplicar un filtro si es necesario)
        subscribers = Subscriber.objects.all()
        recipient_list = [sub.email for sub in subscribers]
        if recipient_list:
            subject = "Nuevo tutorial publicado en WebDev Blog"
            # Construir la URL absoluta del tutorial
            tutorial_url = request.build_absolute_uri(f"/leer_tutoriales/{tutorial.pk}/")
            # Renderizar el template HTML para el correo
            html_message = render_to_string("emails/new_tutorial_email.html", {
                "tutorial": tutorial,
                "tutorial_url": tutorial_url,
            })
            # Mensaje plano de respaldo
            plain_message = (
                f"Se ha publicado un nuevo tutorial: {tutorial.title}.\n"
                f"Visítalo aquí: {tutorial_url}\n\n"
                "¡Gracias por suscribirte a WebDev Blog!"
            )
            # Usamos EmailMultiAlternatives para enviar el correo con copia oculta (bcc)
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],  # Dirección genérica en 'to'
                bcc=recipient_list  # Los suscriptores en copia oculta
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

    return JsonResponse({'published': tutorial.publicado})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from core.models import TutorialCarouselImage

@login_required
def delete_carousel_image(request, pk):
    # Obtiene la imagen del carrusel o devuelve 404 si no existe.
    image_obj = get_object_or_404(TutorialCarouselImage, pk=pk)
    # Verifica que el usuario sea el autor del tutorial al que pertenece la imagen.
    if request.user != image_obj.tutorial.author:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    # Elimina la imagen
    image_obj.delete()
    return JsonResponse({'success': True})
