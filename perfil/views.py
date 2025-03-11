from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('escritor_profile')
    else:
        form = ProfileForm(instance=user)

    # Tutoriales del usuario (6 por página)
    tutorials = user.tutorials.order_by('-created_at')
    paginator = Paginator(tutorials, 6)
    page = request.GET.get('page')
    try:
        tutorials_page = paginator.page(page)
    except PageNotAnInteger:
        tutorials_page = paginator.page(1)
    except EmptyPage:
        tutorials_page = paginator.page(paginator.num_pages)

    # Podcasts subidos (6 por página)
    podcasts = user.podcasts.order_by('-created_at')
    paginator_podcasts = Paginator(podcasts, 6)
    podcast_page = request.GET.get('podcast_page')
    try:
        podcasts_page = paginator_podcasts.page(podcast_page)
    except PageNotAnInteger:
        podcasts_page = paginator_podcasts.page(1)
    except EmptyPage:
        podcasts_page = paginator_podcasts.page(paginator_podcasts.num_pages)

    # Guías subidas (6 por página)
    guias = user.guias.order_by('-created_at')
    paginator_guides = Paginator(guias, 6)
    guide_page = request.GET.get('guide_page')
    try:
        guias_page = paginator_guides.page(guide_page)
    except PageNotAnInteger:
        guias_page = paginator_guides.page(1)
    except EmptyPage:
        guias_page = paginator_guides.page(paginator_guides.num_pages)

    # Selecciona la plantilla según el grupo del usuario
    if user.groups.filter(name="Escritor").exists():
        template_name = 'perfil/escritor_profile.html'
    else:
        template_name = 'perfil/lector_profile.html'

    context = {
        'form': form,
        'tutorials': tutorials_page,
        'podcasts': podcasts_page,
        'guias': guias_page,  # Agregamos las guías al contexto
    }
    return render(request, template_name, context)
