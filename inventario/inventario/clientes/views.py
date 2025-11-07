from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm


class ClienteListView(ListView):
    """Muestra una lista de todos los clientes."""
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        """Permite búsqueda por nombre, apellido o documento."""
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(numero_documento__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('apellido', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ClienteDetailView(DetailView):
    """Muestra los detalles de un cliente específico."""
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"


class ClienteCreateView(CreateView):
    """Vista para crear un nuevo cliente."""
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Cliente {self.object.nombre_completo} creado exitosamente")
        return response


class ClienteUpdateView(UpdateView):
    """Vista para actualizar un cliente existente."""
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Cliente {self.object.nombre_completo} actualizado exitosamente")
        return response


class ClienteDeleteView(DeleteView):
    """Vista para eliminar un cliente."""
    model = Cliente
    template_name = "clientes/cliente_confirm_delete.html"
    success_url = reverse_lazy("clientes:cliente_list")

    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()
        messages.success(self.request, f"Cliente {cliente.nombre_completo} eliminado exitosamente")
        return super().delete(request, *args, **kwargs)
