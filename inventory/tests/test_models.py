import pytest
from inventory.models import Category, Product

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_create_category(self):
        category = Category.objects.create(name="Electrónicos", description="Productos electrónicos")
        assert category.name == "Electrónicos"
        assert category.description == "Productos electrónicos"
        assert str(category) == "Electrónicos"

    def test_category_verbose_name_plural(self):
        assert Category._meta.verbose_name_plural == "categories"

    def test_category_unique_name(self):
        Category.objects.create(name="Ropa")
        with pytest.raises(Exception):
            Category.objects.create(name="Ropa")

    def test_category_default_fields(self):
        category = Category.objects.create(name="Hogar")
        assert category.description == ""
        assert category.created_at is not None
        assert category.updated_at is not None


class TestProductModel:
    def test_create_product(self):
        category = Category.objects.create(name="Electrónicos")
        product = Product.objects.create(
            name="Laptop", description="Laptop gamer",
            category=category, price=15000.00, stock=10, low_stock_threshold=3,
        )
        assert product.name == "Laptop"
        assert product.description == "Laptop gamer"
        assert product.category == category
        assert product.price == 15000.00
        assert product.stock == 10
        assert product.low_stock_threshold == 3
        assert str(product) == "Laptop"

    def test_product_default_stock_and_threshold(self):
        category = Category.objects.create(name="Ropa")
        product = Product.objects.create(name="Camiseta", category=category, price=200.00)
        assert product.stock == 0
        assert product.low_stock_threshold == 5

    def test_product_is_low_stock_true(self):
        category = Category.objects.create(name="Ropa")
        product = Product.objects.create(
            name="Camiseta", category=category, price=200.00, stock=2, low_stock_threshold=5
        )
        assert product.is_low_stock is True

    def test_product_is_low_stock_false(self):
        category = Category.objects.create(name="Ropa")
        product = Product.objects.create(
            name="Camiseta", category=category, price=200.00, stock=10, low_stock_threshold=5
        )
        assert product.is_low_stock is False

    def test_product_is_low_stock_equal_threshold(self):
        category = Category.objects.create(name="Ropa")
        product = Product.objects.create(
            name="Camiseta", category=category, price=200.00, stock=5, low_stock_threshold=5
        )
        assert product.is_low_stock is True

    def test_product_category_relation(self):
        category = Category.objects.create(name="Electrónicos")
        Product.objects.create(name="Laptop", category=category, price=15000.00)
        Product.objects.create(name="Mouse", category=category, price=500.00)
        assert category.products.count() == 2

    def test_product_category_delete_cascade(self):
        category = Category.objects.create(name="Electrónicos")
        Product.objects.create(name="Laptop", category=category, price=15000.00)
        category.delete()
        assert Product.objects.count() == 0