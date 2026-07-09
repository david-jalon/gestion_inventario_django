import pytest
from django.contrib.auth.models import User, Permission
from inventory.models import Category, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    u = User.objects.create_user(username='testuser', password='testpass123')
    perms = Permission.objects.filter(content_type__app_label='inventory')
    u.user_permissions.set(perms)
    return u


@pytest.fixture
def client_authenticated(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def category():
    return Category.objects.create(name="Electrónicos")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Laptop", category=category, price=15000.00, stock=10,
    )


class TestDashboardView:
    def test_dashboard_status(self, client_authenticated):
        response = client_authenticated.get("/")
        assert response.status_code == 200

    def test_dashboard_shows_cards(self, client_authenticated, category, product):
        response = client_authenticated.get("/")
        content = response.content.decode()
        assert "Total Productos" in content
        assert "Stock Bajo" in content
        assert "Categorías" in content
        assert "Valor Total" in content
        assert "1" in content  # total_products
        assert "1" in content  # total_categories

    def test_dashboard_low_stock_count(self, client_authenticated, category):
        Product.objects.create(name="Mouse", category=category, price=500.00, stock=2, low_stock_threshold=5)
        response = client_authenticated.get("/")
        content = response.content.decode()
        assert "Alertas de Stock" in content


class TestProductListView:
    def test_list_all_products(self, client_authenticated, product):
        response = client_authenticated.get("/productos/")
        assert response.status_code == 200
        assert "Laptop" in response.content.decode()

    def test_list_empty(self, client_authenticated):
        response = client_authenticated.get("/productos/")
        assert response.status_code == 200
        assert "No hay productos registrados" in response.content.decode()

    def test_filter_by_category(self, client_authenticated, category, product):
        other_category = Category.objects.create(name="Ropa")
        Product.objects.create(name="Camiseta", category=other_category, price=200.00)
        response = client_authenticated.get(f"/productos/?category={category.id}")
        content = response.content.decode()
        assert "Laptop" in content
        assert "Camiseta" not in content

    def test_list_shows_low_stock_warning(self, client_authenticated, category):
        Product.objects.create(name="Mouse", category=category, price=500.00, stock=2, low_stock_threshold=5)
        response = client_authenticated.get("/productos/")
        assert "Stock bajo" in response.content.decode()

    def test_list_pagination(self, client_authenticated, category):
        for i in range(25):
            Product.objects.create(name=f"Producto {i}", category=category, price=100.00)
        response = client_authenticated.get("/productos/")
        assert response.status_code == 200
        assert "Página 1 de 2" in response.content.decode()

    def test_list_sorting(self, client_authenticated, category):
        Product.objects.create(name="A", category=category, price=10.00, stock=5)
        Product.objects.create(name="B", category=category, price=20.00, stock=3)
        response = client_authenticated.get("/productos/?sort=name&dir=desc")
        content = response.content.decode()
        a_pos = content.index("A")
        b_pos = content.index("B")
        assert b_pos < a_pos

    def test_search_by_name(self, client_authenticated, category, product):
        Product.objects.create(name="Mouse", category=category, price=500.00)
        response = client_authenticated.get("/productos/?q=laptop")
        content = response.content.decode()
        assert "Laptop" in content
        assert "Mouse" not in content

    def test_search_by_description(self, client_authenticated, category):
        Product.objects.create(name="Teclado", category=category, price=300.00, description="Mecánico RGB")
        response = client_authenticated.get("/productos/?q=mecánico")
        assert "Teclado" in response.content.decode()

    def test_search_no_results(self, client_authenticated):
        response = client_authenticated.get("/productos/?q=zzznotfound")
        assert "No hay productos registrados" in response.content.decode()


class TestProductCreateView:
    def test_create_product_get(self, client_authenticated, category):
        response = client_authenticated.get("/productos/nuevo/")
        assert response.status_code == 200

    def test_create_product_valid(self, client_authenticated, category):
        response = client_authenticated.post("/productos/nuevo/", {
            "name": "Tablet", "category": category.id,
            "price": 8000.00, "stock": 15, "low_stock_threshold": 5,
        }, follow=True)
        assert Product.objects.filter(name="Tablet").exists()
        assert response.status_code == 200

    def test_create_product_missing_name(self, client_authenticated, category):
        response = client_authenticated.post("/productos/nuevo/", {
            "category": category.id, "price": 100.00,
        })
        assert response.status_code == 200
        assert "Este campo es obligatorio" in response.content.decode()
        assert Product.objects.count() == 0

    def test_create_product_invalid_category(self, client_authenticated):
        response = client_authenticated.post("/productos/nuevo/", {
            "name": "Test", "category": 999, "price": 100.00,
        })
        assert response.status_code == 200
        assert 'category' in response.context['form'].errors
        assert Product.objects.count() == 0


