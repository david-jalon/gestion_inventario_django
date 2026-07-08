import pytest
from inventory.models import Category, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Electrónicos")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Laptop", category=category, price=15000.00, stock=10,
    )


class TestProductListView:
    def test_list_all_products(self, client, product):
        response = client.get("/")
        assert response.status_code == 200
        assert "Laptop" in response.content.decode()

    def test_list_empty(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "No hay productos registrados" in response.content.decode()

    def test_filter_by_category(self, client, category, product):
        other_category = Category.objects.create(name="Ropa")
        Product.objects.create(name="Camiseta", category=other_category, price=200.00)
        response = client.get(f"/?category={category.id}")
        content = response.content.decode()
        assert "Laptop" in content
        assert "Camiseta" not in content

    def test_list_shows_low_stock_warning(self, client, category):
        Product.objects.create(name="Mouse", category=category, price=500.00, stock=2, low_stock_threshold=5)
        response = client.get("/")
        assert "Stock bajo" in response.content.decode()


class TestProductCreateView:
    def test_create_product_get(self, client, category):
        response = client.get("/nuevo/")
        assert response.status_code == 200

    def test_create_product_valid(self, client, category):
        response = client.post("/nuevo/", {
            "name": "Tablet", "category": category.id,
            "price": 8000.00, "stock": 15, "low_stock_threshold": 5,
        }, follow=True)
        assert Product.objects.filter(name="Tablet").exists()
        assert response.status_code == 200

    def test_create_product_missing_name(self, client, category):
        response = client.post("/nuevo/", {
            "category": category.id, "price": 100.00,
        })
        assert response.status_code == 200
        assert "Nombre, categoría y precio son obligatorios" in response.content.decode()
        assert Product.objects.count() == 0

    def test_create_product_invalid_category(self, client):
        response = client.post("/nuevo/", {
            "name": "Test", "category": 999, "price": 100.00,
        })
        assert response.status_code == 404


class TestProductUpdateView:
    def test_update_product_get(self, client, product):
        response = client.get(f"/{product.pk}/editar/")
        assert response.status_code == 200

    def test_update_product_valid(self, client, product):
        response = client.post(f"/{product.pk}/editar/", {
            "name": "Laptop Actualizada", "category": product.category_id,
            "price": 18000.00, "stock": 5,
        }, follow=True)
        product.refresh_from_db()
        assert product.name == "Laptop Actualizada"
        assert product.price == 18000.00
        assert response.status_code == 200

    def test_update_nonexistent_product(self, client):
        response = client.get("/999/editar/")
        assert response.status_code == 404


class TestProductDeleteView:
    def test_delete_product_get(self, client, product):
        response = client.get(f"/{product.pk}/eliminar/")
        assert response.status_code == 200
        assert "Laptop" in response.content.decode()

    def test_delete_product_confirm(self, client, product):
        response = client.post(f"/{product.pk}/eliminar/", follow=True)
        assert not Product.objects.filter(pk=product.pk).exists()
        assert response.status_code == 200

    def test_delete_nonexistent_product(self, client):
        response = client.post("/999/eliminar/", follow=True)
        assert response.status_code == 404