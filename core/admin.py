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
