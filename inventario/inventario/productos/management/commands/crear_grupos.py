from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from productos.models import Producto, MovimientoStock
from clientes.models import Cliente
from ventas.models import Venta, ItemVenta


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios con sus permisos correspondientes'

    def handle(self, *args, **kwargs):
        # Obtener los content types
        producto_ct = ContentType.objects.get_for_model(Producto)
        movimiento_ct = ContentType.objects.get_for_model(MovimientoStock)
        cliente_ct = ContentType.objects.get_for_model(Cliente)
        venta_ct = ContentType.objects.get_for_model(Venta)
        itemventa_ct = ContentType.objects.get_for_model(ItemVenta)

        # ==================== GRUPO ADMINISTRADORES ====================
        administradores, created = Group.objects.get_or_create(name='administradores')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "administradores" creado'))
        else:
            self.stdout.write(self.style.WARNING('→ Grupo "administradores" ya existe'))
        
        # Dar todos los permisos a administradores
        all_permissions = Permission.objects.all()
        administradores.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {all_permissions.count()} permisos a administradores'))

        # ==================== GRUPO STOCK ====================
        stock, created = Group.objects.get_or_create(name='stock')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "stock" creado'))
        else:
            self.stdout.write(self.style.WARNING('→ Grupo "stock" ya existe'))
        
        # Permisos para stock (productos y movimientos)
        stock_permissions = Permission.objects.filter(
            content_type__in=[producto_ct, movimiento_ct]
        )
        stock.permissions.set(stock_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {stock_permissions.count()} permisos a stock'))

        # ==================== GRUPO VENTAS ====================
        ventas_group, created = Group.objects.get_or_create(name='ventas')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "ventas" creado'))
        else:
            self.stdout.write(self.style.WARNING('→ Grupo "ventas" ya existe'))
        
        # Permisos para ventas (clientes, ventas e items de venta)
        ventas_permissions = Permission.objects.filter(
            content_type__in=[cliente_ct, venta_ct, itemventa_ct]
        )
        ventas_group.permissions.set(ventas_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {ventas_permissions.count()} permisos a ventas'))

        self.stdout.write(self.style.SUCCESS('\n✓ Grupos y permisos configurados correctamente'))
        self.stdout.write(self.style.SUCCESS('\nResumen:'))
        self.stdout.write(f'  • administradores: acceso completo al sistema')
        self.stdout.write(f'  • stock: gestión de productos y movimientos')
        self.stdout.write(f'  • ventas: gestión de clientes y ventas')
