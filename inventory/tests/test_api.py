import pytest
import json
from django.contrib.auth.models import User
from inventory.models import Category, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username='apiuser', password='testpass123')


@pytest.fixture
def client_auth(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def category():
    return Category.objects.create(name='Electrónicos')


@pytest.fixture
def product(category):
    return Product.objects.create(
        name='Laptop', category=category, price=15000.00, stock=10,
    )


class TestCategoryAPI:
    def test_list_categories(self, client_auth, category):
        response = client_auth.get('/api/categorias/')
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Electrónicos'

    def test_create_category(self, client_auth):
        response = client_auth.post('/api/categorias/', {
            'name': 'Ropa', 'description': 'Prendas de vestir'
        }, content_type='application/json')
        assert response.status_code == 201
        assert response.json()['name'] == 'Ropa'

    def test_retrieve_category(self, client_auth, category):
        response = client_auth.get(f'/api/categorias/{category.id}/')
        assert response.status_code == 200
        assert response.json()['name'] == 'Electrónicos'

    def test_update_category(self, client_auth, category):
        response = client_auth.put(f'/api/categorias/{category.id}/', {
            'name': 'Tecnología', 'description': category.description
        }, content_type='application/json')
        assert response.status_code == 200
        assert response.json()['name'] == 'Tecnología'

    def test_delete_category(self, client_auth, category):
        response = client_auth.delete(f'/api/categorias/{category.id}/')
        assert response.status_code == 204
        assert Category.objects.count() == 0

    def test_search_category(self, client_auth, category):
        Category.objects.create(name='Ropa')
        response = client_auth.get('/api/categorias/?search=Ropa')
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Ropa'


class TestProductAPI:
    def test_list_products(self, client_auth, product):
        response = client_auth.get('/api/productos/')
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Laptop'

    def test_create_product(self, client_auth, category):
        response = client_auth.post('/api/productos/', {
            'name': 'Mouse', 'category': category.id,
            'price': '500.00', 'stock': 25,
        }, content_type='application/json')
        assert response.status_code == 201
        assert response.json()['name'] == 'Mouse'

    def test_retrieve_product(self, client_auth, product):
        response = client_auth.get(f'/api/productos/{product.id}/')
        assert response.status_code == 200
        assert response.json()['name'] == 'Laptop'

    def test_update_product(self, client_auth, product):
        response = client_auth.patch(f'/api/productos/{product.id}/', {
            'price': '12000.00',
        }, content_type='application/json')
        assert response.status_code == 200
        assert float(response.json()['price']) == 12000.00

    def test_delete_product(self, client_auth, product):
        response = client_auth.delete(f'/api/productos/{product.id}/')
        assert response.status_code == 204
        assert Product.objects.count() == 0

    def test_filter_by_category(self, client_auth, category, product):
        other_cat = Category.objects.create(name='Ropa')
        Product.objects.create(name='Camiseta', category=other_cat, price=200.00, stock=10)
        response = client_auth.get(f'/api/productos/?category={category.id}')
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Laptop'

    def test_search_product(self, client_auth, product):
        response = client_auth.get('/api/productos/?search=laptop')
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 1

    def test_ordering(self, client_auth, category, product):
        Product.objects.create(name='Audífonos', category=category, price=800.00, stock=5)
        response = client_auth.get('/api/productos/?ordering=name')
        assert response.status_code == 200
        data = response.json()
        names = [p['name'] for p in data['results']]
        assert names == sorted(names)

    def test_is_low_stock_field(self, client_auth, category):
        prod = Product.objects.create(name='Teclado', category=category, price=300.00, stock=2, low_stock_threshold=5)
        response = client_auth.get(f'/api/productos/{prod.id}/')
        assert response.json()['is_low_stock'] is True

    def test_anonymous_gets_401(self, client):
        response = client.get('/api/productos/')
        assert response.status_code == 403

    def test_is_low_stock_read_only(self, client_auth, category):
        prod = Product.objects.create(name='Teclado', category=category, price=300.00, stock=2, low_stock_threshold=5)
        response = client_auth.patch(f'/api/productos/{prod.id}/', {
            'is_low_stock': False,
        }, content_type='application/json')
        assert response.status_code == 200
        assert response.json()['is_low_stock'] is True
