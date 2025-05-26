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

from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404
from core.models import Tutorial, Lector
from .forms import CommentForm
from django.contrib.auth.views import redirect_to_login


class TutorialDetailView(FormMixin, DetailView):
    model = Tutorial
    template_name = 'leer_tutoriales/mis_tutoriales.html'  # ESTE ES EL NOMBRE DE TU PLANTILLA
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutorial = self.object
        current_user = self.request.user

        # --- Lógica para limitación de contenido (60%) ---
        # Esta lógica asume que los bloques se cargan vía AJAX y la plantilla decide si mostrar el mensaje.
        # Si la carga de bloques es puramente vía AJAX, la limitación real de bloques se hace en la vista AJAX.
        user_for_content_check = current_user if current_user.is_authenticated else get_object_or_404(Lector,
                                                                                                      username="electro")

        context['mostrar_limite'] = False
        if hasattr(tutorial, 'blocks') and tutorial.blocks.exists():  # Solo si hay bloques
            total_blocks = tutorial.blocks.count()
            if user_for_content_check != tutorial.author and \
                    hasattr(user_for_content_check, 'subscription') and \
                    user_for_content_check.subscription.plan == "Básico" and \
                    total_blocks > 0:
                context['mostrar_limite'] = True

        # --- Lógica para Permisos de Descarga ---
        user_is_author = current_user.is_authenticated and current_user == tutorial.author
        user_has_premium_or_higher = current_user.is_authenticated and \
                                     hasattr(current_user, 'subscription') and \
                                     current_user.subscription.plan != "Básico"

        user_can_download_directly = user_is_author or user_has_premium_or_higher

        # Para el botón de descarga principal (al final del artículo)
        context['mostrar_descarga'] = bool(tutorial.code_file) and user_can_download_directly

        # Para el nuevo botón de descarga junto al título
        context['code_file_exists'] = bool(tutorial.code_file)

        if context['code_file_exists']:
            if user_can_download_directly:
                context['title_download_url'] = reverse('download_code_file', kwargs={'pk': tutorial.pk})
                context['title_download_cta_type'] = 'download'
                context['title_download_button_text'] = 'Descargar Código'
                context['title_download_link_title_attr'] = 'Descargar código fuente del tutorial'
            elif not current_user.is_authenticated:
                # Asegúrate de que 'login:login' es el nombre correcto de tu URL de login
                # y que tu app de login tiene app_name='login'
                login_url = reverse_lazy('login:login')
                context['title_download_url'] = f"{login_url}?next={self.request.path}"
                context['title_download_cta_type'] = 'login'
                context['title_download_button_text'] = 'Descargar'  # O 'Descargar (Login)'
                context['title_download_link_title_attr'] = 'Iniciar sesión para descargar'
            else:  # Autenticado, pero no tiene permisos (ej. plan Básico y no es autor)
                # Asegúrate de que 'suscripcion_home' es el nombre correcto de tu URL de suscripciones
                context['title_download_url'] = reverse_lazy('suscripcion_home')
                context['title_download_cta_type'] = 'subscribe'
                context['title_download_button_text'] = 'Descargar'  # O 'Descargar (Premium)'
                context['title_download_link_title_attr'] = 'Obtener membresía para descargar'
        else:
            context['title_download_url'] = '#'
            context['title_download_cta_type'] = 'none'  # No se mostrará el botón
            context['title_download_button_text'] = ''
            context['title_download_link_title_attr'] = ''

        # Comentarios
        top_level_comments = tutorial.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments

        if 'form' not in context:
            context['form'] = self.get_form()
        # context['tutorial'] ya está disponible como self.object
        return context

    def get_success_url(self):
        return reverse('tutorial_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Asumiendo que 'login:login' es el nombre de tu URL de login
            # y que tu app de login se llama 'login'
            login_url = reverse_lazy('login:login')
            return redirect_to_login(request.get_full_path(), login_url=login_url)

        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.tutorial = self.object
        comment.author = self.request.user
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
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

# VISTA views.py - CORREGIDA
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from core.models import Tutorial, Lector
# No necesitas 'escape' si solo lo usas aquí, puedes borrar el import

def load_all_tutorial_blocks(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    blocks = tutorial.blocks.all().order_by('order')
    total = blocks.count()

    if not request.user.is_authenticated:
        user = get_object_or_404(Lector, username="electro")
    else:
        user = request.user

    if user != tutorial.author and (user.username == "electro" or (hasattr(user, 'subscription') and user.subscription.plan == "Básico")) and total > 0:
        visible_count = int(total * 0.6)
        blocks = blocks[:visible_count]

    blocks_data = []
    for block in blocks:
        # Aquí ya no escapamos el contenido del código
        content = block.content
        if block.block_type == 'text':
            content = '<div class="text-block-wrapper">' + content + '</div>'

        blocks_data.append({
            'id': block.id,
            'block_type': block.block_type,
            'content': content,
            'order': block.order,
        })

    print(f"Enviando {len(blocks_data)} bloques para Tutorial ID {tutorial_id}")
    return JsonResponse({'blocks': blocks_data})
