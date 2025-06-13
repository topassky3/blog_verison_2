from django.urls import path
from .views import AuthorProfileView

# Este nombre de app ayuda a Django a organizar las URLs
app_name = 'leer_perfil'

urlpatterns = [
    # Usamos <int:pk> porque es el estándar de Django para DetailView
    # y hace que la vista sea más simple.
    path('<int:pk>/', AuthorProfileView.as_view(), name='author_profile'),
]