class TestProductUpdateView:
    def test_update_product_get(self, client_authenticated, product):
        response = client_authenticated.get(f"/productos/{product.pk}/editar/")
        assert response.status_code == 200

    def test_update_product_valid(self, client_authenticated, product):
        response = client_authenticated.post(f"/productos/{product.pk}/editar/", {
            "name": "Laptop Actualizada", "category": product.category_id,
            "price": 18000.00, "stock": 5,
        }, follow=True)
        product.refresh_from_db()
        assert product.name == "Laptop Actualizada"
        assert product.price == 18000.00
        assert response.status_code == 200

    def test_update_nonexistent_product(self, client_authenticated):
        response = client_authenticated.get("/productos/999/editar/")
        assert response.status_code == 404


class TestProductDeleteView:
    def test_delete_product_get(self, client_authenticated, product):
        response = client_authenticated.get(f"/productos/{product.pk}/eliminar/")
        assert response.status_code == 200
        assert "Laptop" in response.content.decode()

    def test_delete_product_confirm(self, client_authenticated, product):
        response = client_authenticated.post(f"/productos/{product.pk}/eliminar/", follow=True)
        assert not Product.objects.filter(pk=product.pk).exists()
        assert response.status_code == 200

    def test_delete_nonexistent_product(self, client_authenticated):
        response = client_authenticated.post("/productos/999/eliminar/", follow=True)
        assert response.status_code == 404


class TestCategoryListView:
    def test_list_categories(self, client_authenticated, category):
        response = client_authenticated.get("/categorias/")
        assert response.status_code == 200
        assert "Electrónicos" in response.content.decode()

    def test_list_empty(self, client_authenticated):
        response = client_authenticated.get("/categorias/")
        assert response.status_code == 200
        assert "No hay categorías registradas" in response.content.decode()


class TestCategoryCreateView:
    def test_create_category_get(self, client_authenticated):
        response = client_authenticated.get("/categorias/nueva/")
        assert response.status_code == 200

    def test_create_category_valid(self, client_authenticated):
        response = client_authenticated.post("/categorias/nueva/", {
            "name": "Ropa", "description": "Prendas de vestir",
        }, follow=True)
        assert Category.objects.filter(name="Ropa").exists()
        assert response.status_code == 200

    def test_create_category_duplicate(self, client_authenticated, category):
        response = client_authenticated.post("/categorias/nueva/", {
            "name": "Electrónicos",
        })
        assert response.status_code == 200
        assert 'name' in response.context['form'].errors


class TestCategoryUpdateView:
    def test_update_category_get(self, client_authenticated, category):
        response = client_authenticated.get(f"/categorias/{category.pk}/editar/")
        assert response.status_code == 200

    def test_update_category_valid(self, client_authenticated, category):
        response = client_authenticated.post(f"/categorias/{category.pk}/editar/", {
            "name": "Electrodomésticos",
        }, follow=True)
        category.refresh_from_db()
        assert category.name == "Electrodomésticos"

    def test_update_nonexistent_category(self, client_authenticated):
        response = client_authenticated.get("/categorias/999/editar/")
        assert response.status_code == 404


class TestCategoryDeleteView:
    def test_delete_category_confirm(self, client_authenticated, category):
        response = client_authenticated.post(f"/categorias/{category.pk}/eliminar/", follow=True)
        assert not Category.objects.filter(pk=category.pk).exists()
        assert response.status_code == 200

    def test_delete_nonexistent_category(self, client_authenticated):
        response = client_authenticated.post("/categorias/999/eliminar/", follow=True)
        assert response.status_code == 404


class TestProductExportCSV:
    def test_export_csv_success(self, client_authenticated, product):
        response = client_authenticated.get("/productos/exportar/")
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv; charset=utf-8'
        assert 'attachment' in response['Content-Disposition']
        assert 'productos_' in response['Content-Disposition']
        assert '.csv' in response['Content-Disposition']
        content = response.content.decode('utf-8-sig')
        assert 'Nombre' in content
        assert 'Laptop' in content

    def test_export_csv_redirects_anonymous(self, client):
        response = client.get("/productos/exportar/")
        assert response.status_code == 302

    def test_export_csv_empty(self, client_authenticated):
        response = client_authenticated.get("/productos/exportar/")
        content = response.content.decode('utf-8-sig')
        lines = [l for l in content.splitlines() if l]
        assert len(lines) == 1
        assert 'Nombre' in lines[0]

    def test_export_csv_headers_and_bom(self, client_authenticated):
        response = client_authenticated.get("/productos/exportar/")
        raw = response.content
        assert raw[:3] == b'\xef\xbb\xbf'
