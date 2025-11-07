from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from clientes.models import Cliente
from productos.models import Producto
import uuid


class Venta(models.Model):
    """Model definition for Venta."""

    codigo_venta = models.CharField(
        "Código de Venta",
        max_length=50,
        unique=True,
        editable=False,
        help_text="Código único de la venta"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name="Cliente"
    )
    fecha = models.DateTimeField("Fecha de Venta", default=timezone.now)
    total = models.DecimalField(
        "Total",
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total de la venta"
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        """Meta definition for Venta."""
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        """Unicode representation of Venta."""
        return f"Venta {self.codigo_venta} - {self.cliente.nombre_completo}"
    
    def save(self, *args, **kwargs):
        """Genera el código de venta si no existe."""
        if not self.codigo_venta:
            # Genera un código único basado en timestamp
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_part = str(uuid.uuid4())[:8].upper()
            self.codigo_venta = f"V-{timestamp}-{random_part}"
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula el total de la venta sumando todos los items."""
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save()
        return total


class ItemVenta(models.Model):
    """Model definition for ItemVenta."""

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Venta"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    cantidad = models.IntegerField("Cantidad", default=1)
    precio_unitario = models.DecimalField(
        "Precio Unitario",
        max_digits=10,
        decimal_places=2,
        help_text="Precio del producto al momento de la venta"
    )
    subtotal = models.DecimalField(
        "Subtotal",
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        """Meta definition for ItemVenta."""
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'
        ordering = ['id']

    def __str__(self):
        """Unicode representation of ItemVenta."""
        return f"{self.producto.nombre} x {self.cantidad}"
    
    def clean(self):
        """Valida que haya stock suficiente."""
        if self.cantidad and self.producto:
            if self.cantidad <= 0:
                raise ValidationError("La cantidad debe ser mayor a 0")
            if self.producto.stock < self.cantidad:
                raise ValidationError(
                    f"Stock insuficiente. Disponible: {self.producto.stock}, Solicitado: {self.cantidad}"
                )
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente."""
        if self.precio_unitario and self.cantidad:
            self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
