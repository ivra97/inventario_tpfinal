from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['numero_documento', 'apellido', 'nombre', 'email', 'telefono']
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'apellido', 'numero_documento', 'email']
    ordering = ['apellido', 'nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'numero_documento')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'telefono', 'direccion')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
