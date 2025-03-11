import json
from django.http import JsonResponse, HttpResponse
from django.views.generic import CreateView, UpdateView
from core.models import Guia, GuiaBlock

class GuiaCreateView(CreateView):
    model = Guia
    # Definimos los campos básicos para la guía
    fields = ['title', 'description', 'category', 'image']
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo usuarios autenticados pueden crear una guía
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asignamos el autor y guardamos la guía
        form.instance.author = self.request.user
        self.object = form.save()

        # Procesamos los bloques enviados (editor similar al tutorial)
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
                self.object.delete()
                form.add_error(None, 'Error al guardar los bloques de la guía.')
                return self.form_invalid(form)

        # Si la petición es AJAX devolvemos JSON; si no, redirigimos a la vista de edición
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


class GuiaUpdateView(UpdateView):
    model = Guia
    fields = ['title', 'description', 'category', 'image']
    template_name = 'crear_guia/crear_guia.html'

    def dispatch(self, request, *args, **kwargs):
        guia = self.get_object()
        # Solo el autor de la guía puede editarla
        if not request.user.is_authenticated or request.user != guia.author:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        # Se procesan y actualizan los bloques:
        # Se eliminan los anteriores y se crean nuevos a partir del JSON enviado.
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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import Guia

@login_required
@require_POST
def toggle_publish(request, pk):
    guia = get_object_or_404(Guia, pk=pk, author=request.user)
    guia.publicado = not guia.publicado
    guia.save()
    return JsonResponse({'published': guia.publicado})


