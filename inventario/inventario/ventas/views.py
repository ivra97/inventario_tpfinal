from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from xhtml2pdf import pisa
from io import BytesIO
from datetime import timedelta
from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaFormSet
from productos.models import MovimientoStock


class VentaListView(LoginRequiredMixin, ListView):
    """Muestra una lista de todas las ventas."""
    model = Venta
    template_name = "ventas/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 10

    def get_queryset(self):
        """Ordena por fecha descendente."""
        return Venta.objects.select_related('cliente').order_by('-fecha')


class VentaDetailView(LoginRequiredMixin, DetailView):
    """Muestra los detalles de una venta con sus items."""
    model = Venta
    template_name = "ventas/venta_detail.html"
    context_object_name = "venta"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('producto').all()
        return context


class VentaCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear una nueva venta con items."""
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemVentaFormSet(self.request.POST, instance=self.object)
        else:
            # En GET, si es una nueva venta, no pasar instance
            context['formset'] = ItemVentaFormSet()
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Procesa el formulario de venta y el formset de items."""
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            # Guardar la venta
            self.object = form.save(commit=False)
            self.object.save()

            # Guardar los items
            formset.instance = self.object
            items = formset.save(commit=False)

            total_venta = 0

            # Procesar cada item
            for item in items:
                # Obtener el precio actual del producto
                item.precio_unitario = item.producto.precio
                item.subtotal = item.cantidad * item.precio_unitario
                
                # Validar stock
                if item.producto.stock < item.cantidad:
                    messages.error(
                        self.request,
                        f"Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.stock}"
                    )
                    transaction.set_rollback(True)
                    return self.form_invalid(form)
                
                # Descontar stock
                item.producto.stock -= item.cantidad
                item.producto.save()

                # Registrar movimiento de stock
                MovimientoStock.objects.create(
                    producto=item.producto,
                    tipo='salida',
                    cantidad=item.cantidad,
                    motivo=f'Venta {self.object.codigo_venta}',
                    fecha=timezone.now(),
                    usuario=self.request.user.username if self.request.user.is_authenticated else 'Sistema'
                )

                # Guardar el item
                item.save()
                
                # Acumular total
                total_venta += item.subtotal

            # Procesar items marcados para eliminación
            for item in formset.deleted_objects:
                item.delete()

            # Actualizar el total de la venta
            self.object.total = total_venta
            self.object.save()

            messages.success(
                self.request,
                f"Venta {self.object.codigo_venta} creada exitosamente. Total: ${total_venta}"
            )
            return redirect(self.success_url)
        else:
            # El formset tiene errores
            messages.error(self.request, "Por favor corrija los errores en los items de la venta")
            return self.form_invalid(form)


def generar_pdf_venta(request, pk):
    """Genera un PDF del comprobante de venta."""
    venta = get_object_or_404(Venta, pk=pk)
    items = venta.items.select_related('producto').all()
    
    # Renderizar el template HTML
    html_string = render_to_string('ventas/comprobante_pdf.html', {
        'venta': venta,
        'items': items,
        'fecha_actual': timezone.now()
    })
    
    # Crear el PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        # Crear respuesta HTTP con el PDF
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobante_venta_{venta.codigo_venta}.pdf"'
        return response
    
    return HttpResponse('Error al generar PDF', status=500)


def dashboard_ventas(request):
    """Dashboard con gráfico de ventas por día."""
    # Obtener ventas de los últimos 30 días
    fecha_inicio = timezone.now() - timedelta(days=30)
    
    ventas_por_dia = Venta.objects.filter(
        fecha__gte=fecha_inicio
    ).annotate(
        dia=TruncDate('fecha')
    ).values('dia').annotate(
        total_dia=Sum('total'),
        cantidad_ventas=Count('id')
    ).order_by('dia')
    
    # Preparar datos para Chart.js
    labels = [v['dia'].strftime('%d/%m') for v in ventas_por_dia]
    totales = [float(v['total_dia']) for v in ventas_por_dia]
    cantidades = [v['cantidad_ventas'] for v in ventas_por_dia]
    
    # Estadísticas generales
    total_ventas = Venta.objects.filter(fecha__gte=fecha_inicio).aggregate(
        total=Sum('total'),
        cantidad=Count('id')
    )
    
    context = {
        'labels': labels,
        'totales': totales,
        'cantidades': cantidades,
        'total_mes': total_ventas['total'] or 0,
        'cantidad_mes': total_ventas['cantidad'] or 0,
        'promedio_venta': (total_ventas['total'] / total_ventas['cantidad']) if total_ventas['cantidad'] else 0
    }
    
    return render(request, 'ventas/dashboard.html', context)
