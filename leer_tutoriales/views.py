# leer_tutoriales/views.py

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, FileResponse, Http404
from django.views.generic import DetailView, TemplateView, View
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, ExpressionWrapper, IntegerField
from django.conf import settings
import bleach

from core.models import Tutorial, Comment, Lector
from .forms import CommentForm


class VerTutorialesView(TemplateView):
    template_name = 'leer_tutoriales/mis_tutoriales.html'


class TutorialDetailView(FormMixin, DetailView):
    model = Tutorial
    template_name = 'leer_tutoriales/mis_tutoriales.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutorial = self.object
        current_user = self.request.user

        user_for_content_check = current_user if current_user.is_authenticated else get_object_or_404(Lector,
                                                                                                      username="electro")

        context['mostrar_limite'] = False
        if hasattr(tutorial, 'blocks') and tutorial.blocks.exists():
            total_blocks = tutorial.blocks.count()
            if user_for_content_check != tutorial.author and hasattr(user_for_content_check,
                                                                     'subscription') and user_for_content_check.subscription.plan == "Básico" and total_blocks > 0:
                context['mostrar_limite'] = True

        user_is_author = current_user.is_authenticated and current_user == tutorial.author
        user_has_premium_or_higher = current_user.is_authenticated and hasattr(current_user,
                                                                               'subscription') and current_user.subscription.plan != "Básico"
        user_can_download_directly = user_is_author or user_has_premium_or_higher

        context['mostrar_descarga'] = bool(tutorial.code_file) and user_can_download_directly
        context['code_file_exists'] = bool(tutorial.code_file)

        if context['code_file_exists']:
            if user_can_download_directly:
                context.update({
                    'title_download_url': reverse('download_code_file', kwargs={'pk': tutorial.pk}),
                    'title_download_cta_type': 'download',
                    'title_download_button_text': 'Descargar Código',
                    'title_download_link_title_attr': 'Descargar código fuente del tutorial'
                })
            elif not current_user.is_authenticated:
                login_url = reverse_lazy('login:login')
                context.update({
                    'title_download_url': f"{login_url}?next={self.request.path}",
                    'title_download_cta_type': 'login',
                    'title_download_button_text': 'Descargar',
                    'title_download_link_title_attr': 'Iniciar sesión para descargar'
                })
            else:
                context.update({
                    'title_download_url': reverse_lazy('suscripcion_home'),
                    'title_download_cta_type': 'subscribe',
                    'title_download_button_text': 'Descargar',
                    'title_download_link_title_attr': 'Obtener membresía para descargar'
                })

        context['top_level_comments'] = tutorial.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')

        if 'form' not in context:
            context['form'] = self.get_form()

        return context

    def get_success_url(self):
        return reverse('tutorial_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
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


@login_required
@require_POST
def toggle_comment_like(request):
    comment_id = request.POST.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.dislikes.remove(user) if user in comment.dislikes.all() else None
        comment.likes.add(user)

    return JsonResponse({
        'liked': user in comment.likes.all(),
        'like_count': comment.likes.count(),
        'dislike_count': comment.dislikes.count()
    })


@login_required
@require_POST
def toggle_comment_dislike(request):
    comment_id = request.POST.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
    else:
        comment.likes.remove(user) if user in comment.likes.all() else None
        comment.dislikes.add(user)

    return JsonResponse({
        'disliked': user in comment.dislikes.all(),
        'dislike_count': comment.dislikes.count(),
        'like_count': comment.likes.count()
    })


@login_required
@require_POST
def delete_comment(request):
    comment_id = request.POST.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    parent_id = comment.parent.id if comment.parent else None
    comment.delete()

    data = {'success': True}
    if parent_id:
        data['parent_id'] = parent_id
    return JsonResponse(data)


class DownloadCodeFileView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        tutorial = get_object_or_404(Tutorial, pk=pk)
        if not (request.user == tutorial.author or (
                hasattr(request.user, 'subscription') and request.user.subscription.plan != "Básico")):
            raise Http404("No tienes permiso para descargar este código.")

        if not tutorial.code_file:
            raise Http404("No se encontró el archivo de código para este tutorial.")

        return FileResponse(tutorial.code_file.open('rb'), as_attachment=True, filename=tutorial.code_file.name)


# Asegúrate de tener estos imports al principio del archivo
import re
from django.utils.html import escape
from django.conf import settings
import bleach
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from core.models import Tutorial, Lector


# ... y tus otros imports

# Esta es la versión final y definitiva de la función
def load_all_tutorial_blocks(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    blocks = tutorial.blocks.all().order_by('order')
    total = blocks.count()
    user = request.user if request.user.is_authenticated else get_object_or_404(Lector, username="electro")

    if user != tutorial.author and (not request.user.is_authenticated or (
            hasattr(user, 'subscription') and user.subscription.plan == "Básico")) and total > 0:
        visible_count = max(1, int(total * 0.6))
        blocks = blocks[:visible_count]

    blocks_data = []
    for block in blocks:
        content = block.content
        if block.block_type == 'text':

            # --- TÉCNICA DEL PLACEHOLDER ---

            code_snippets = []

            def replace_with_placeholder(match):
                # Guarda el código original en nuestra lista
                code_snippets.append(match.group(1))
                # Reemplázalo con un marcador único en el texto principal
                return f"__CODE_PLACEHOLDER_{len(code_snippets) - 1}__"

            # 1. Reemplazamos todos los <code>...</code> con marcadores
            content_with_placeholders = re.sub(
                r'<code>(.*?)</code>',
                replace_with_placeholder,
                block.content,
                flags=re.DOTALL
            )

            # 2. Limpiamos el HTML principal. Bleach ignorará los marcadores.
            sanitized_content = bleach.clean(
                content_with_placeholders,
                tags=settings.BLEACH_ALLOWED_TAGS,
                attributes=settings.BLEACH_ALLOWED_ATTRIBUTES
            )

            # 3. Reemplazamos los marcadores por el código original, ahora sí, escapado.
            final_content = sanitized_content
            for i, raw_code in enumerate(code_snippets):
                # Creamos la etiqueta <code> con el contenido escapado
                escaped_code_tag = f"<code>{escape(raw_code)}</code>"
                final_content = final_content.replace(
                    f"__CODE_PLACEHOLDER_{i}__",
                    escaped_code_tag
                )

            content = final_content
            # --- FIN DE LA TÉCNICA ---

        blocks_data.append({
            'id': block.id,
            'block_type': block.block_type,
            'content': content,
            'order': block.order,
        })

    return JsonResponse({'blocks': blocks_data})