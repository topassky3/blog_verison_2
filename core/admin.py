from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Lector

@admin.register(Lector)
class LectorAdmin(UserAdmin):
    list_display = ('username', 'email', 'telefono', 'email_confirmado', 'display_role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telefono', 'email_confirmado')}),
    )
    actions = ['make_escritor', 'make_lector']

    def display_role(self, obj):
        return "Escritor" if obj.es_escritor else "Lector"
    display_role.short_description = "Rol"

    def make_escritor(self, request, queryset):
        """Acción para asignar el grupo 'Escritor' a los usuarios seleccionados."""
        group, created = Group.objects.get_or_create(name='Escritor')
        for user in queryset:
            user.groups.add(group)
        self.message_user(request, "Los usuarios seleccionados han sido marcados como Escritor.")
    make_escritor.short_description = "Marcar como Escritor"

    def make_lector(self, request, queryset):
        """Acción para quitar el grupo 'Escritor' y dejar a los usuarios como Lector."""
        group = Group.objects.filter(name='Escritor').first()
        if group:
            for user in queryset:
                user.groups.remove(group)
        self.message_user(request, "Los usuarios seleccionados han sido marcados como Lector.")
    make_lector.short_description = "Marcar como Lector"

from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # En el formulario de edición se mostrarán "name" y "slug",
    # mientras que en el de creación solo se mostrará "name"
    def get_fields(self, request, obj=None):
        if obj:
            return ('name', 'slug')
        return ('name',)

    # Prepopula "slug" solo en el formulario de edición
    def get_prepopulated_fields(self, request, obj=None):
        if obj:
            return {"slug": ("name",)}
        return {}

    # Como en el formulario de edición queremos que "slug" no se edite, lo marcamos como readonly
    readonly_fields = ('slug',)

    list_display = ('name', 'slug')


from django.contrib import admin
from .models import PodcastCategory

from django.contrib import admin
from .models import PodcastCategory


@admin.register(PodcastCategory)
class PodcastCategoryAdmin(admin.ModelAdmin):
    # Oculta el campo slug en el formulario del admin
    exclude = ('slug',)

    # En la lista, mostramos name y slug (opcional)
    list_display = ('name', 'slug')
