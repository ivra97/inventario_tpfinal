# Sistema de Inventario - Django

Sistema de gestión de inventario desarrollado con Django 5.2, que incluye control de productos, clientes, ventas y autenticación con permisos por grupos.

## Características

- **Productos**: CRUD completo con SKU único, control de stock, stock mínimo y movimientos
- **Clientes**: Gestión de clientes con validación de documento único
- **Ventas**: Sistema de ventas con formsets, descuento automático de stock y registro de movimientos
- **Autenticación**: Django-allauth con login obligatorio y registro deshabilitado
- **Permisos**: 3 grupos de usuarios (administradores, stock, ventas)
- **Interfaz**: Bootstrap 4 con navbar unificado, paginación, iconos y mensajes de feedback

## Requisitos

- Docker
- Docker Compose

## Instalación y Ejecución con Docker

### 1. Clonar el repositorio

```bash
git clone https://github.com/ivra97/inventario_tpfinal.git
cd inventario_tpfinal
```

### 2. Levantar el proyecto con un solo comando

```bash
docker-compose up --build
```

Este comando:
- Construye las imágenes de Docker
- Crea los contenedores para Django y PostgreSQL
- Aplica automáticamente las migraciones (`makemigrations` y `migrate`)
- Crea los grupos de permisos
- Crea un superusuario por defecto: `admin` / `admin123`
- Inicia el servidor en `http://localhost:8000`

### 3. Acceder a la aplicación

Abre tu navegador en: **http://localhost:8000**

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

### 4. Detener los contenedores

```bash
docker-compose down
```

Para eliminar también los volúmenes (base de datos):

```bash
docker-compose down -v
```

## Desarrollo Local (sin Docker)

Si prefieres ejecutar el proyecto localmente:

### 1. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones

```bash
cd inventario
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superusuario

```bash
python manage.py createsuperuser
```

### 5. Crear grupos de permisos

```bash
python manage.py crear_grupos
```

### 6. Ejecutar servidor

```bash
python manage.py runserver
```

Accede a: **http://127.0.0.1:8000**

## Estructura del Proyecto

```
inventario_tpfinal/
├── inventario/                 # Proyecto Django
│   ├── inventario/            # Configuración principal
│   ├── productos/             # App de productos
│   ├── clientes/              # App de clientes
│   ├── ventas/                # App de ventas
│   ├── templates/             # Templates compartidos
│   └── manage.py
├── Dockerfile                 # Configuración Docker
├── docker-compose.yml         # Orquestación de servicios
├── docker-entrypoint.sh       # Script de inicialización
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## Grupos de Permisos

El sistema cuenta con 3 grupos de usuarios:

1. **administradores**: Acceso completo al sistema (68 permisos)
2. **stock**: Gestión de productos y movimientos (8 permisos)
3. **ventas**: Gestión de clientes y ventas (12 permisos)

Los grupos se crean automáticamente al levantar el proyecto con Docker.

## Tecnologías Utilizadas

- **Backend**: Django 5.2.6, Python 3.11
- **Base de Datos**: PostgreSQL 15 (Docker) / SQLite (desarrollo local)
- **Frontend**: Bootstrap 4, Font Awesome, Crispy Forms
- **Autenticación**: Django-allauth
- **Contenedores**: Docker, Docker Compose

## Autor

Ivan - [GitHub](https://github.com/ivra97)

## Licencia

Este proyecto fue desarrollado con fines educativos.
