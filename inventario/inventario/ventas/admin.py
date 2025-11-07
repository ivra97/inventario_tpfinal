from django.contrib import admin
from .models import Venta, ItemVenta


class ItemVentaInline(admin.TabularInline):
    """Inline para mostrar items dentro de la venta."""
    model = ItemVenta
    extra = 1
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['codigo_venta', 'cliente', 'fecha', 'total', 'fecha_creacion']
    list_filter = ['fecha', 'fecha_creacion']
    search_fields = ['codigo_venta', 'cliente__nombre', 'cliente__apellido']
    readonly_fields = ['codigo_venta', 'total', 'fecha_creacion']
    date_hierarchy = 'fecha'
    inlines = [ItemVentaInline]
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('codigo_venta', 'cliente', 'fecha')
        }),
        ('Totales', {
            'fields': ('total',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha']
    search_fields = ['venta__codigo_venta', 'producto__nombre']
    readonly_fields = ['subtotal']
