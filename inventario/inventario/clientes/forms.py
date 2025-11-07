from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Reset, ButtonHolder, Field, HTML
from crispy_forms.bootstrap import PrependedText


class ClienteForm(forms.ModelForm):
    """
    Formulario para la creación y edición de clientes.
    """
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'numero_documento', 'email', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'numero_documento': 'Debe ser único para cada cliente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Row(
                Column(Field('nombre'), css_class='col-md-6'),
                Column(Field('apellido'), css_class='col-md-6'),
            ),
            Field('numero_documento'),
            Row(
                Column(PrependedText('email', '@'), css_class='col-md-6'),
                Column(PrependedText('telefono', '<i class="fas fa-phone"></i>'), css_class='col-md-6'),
            ),
            Field('direccion'),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn btn-success'),
                Reset('reset', 'Limpiar', css_class='btn btn-outline-secondary'),
                HTML('<a href="{% url \'clientes:cliente_list\' %}" class="btn btn-secondary">Cancelar</a>')
            )
        )

    def clean_numero_documento(self):
        """Valida que el número de documento no esté vacío y sea único."""
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            numero_documento = numero_documento.strip()
            if not numero_documento:
                raise ValidationError("El número de documento no puede estar vacío")
            
            # Validar unicidad solo si es un nuevo cliente o si cambió el documento
            if self.instance.pk:
                # Es una edición
                if Cliente.objects.exclude(pk=self.instance.pk).filter(numero_documento=numero_documento).exists():
                    raise ValidationError("Ya existe un cliente con este número de documento")
            else:
                # Es una creación
                if Cliente.objects.filter(numero_documento=numero_documento).exists():
                    raise ValidationError("Ya existe un cliente con este número de documento")
        
        return numero_documento

    def clean_email(self):
        """Normaliza el email a minúsculas."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email
    
    def clean_telefono(self):
        """Limpia espacios del teléfono."""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
        return telefono
