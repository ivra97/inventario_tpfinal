from django.db import models
from django.core.validators import EmailValidator, RegexValidator

# Create your models here.

class Cliente(models.Model):
    """Model definition for Cliente."""

    nombre = models.CharField("Nombre", max_length=100)
    apellido = models.CharField("Apellido", max_length=100)
    numero_documento = models.CharField(
        "Número de Documento",
        max_length=20,
        unique=True,
        help_text="Número de documento único del cliente"
    )
    email = models.EmailField(
        "E-mail",
        max_length=254,
        validators=[EmailValidator()],
        help_text="Correo electrónico del cliente"
    )
    telefono = models.CharField(
        "Teléfono",
        max_length=20,
        help_text="Número de teléfono de contacto"
    )
    direccion = models.TextField(
        "Dirección",
        max_length=300,
        help_text="Dirección completa del cliente"
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        """Meta definition for Cliente."""

        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        """Unicode representation of Cliente."""
        return f"{self.apellido}, {self.nombre}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente."""
        return f"{self.nombre} {self.apellido}"
