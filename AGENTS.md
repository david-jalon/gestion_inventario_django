# Gestión de Inventario

Sistema Django para gestión de inventario con CRUD de productos, filtrado por categoría y alertas de stock bajo. Orientado a pequeños negocios.

## Stack
- Lenguaje: Python 3.12+
- Framework: Django 5.2
- Base de datos: SQLite3 (con psycopg2-binary listo para PostgreSQL)
- Tests: pytest + pytest-django
- Type checking: mypy
- Variables de entorno: python-decouple

## Comandos
- `python manage.py runserver` — arranca el servidor en local
- `pytest` — ejecuta los tests (deben pasar antes de cada commit)
- `mypy .` — type checking
- `python manage.py makemigrations` + `python manage.py migrate` — aplicar migraciones

## Estructura del proyecto
- `config/` — configuración del proyecto (settings, urls raíz, wsgi, asgi)
- `inventory/` — app principal (modelos Category y Product, vistas, tests, admin)
- `users/` — app esqueleto para autenticación (pendiente de implementar)
- `templates/` — templates HTML con Tailwind CSS vía CDN
- `.opencode/` — configuración de opencode (skills)

## Convenciones
- `snake_case` para variables, funciones y archivos Python.
- Tests con pytest dentro de `inventory/tests/` en archivos `test_*.py`.
- Function-Based Views con `render`, `redirect`, `get_object_or_404`.
- Manejo manual de `request.POST` (sin ModelForms aún).
- Mensajes flash con `django.contrib.messages`.
- Templates extienden `base.html` y usan clases utilitarias de Tailwind.

## No hagas
- No instalar dependencias sin avisar y actualizar `requirements.txt`.
- No editar migraciones a mano — siempre `makemigrations` + `migrate`.
- No subir archivos `.env*` al repositorio (están en `.gitignore`).
- No modificar `.venv/`, `__pycache__/`, `node_modules/`.

## Flujo de trabajo
- Antes de una tarea no trivial, propón un plan y espera mi OK.
- Una tarea a la vez; al terminar, dime qué cambiaste para que lo revise.
- Si no estás seguro al 80%, pregunta. No inventes.

## Documentación
- `ROADMAP.md` — plan de desarrollo por fases
- `.opencode/skills/frontend-design/SKILL.md` — guía de diseño visual
