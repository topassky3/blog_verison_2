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
            # Puedes agregar un mensaje de éxito o redirigir a otra vista
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    # Seleccionar la plantilla según el grupo del usuario
    if user.groups.filter(name="Escritor").exists():
        template_name = 'perfil/escritor_profile.html'
    else:
        template_name = 'perfil/lector_profile.html'

    return render(request, template_name, {'form': form})
