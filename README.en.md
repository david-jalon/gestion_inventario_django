# Inventory Management

> Web-based inventory management system for small businesses.  
> Product CRUD, stock control, movement history, user permissions, REST API, dark mode.

## ✨ Features

- **Dashboard** with summary cards for totals, low stock, inventory value, and latest products
- **Product CRUD** with search, category filter, sorting, and pagination
- **Category CRUD**
- **Stock movement history** (entries/exits) with automatic signal on product create/edit
- **Low stock alerts** — Persistent banner across the app + highlighted rows
- **Authentication** — Login, register, logout
- **User profile** — Edit name/email, change password
- **User administration** (superuser) — Create, edit, activate/deactivate, delete, assign groups and permissions
- **Roles & permissions** — Predefined groups (Administrators, Editors, Viewers) with `require_permission` decorator
- **REST API** — Full endpoints with search, filters, and pagination (Django REST Framework)
- **CSV export** — Download product list with timestamp in filename
- **Company settings** — Customizable company name, logo, and currency symbol
- **Dark mode** — Toggle button with `localStorage` persistence, respects system preference, no flash

## 🛠️ Tech Stack

| Technology | Version |
|---|---|
| Python | 3.12+ |
| Django | 5.2 |
| Django REST Framework | 3.17 |
| django-filter | 25.1 |
| SQLite3 (production-ready with psycopg2) | — |
| Tailwind CSS | via CDN (`darkMode: class`) |
| pytest + pytest-django | 8.x / 4.x |
| mypy | — |
| python-decouple | 3.8 |

## 🚀 Installation

```bash
git clone https://github.com/yourusername/inventory-management.git
cd inventory-management

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
```

Edit `.env` and set `DJANGO_SECRET_KEY`. Generate one with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# Database
python manage.py migrate

# (Optional) Create predefined groups and permissions
python manage.py seed_groups

# Create a superuser (access /admin/ and /usuarios/)
python manage.py createsuperuser

# Development server
python manage.py runserver
```

Open `http://localhost:8000/` in your browser.

## ⚙️ Configuration

### Environment variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | (required) |
| `DJANGO_DEBUG` | Debug mode | `True` |

### UI configuration

Logged in as superuser, go to `/configuracion/` (gear icon ⚙️ in navbar) to set:
- Company name (displayed in navbar and page title)
- Logo (image upload)
- Currency symbol (replaces `$` in dashboard and products)

## 📋 Main routes

| Route | Description | Permission |
|---|---|---|
| `/` | Dashboard | Authenticated |
| `/productos/` | Product list | Authenticated |
| `/productos/nuevo/` | Create product | `inventory.add_product` |
| `/productos/exportar/` | Export CSV | Authenticated |
| `/productos/<id>/editar/` | Edit product | `inventory.change_product` |
| `/productos/<id>/eliminar/` | Delete product | `inventory.delete_product` |
| `/productos/<id>/movimientos/` | Stock history | Authenticated |
| `/categorias/` | Category list | Authenticated |
| `/configuracion/` | Company settings | Superuser |
| `/usuarios/` | User admin | Superuser |
| `/perfil/editar/` | Edit profile | Authenticated |
| `/perfil/cambiar-contrasena/` | Change password | Authenticated |
| `/login/` | Sign in | Anonymous |
| `/registro/` | Sign up | Anonymous |

## 📡 REST API

Endpoints available at `/api/` (authentication required via session or Basic Auth):

| Endpoint | Methods | Description |
|---|---|---|
| `/api/productos/` | GET, POST | List/create products |
| `/api/productos/<id>/` | GET, PUT, PATCH, DELETE | Retrieve/update/delete |
| `/api/categorias/` | GET, POST | List/create categories |
| `/api/categorias/<id>/` | GET, PUT, PATCH, DELETE | Retrieve/update/delete |

**Query parameters:**
- `?category=1` — Filter by category
- `?search=laptop` — Search by name/description
- `?ordering=price` — Sort (prefix with `-` for descending)
- Pagination: 20 results per page

## 📁 Project structure

```
.
├── config/             # Django configuration (settings, urls, wsgi)
├── inventory/          # Main app
│   ├── api.py          # DRF ViewSets
│   ├── api_urls.py     # API routes
│   ├── context_processors.py
│   ├── forms.py        # ModelForms
│   ├── models.py       # Category, Product, StockMovement, CompanySettings
│   ├── serializers.py  # DRF serializers
│   ├── urls.py         # App routes
│   ├── views.py        # Function-Based Views
│   ├── management/commands/  # Custom commands (seed_groups)
│   └── tests/          # Tests (132 tests)
├── users/              # Authentication and profiles app
├── templates/          # HTML templates with Tailwind CSS
│   ├── base.html
│   ├── inventory/
│   ├── registration/
│   └── users/
├── media/              # Uploaded files (logos)
├── manage.py
├── requirements.txt
└── ROADMAP.md
```

## 🧪 Tests

```bash
pytest              # Run all tests (132)
pytest -v           # Verbose mode
pytest -k "api"     # Filter by name
```

Type checking:

```bash
mypy .
```

## 📄 License

MIT
