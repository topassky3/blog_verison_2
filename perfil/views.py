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
            # Si el usuario es escritor, redirige a la URL 'escritor_profile'
            return redirect('escritor_profile')
    else:
        form = ProfileForm(instance=user)

    # Tutoriales del usuario (paginar 6 por página)
    tutorials = user.tutorials.order_by('-created_at')
    paginator = Paginator(tutorials, 6)
    page = request.GET.get('page')
    try:
        tutorials_page = paginator.page(page)
    except PageNotAnInteger:
        tutorials_page = paginator.page(1)
    except EmptyPage:
        tutorials_page = paginator.page(paginator.num_pages)

    # Podcasts subidos por el usuario (paginar 6 por página)
    podcasts = user.podcasts.order_by('-created_at')
    paginator_podcasts = Paginator(podcasts, 6)
    podcast_page = request.GET.get('podcast_page')
    try:
        podcasts_page = paginator_podcasts.page(podcast_page)
    except PageNotAnInteger:
        podcasts_page = paginator_podcasts.page(1)
    except EmptyPage:
        podcasts_page = paginator_podcasts.page(paginator_podcasts.num_pages)

    # Seleccionar plantilla según grupo
    if user.groups.filter(name="Escritor").exists():
        template_name = 'perfil/escritor_profile.html'
    else:
        template_name = 'perfil/lector_profile.html'

    context = {
        'form': form,
        'tutorials': tutorials_page,
        'podcasts': podcasts_page,  # Se agregan los podcasts al contexto
    }
    return render(request, template_name, context)
