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
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    # Obtener los tutoriales del usuario ordenados de más nuevos a más antiguos
    tutorials = user.tutorials.order_by('-created_at')

    # Paginar la lista de tutoriales de a 6 por página
    paginator = Paginator(tutorials, 6)
    page = request.GET.get('page')
    try:
        tutorials_page = paginator.page(page)
    except PageNotAnInteger:
        tutorials_page = paginator.page(1)
    except EmptyPage:
        tutorials_page = paginator.page(paginator.num_pages)

    # Seleccionar la plantilla según el grupo del usuario
    if user.groups.filter(name="Escritor").exists():
        template_name = 'perfil/escritor_profile.html'
    else:
        template_name = 'perfil/lector_profile.html'

    return render(request, template_name, {'form': form, 'tutorials': tutorials_page})
