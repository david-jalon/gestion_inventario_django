import pytest
from django.contrib.auth.models import User
from inventory.models import Category, Product, StockMovement

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def client_auth(client, user):
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


class TestStockMovementModel:
    def test_create_entry_movement(self, product):
        movement = StockMovement.objects.create(
            product=product, quantity=5, movement_type='entry', reason='Reabastecimiento'
        )
        assert movement.product == product
        assert movement.quantity == 5
        assert movement.movement_type == 'entry'
        assert str(movement) == 'Entrada - Laptop (5)'

    def test_create_exit_movement(self, product):
        movement = StockMovement.objects.create(
            product=product, quantity=3, movement_type='exit', reason='Venta'
        )
        assert movement.movement_type == 'exit'
        assert str(movement) == 'Salida - Laptop (3)'

    def test_movement_ordering(self, product):
        StockMovement.objects.create(product=product, quantity=1, movement_type='entry')
        StockMovement.objects.create(product=product, quantity=2, movement_type='exit')
        movements = StockMovement.objects.all()
        assert movements[0].quantity == 2
        assert movements[1].quantity == 1

    def test_cascade_on_product_delete(self, product):
        StockMovement.objects.create(product=product, quantity=5, movement_type='entry')
        product.delete()
        assert StockMovement.objects.count() == 0

    def test_signal_creates_movement_on_create(self, category):
        product = Product.objects.create(
            name="Mouse", category=category, price=500.00, stock=10,
        )
        movements = product.movements.all()
        assert movements.count() == 1
        assert movements[0].movement_type == 'entry'
        assert movements[0].quantity == 10
        assert movements[0].reason == 'Stock inicial'


class TestMovementListView:
    def test_list_movements(self, client_auth, product):
        StockMovement.objects.create(product=product, quantity=5, movement_type='entry', reason='Compra')
        response = client_auth.get(f"/productos/{product.pk}/movimientos/")
        assert response.status_code == 200
        assert "Compra" in response.content.decode()
        assert "Laptop" in response.content.decode()

    def test_list_shows_signal_movement(self, client_auth, product):
        response = client_auth.get(f"/productos/{product.pk}/movimientos/")
        assert response.status_code == 200
        assert "Stock inicial" in response.content.decode()
        assert "+10" in response.content.decode()

    def test_list_nonexistent_product(self, client_auth):
        response = client_auth.get("/productos/999/movimientos/")
        assert response.status_code == 404


class TestMovementCreateView:
    def test_create_entry(self, client_auth, product):
        response = client_auth.post(f"/productos/{product.pk}/movimientos/nuevo/", {
            "quantity": 5, "movement_type": "entry", "reason": "Nueva compra",
        }, follow=True)
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.stock == 15
        assert StockMovement.objects.filter(product=product, reason="Nueva compra").exists()

    def test_create_exit(self, client_auth, product):
        response = client_auth.post(f"/productos/{product.pk}/movimientos/nuevo/", {
            "quantity": 3, "movement_type": "exit", "reason": "Venta",
        }, follow=True)
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.stock == 7

    def test_create_nonexistent_product(self, client_auth):
        response = client_auth.post("/productos/999/movimientos/nuevo/", {
            "quantity": 1, "movement_type": "entry",
        })
        assert response.status_code == 404
