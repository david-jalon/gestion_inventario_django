# Roadmap — Gestión de Inventario

> Proyecto Django para gestión de inventario con CRUD de productos, filtrado por categoría y alertas de stock bajo.

---

## ✅ Fase 1 — Setup inicial
- [x] Crear proyecto Django (`django-admin startproject`)
- [x] Configurar variables de entorno con `python-decouple`
- [x] Configurar `.gitignore`
- [x] Configurar `.env.example`

## ✅ Fase 2 — Modelos y base de datos
- [x] Modelo `Category` (name, description, timestamps)
- [x] Modelo `Product` (name, description, category FK, price, stock, low_stock_threshold, timestamps)
- [x] Propiedad `is_low_stock`
- [x] Migración inicial aplicada
- [x] Registro en admin

## ✅ Fase 3 — Vistas y templates
- [x] Vista `product_list` con filtro por categoría
- [x] Vista `product_create`
- [x] Vista `product_update`
- [x] Vista `product_delete`
- [x] Templates con Tailwind CSS (base, list, form, confirm)
- [x] Mensajes flash (success/error)
- [x] Filtro por categoría en la URL

## ✅ Fase 4 — Testing
- [x] Tests de modelos (creación, validación, unicidad, relaciones, cascade delete, low_stock)
- [x] Tests de vistas (listado, filtro, CRUD, casos borde: 404, datos faltantes)
- [x] Configuración de pytest y mypy
- [x] 25 tests pasando al 100%

---

## 🎨 Fase 5 — Mejoras visuales ✅

- [x] **Dashboard con cards de resumen** — Página principal con cards: total productos, stock bajo, categorías, valor total del inventario
- [x] **UI más pulida** — Botones con iconos (Heroicons), badges de estado, sombras, transiciones hover
- [x] **Tabla responsive** — `overflow-x-auto` + columnas con ancho mínimo en mobile
- [x] **Paginación** — Paginar productos de 20 en 20
- [x] **Mensajes toast con auto-dismiss** — Mensajes success/error que desaparecen tras 3s (JS vanilla)
- [x] **Modal de confirmación** — Eliminar producto desde un modal en vez de página aparte
- [x] **Ordenar columnas** — Click en headers (nombre, precio, stock) para ordenar ascendente/descendente
- [x] **Empty state ilustrado** — Mensaje visual cuando no hay productos con icono y CTA

## ✅ Fase 6 — Funcionalidades core

- [x] **CRUD de Categorías** — Vistas, templates, URLs y tests para gestionar categorías desde la UI
- [x] **Django ModelForms** — `ProductForm`, `CategoryForm`, `StockMovementForm` con validación y widgets
- [x] **Autenticación (app `users`)** — Login, logout, registro, `@login_required` en todas las vistas, templates
- [x] **Búsqueda por nombre** — Campo de búsqueda que filtra productos por nombre o descripción
- [x] **Historial de movimientos de stock** — Modelo `StockMovement`, señal automática, vistas y templates

## 👥 Fase 7 — Gestión de usuarios y permisos

- [ ] **Perfil de usuario** — Cambiar contraseña (`PasswordChangeView`), editar nombre y email
- [ ] **Admin de usuarios (solo superuser)** — Listar, crear, editar, activar/desactivar staff
- [ ] **Grupos predefinidos** — Administradores, Editores, Visualizadores con permisos específicos
- [ ] **Adaptar vistas y templates** — Ocultar botones y acciones según permisos del usuario
- [ ] **Enlace "Mi Perfil" y "Administrar Usuarios"** en navbar (según rol)

## 🚀 Fase 8 — Extras

- [ ] **Exportar a CSV** — Botón para descargar listado de productos como CSV
- [ ] **API REST (DRF)** — Endpoints con Django Rest Framework para productos y categorías
- [ ] **Notificaciones persistentes** — Banner fijo en la navbar si hay productos con stock bajo

---

> **Leyenda:** ✅ Completado | 🎨 Visual | ⚙️ Funcional | 👥 Usuarios | 🚀 Extra
