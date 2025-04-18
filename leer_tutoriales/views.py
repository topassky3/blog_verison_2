from django.views.generic import TemplateView

class VerTutorialesView(TemplateView):
    template_name = ('leer_tutoriales/mis_tutoriales.html')


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, ExpressionWrapper, IntegerField
from core.models import Tutorial
from .forms import CommentForm

from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404
from core.models import Tutorial, Lector
from .forms import CommentForm
from django.contrib.auth.views import redirect_to_login

class TutorialDetailView(FormMixin, DetailView):
    model = Tutorial
    template_name = 'leer_tutoriales/mis_tutoriales.html'
    form_class = CommentForm

    def get_user(self):
        # Si el usuario está autenticado se usa el real,
        # en caso contrario se asigna el usuario por defecto "electro"
        if self.request.user.is_authenticated:
            return self.request.user
        return get_object_or_404(Lector, username="electro")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutorial = self.object
        all_blocks = tutorial.blocks.all()
        total_blocks = all_blocks.count()

        user = self.get_user()

        # Se aplica la restricción (mostrar solo el 60%) si el usuario (real o por defecto)
        # no es el autor y tiene plan "Básico"
        if user != tutorial.author and hasattr(user, 'subscription') and user.subscription.plan == "Básico" and total_blocks > 0:
            visible_count = int(total_blocks * 0.6)
            context['visible_blocks'] = all_blocks[:visible_count]
            context['mostrar_limite'] = True
        else:
            context['visible_blocks'] = all_blocks
            context['mostrar_limite'] = False

        # Lógica para mostrar el botón de descarga:
        # Permitimos la descarga si el usuario es el autor o si tiene una suscripción distinta a "Básico"
        if user == tutorial.author or (hasattr(user, 'subscription') and user.subscription.plan != "Básico"):
            context['mostrar_descarga'] = True
        else:
            context['mostrar_descarga'] = False

        # Comentarios y demás datos de contexto
        top_level_comments = tutorial.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments

        if 'form' not in context:
            context['form'] = self.get_form()
        context['tutorial'] = tutorial
        return context

    def get_success_url(self):
        # Redirige a la misma URL del detalle del tutorial
        return reverse('tutorial_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        # Si el usuario no ha iniciado sesión, se redirige a la página de login.
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.object = self.get_object()  # Obtiene el tutorial actual
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Asumimos que el usuario ya está autenticado
        comment = form.save(commit=False)
        comment.tutorial = self.object
        comment.author = self.request.user  # Usamos el usuario autenticado
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
                from core.models import Comment
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                pass
        comment.save()
        return super().form_valid(form)


# core/views.py (o donde centralices las vistas para interacciones AJAX)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import Comment


@login_required
@require_POST
def toggle_comment_like(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        # Si el usuario ya dio "no me gusta", se quita esa reacción
        if user in comment.dislikes.all():
            comment.dislikes.remove(user)
        comment.likes.add(user)
        liked = True

    data = {
        'liked': liked,
        'like_count': comment.likes.count(),
        'dislike_count': comment.dislikes.count()  # Esto permite actualizar el contador de "no me gusta"
    }
    return JsonResponse(data)


# core/views.py (o donde centralices las vistas AJAX)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import Comment

@login_required
@require_POST
def toggle_comment_dislike(request):
    comment_id = request.POST.get('comment_id')
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)

    user = request.user
    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        # Si el usuario ya dio "me gusta", se quita esa reacción
        if user in comment.likes.all():
            comment.likes.remove(user)
        comment.dislikes.add(user)
        disliked = True

    data = {
        'disliked': disliked,
        'dislike_count': comment.dislikes.count(),
        'like_count': comment.likes.count()  # Para actualizar también el contador de "me gusta"
    }
    return JsonResponse(data)


# core/views.py (nueva vista para borrar comentarios)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import Comment


@login_required
@require_POST
def delete_comment(request):
    comment_id = request.POST.get('comment_id')
    try:
        # Obtenemos el comentario, comprobando que el usuario es el autor
        comment = Comment.objects.get(id=comment_id, author=request.user)
        parent_id = comment.parent.id if comment.parent else None  # Guardamos el id del padre si existe
        comment.delete()
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comentario no encontrado o no tienes permiso para borrarlo.'}, status=404)

    data = {'success': True}
    if parent_id:
        data['parent_id'] = parent_id  # Devolvemos el id del comentario padre si se borró una respuesta
    return JsonResponse(data)



from django.views import View
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Tutorial

class DownloadCodeFileView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        tutorial = get_object_or_404(Tutorial, pk=pk)
        # Verifica si el usuario tiene permiso (es el autor o tiene suscripción premium/anual)
        if not (request.user == tutorial.author or (hasattr(request.user, 'subscription') and request.user.subscription.plan != "Básico")):
            raise Http404("No tienes permiso para descargar este código.")

        if not tutorial.code_file:
            raise Http404("No se encontró el archivo de código para este tutorial.")
        return FileResponse(tutorial.code_file.open('rb'), as_attachment=True, filename=tutorial.code_file.name)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.html import escape
from core.models import Tutorial, Lector

def load_all_tutorial_blocks(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    blocks = tutorial.blocks.all().order_by('order')
    total = blocks.count()

    # Si el usuario no está autenticado, se asigna el usuario "electro"
    if not request.user.is_authenticated:
        user = get_object_or_404(Lector, username="electro")
    else:
        user = request.user

    # Verificar si se debe limitar el contenido:
    # Si el usuario (real o por defecto) no es el autor y tiene plan "Básico"
    if user != tutorial.author and (user.username == "electro" or (hasattr(user, 'subscription') and user.subscription.plan == "Básico")) and total > 0:
        visible_count = int(total * 0.6)
        blocks = blocks[:visible_count]

    blocks_data = []
    for block in blocks:
        content = block.content
        if block.block_type == 'code':
            # Escapa el contenido para que se muestre como texto literal
            content = escape(content)
        elif block.block_type == 'text':
            # Envolver el contenido en un contenedor aislado
            content = '<div class="text-block-wrapper">' + content + '</div>'
        blocks_data.append({
            'id': block.id,
            'block_type': block.block_type,
            'content': content,
            'order': block.order,
        })

    print(f"Enviando {len(blocks_data)} bloques para Tutorial ID {tutorial_id}")
    return JsonResponse({'blocks': blocks_data})
