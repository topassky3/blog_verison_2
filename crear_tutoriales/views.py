import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView
from core.models import Tutorial, TutorialBlock

class TutorialCreateView(CreateView):
    model = Tutorial
    fields = ['title', 'duration', 'level', 'category', 'image', 'code_file']
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
    fields = ['title', 'duration', 'level', 'category', 'image', 'code_file']
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
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from core.models import Tutorial
from core.models import Subscriber

@login_required
@require_POST
def toggle_publish(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk, author=request.user)
    # Alterna el estado de publicación
    tutorial.publicado = not tutorial.publicado
    tutorial.save()

    # Si se acaba de publicar el tutorial, enviamos el email a los suscriptores
    if tutorial.publicado:
        # Obtener todos los suscriptores activos (si tienes un filtro, por ejemplo, active=True)
        subscribers = Subscriber.objects.all()
        recipient_list = [sub.email for sub in subscribers]
        if recipient_list:
            subject = "Nuevo tutorial publicado en WebDev Blog"
            # Renderiza el template HTML para el correo
            html_message = render_to_string("emails/new_tutorial_email.html", {
                "tutorial": tutorial,
                "tutorial_url": request.build_absolute_uri(f"/tutoriales/{tutorial.pk}/")
            })
            # Mensaje plano de respaldo
            plain_message = (
                f"Se ha publicado un nuevo tutorial: {tutorial.title}.\n"
                f"Visítalo aquí: {request.build_absolute_uri(f'/tutoriales/{tutorial.pk}/')}\n\n"
                "¡Gracias por suscribirte a WebDev Blog!"
            )
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
                html_message=html_message,
            )

    return JsonResponse({'published': tutorial.publicado})
