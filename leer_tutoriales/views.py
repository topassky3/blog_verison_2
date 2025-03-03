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

class TutorialDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Tutorial
    template_name = 'leer_tutoriales/mis_tutoriales.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tutorial'] = self.object
        # Calculamos el score: diferencia de me gusta y no me gusta.
        top_level_comments = self.object.comments.filter(parent__isnull=True).annotate(
            like_count=Count('likes'),
            dislike_count=Count('dislikes'),
            score=ExpressionWrapper(Count('likes') - Count('dislikes'), output_field=IntegerField())
        ).order_by('-score', '-created_at')
        context['top_level_comments'] = top_level_comments
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def get_success_url(self):
        # Redirige a la misma URL del detalle del tutorial
        return reverse('tutorial_detail', kwargs={'pk': self.object.pk}) + "#comments"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Obtiene el tutorial actual
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.tutorial = self.object
        comment.author = self.request.user
        # Si se envía el campo 'parent', se asigna el comentario padre
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
