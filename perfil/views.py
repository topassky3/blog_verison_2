# perfil/views.py

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
# --- ¡IMPORTACIONES NUEVAS! ---
from core.models import Lector, Tutorial, Guia, Podcast, Comment


@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            # He cambiado esto a 'profile' que parece ser tu URL principal del perfil
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    # --- LÓGICA DE PAGINACIÓN (ya la tienes, la dejamos igual) ---
    # Tutoriales
    tutorials = user.tutorials.order_by('-created_at')
    paginator = Paginator(tutorials, 6)
    page = request.GET.get('page')
    try:
        tutorials_page = paginator.page(page)
    except PageNotAnInteger:
        tutorials_page = paginator.page(1)
    except EmptyPage:
        tutorials_page = paginator.page(paginator.num_pages)

    # Podcasts
    podcasts = user.podcasts.order_by('-created_at')
    paginator_podcasts = Paginator(podcasts, 6)
    podcast_page = request.GET.get('podcast_page')
    try:
        podcasts_page = paginator_podcasts.page(podcast_page)
    except PageNotAnInteger:
        podcasts_page = paginator_podcasts.page(1)
    except EmptyPage:
        podcasts_page = paginator_podcasts.page(paginator_podcasts.num_pages)

    # Guías
    guias = user.guias.order_by('-created_at')
    paginator_guides = Paginator(guias, 6)
    guide_page = request.GET.get('guide_page')
    try:
        guias_page = paginator_guides.page(guide_page)
    except PageNotAnInteger:
        guias_page = paginator_guides.page(1)
    except EmptyPage:
        guias_page = paginator_guides.page(paginator_guides.num_pages)

    # --- INICIO DE LA NUEVA LÓGICA DE ESTADÍSTICAS ---

    # Estadísticas específicas del autor logueado
    total_comentarios_en_tutoriales = Comment.objects.filter(tutorial__author=user).count()
    # (Haríamos lo mismo para comentarios de guías y podcasts si los modelos existen)

    stats_autor = {
        'total_tutoriales': user.tutorials.count(),
        'total_guias': user.guias.count(),
        'total_podcasts': user.podcasts.count(),
        'total_comentarios': total_comentarios_en_tutoriales,
    }

    # Estadísticas generales del sitio (solo si es escritor)
    stats_generales = {}
    if user.groups.filter(name="Escritor").exists():
        stats_generales = {
            'total_usuarios': Lector.objects.count(),
            'total_tutoriales_publicados': Tutorial.objects.filter(publicado=True).count(),
            'total_guias_publicadas': Guia.objects.filter(publicado=True).count(),
            'total_podcasts_publicados': Podcast.objects.filter(publicado=True).count(),
        }

    # --- FIN DE LA NUEVA LÓGICA DE ESTADÍSTICAS ---

    if user.groups.filter(name="Escritor").exists():
        template_name = 'perfil/escritor_profile.html'
    else:
        template_name = 'perfil/lector_profile.html'

    context = {
        'form': form,
        'tutorials': tutorials_page,
        'podcasts': podcasts_page,
        'guias': guias_page,
        'stats_autor': stats_autor,  # <--- Nuevo contexto
        'stats_generales': stats_generales,  # <--- Nuevo contexto
    }
    return render(request, template_name, context)