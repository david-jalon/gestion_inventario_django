# Gestión de Inventario

> Sistema web para la gestión de inventario de pequeños negocios.  
> CRUD de productos, control de stock, historial de movimientos, usuarios con permisos, API REST, modo oscuro.

## ✨ Funcionalidades

- **Dashboard** con cards de totales, stock bajo, valor del inventario y últimos productos
- **CRUD de productos** con búsqueda, filtro por categoría, ordenamiento y paginación
- **CRUD de categorías**
- **Historial de movimientos de stock** (entradas/salidas) con señal automática al crear/editar productos
- **Alertas de stock bajo** — Banner persistente en toda la app + columna resaltada
- **Autenticación** — Login, registro, logout
- **Perfil de usuario** — Editar nombre/email, cambiar contraseña
- **Admin de usuarios** (superuser) — Crear, editar, activar/desactivar, eliminar, asignar grupos y permisos
- **Roles y permisos** — Grupos predefinidos (Administradores, Editores, Visualizadores) con decorador `require_permission`
- **API REST** — Endpoints completos con búsqueda, filtros y paginación (Django REST Framework)
- **Exportar a CSV** — Descarga del listado de productos con fecha/hora en el nombre
- **Configuración de empresa** — Nombre, logo y símbolo de moneda personalizables
- **Modo oscuro** — Toggle con persistencia en `localStorage`, respeta preferencia del sistema, sin flash

## 🛠️ Stack

| Tecnología | Versión |
|---|---|
| Python | 3.12+ |
| Django | 5.2 |
| Django REST Framework | 3.17 |
| django-filter | 25.1 |
| SQLite3 (producción-ready con psycopg2) | — |
| Tailwind CSS | vía CDN (`darkMode: class`) |
| pytest + pytest-django | 8.x / 4.x |
| mypy | — |
| python-decouple | 3.8 |

## 🚀 Instalación

```bash
git clone https://github.com/tuusuario/gestion-inventario.git
cd gestion-inventario

# Entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env
```

Edita `.env` con `DJANGO_SECRET_KEY`. Puedes generar una con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# Base de datos
python manage.py migrate

# (Opcional) Crea grupos y permisos predefinidos
python manage.py seed_groups

# Crea un superusuario (accede a /admin/ y /usuarios/)
python manage.py createsuperuser

# Servidor de desarrollo
python manage.py runserver
```

Accede a `http://localhost:8000/`.

## ⚙️ Configuración

### Variables de entorno (`.env`)

| Variable | Descripción | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django | (requerida) |
| `DJANGO_DEBUG` | Modo debug | `True` |

### Configuración desde la UI

Con sesión de superusuario, ve a `/configuracion/` (icono ⚙️ en navbar) para:
- Nombre de la empresa (se muestra en navbar y título)
- Logo (subida de imagen)
- Símbolo de moneda (se reemplaza en dashboard y productos)

## 📋 Rutas principales

| Ruta | Descripción | Permiso |
|---|---|---|
| `/` | Dashboard | Authenticated |
| `/productos/` | Lista de productos | Authenticated |
| `/productos/nuevo/` | Crear producto | `inventory.add_product` |
| `/productos/exportar/` | Exportar CSV | Authenticated |
| `/productos/<id>/editar/` | Editar producto | `inventory.change_product` |
| `/productos/<id>/eliminar/` | Eliminar producto | `inventory.delete_product` |
| `/productos/<id>/movimientos/` | Historial de stock | Authenticated |
| `/categorias/` | Lista de categorías | Authenticated |
| `/configuracion/` | Config. empresa | Superuser |
| `/usuarios/` | Admin usuarios | Superuser |
| `/perfil/editar/` | Editar perfil | Authenticated |
| `/perfil/cambiar-contrasena/` | Cambiar contraseña | Authenticated |
| `/login/` | Iniciar sesión | Anonymous |
| `/registro/` | Registrarse | Anonymous |

## 📡 API REST

Endpoints disponibles en `/api/` (requieren autenticación vía sesión o Basic Auth):

| Endpoint | Métodos | Descripción |
|---|---|---|
| `/api/productos/` | GET, POST | Listar/crear productos |
| `/api/productos/<id>/` | GET, PUT, PATCH, DELETE | Detalle/editar/eliminar |
| `/api/categorias/` | GET, POST | Listar/crear categorías |
| `/api/categorias/<id>/` | GET, PUT, PATCH, DELETE | Detalle/editar/eliminar |

**Parámetros de consulta:**
- `?category=1` — Filtrar por categoría
- `?search=laptop` — Búsqueda por nombre/descripción
- `?ordering=price` — Ordenar (precede con `-` para descendente)
- Paginación: 20 resultados por página

## 📁 Estructura del proyecto

```
.
├── config/             # Configuración de Django (settings, urls, wsgi)
├── inventory/          # App principal
│   ├── api.py          # ViewSets DRF
│   ├── api_urls.py     # Rutas de la API
│   ├── context_processors.py
│   ├── forms.py        # ModelForms
│   ├── models.py       # Category, Product, StockMovement, CompanySettings
│   ├── serializers.py  # DRF serializers
│   ├── urls.py         # Rutas de la app
│   ├── views.py        # Function-Based Views
│   ├── management/commands/  # Comandos personalizados (seed_groups)
│   └── tests/          # Tests (132 tests)
├── users/              # App de autenticación y perfiles
├── templates/          # Templates HTML con Tailwind CSS
│   ├── base.html
│   ├── inventory/
│   ├── registration/
│   └── users/
├── media/              # Archivos subidos (logos)
├── manage.py
├── requirements.txt
└── ROADMAP.md
```

## 🧪 Tests

```bash
pytest              # Todos los tests (132)
pytest -v           # Modo verbose
pytest -k "api"     # Filtrar por nombre
```

Type checking:

```bash
mypy .
```

## 📄 Licencia

MIT
