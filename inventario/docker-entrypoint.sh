#!/bin/bash

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté disponible..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL está listo."

# Ejecutar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario si no existe (opcional)
echo "Verificando superusuario..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin / admin123')
else:
    print('Superusuario ya existe')
END

# Crear grupos de permisos
echo "Creando grupos de permisos..."
python manage.py crear_grupos

# Iniciar el servidor Django
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000
