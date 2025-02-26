from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    # Si tu modelo de usuario es Lector, puedes acceder a la propiedad 'es_escritor'
    if user.groups.filter(name="Escritor").exists():
        # Renderiza el perfil de escritor
        return render(request, 'perfil/escritor_profile.html', {'user': user})
    else:
        # Renderiza el perfil de lector
        return render(request, 'perfil/lector_profile.html', {'user': user})
