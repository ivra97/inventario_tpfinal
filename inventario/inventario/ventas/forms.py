from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Venta, ItemVenta
from clientes.models import Cliente
from productos.models import Producto
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div, HTML
from crispy_forms.bootstrap import FormActions


class VentaForm(forms.ModelForm):
    """Formulario para la cabecera de la venta."""
    
    class Meta:
        model = Venta
        fields = ['cliente', 'fecha']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        
        # Configurar el campo fecha con valor inicial
        if not self.instance.pk:
            from django.utils import timezone
            initial_date = timezone.now().strftime('%Y-%m-%dT%H:%M')
            self.fields['fecha'].initial = initial_date
        
        self.helper.layout = Layout(
            Row(
                Column(Field('cliente'), css_class='col-md-6'),
                Column(Field('fecha'), css_class='col-md-6'),
            )
        )


class ItemVentaForm(forms.ModelForm):
    """Formulario para cada item de venta."""
    
    class Meta:
        model = ItemVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 1, 'class': 'cantidad-item'}),
            'precio_unitario': forms.NumberInput(attrs={'step': '0.01', 'class': 'precio-item', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].widget.attrs.update({'class': 'producto-select'})
        # Añadir atributos data para facilitar el cálculo con JavaScript
        self.fields['producto'].queryset = Producto.objects.filter(stock__gt=0).order_by('nombre')
    
    def clean_cantidad(self):
        """Valida que la cantidad sea positiva y que haya stock."""
        cantidad = self.cleaned_data.get('cantidad')
        producto = self.cleaned_data.get('producto')
        
        if cantidad and cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")
        
        if producto and cantidad:
            if producto.stock < cantidad:
                raise ValidationError(
                    f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                )
        
        return cantidad


# Crear el formset para los items de venta
ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,  # Número de formularios vacíos a mostrar
    can_delete=True,
    min_num=1,  # Mínimo 1 item
    validate_min=True,
)
