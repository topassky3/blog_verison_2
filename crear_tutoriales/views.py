import json
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView
from core.models import Tutorial, TutorialBlock

class TutorialCreateView(CreateView):
    model = Tutorial
    fields = ['title', 'duration', 'level']
    template_name = 'crear_tutoriales/tutorial_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Verificar que el usuario esté autenticado y sea escritor
        if not request.user.is_authenticated or not request.user.es_escritor:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        # Guardar bloques (siempre que vengan en POST)
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
                self.object.delete()  # Eliminar tutorial si hubo error
                form.add_error(None, 'Error al guardar los bloques del tutorial.')
                return self.form_invalid(form)

        # Si la petición es AJAX, respondemos con JSON
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'message': 'Tutorial creado exitosamente.',
                'tutorial_pk': self.object.pk  # Importante devolver la pk
            }
            return JsonResponse(data)
        else:
            # Si no es AJAX, redirigir de manera normal
            return redirect('tutorial_update', pk=self.object.pk)


class TutorialUpdateView(UpdateView):
    model = Tutorial
    fields = ['title', 'duration', 'level']
    template_name = 'crear_tutoriales/tutorial_form.html'

    def dispatch(self, request, *args, **kwargs):
        tutorial = self.get_object()
        # Asegurar que el usuario sea el autor
        if not request.user.is_authenticated or request.user != tutorial.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        # Procesar bloques
        blocks_json = self.request.POST.get('blocks')
        if blocks_json:
            try:
                blocks_data = json.loads(blocks_json)
                # Borramos bloques anteriores y creamos nuevos
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
