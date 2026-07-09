import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


class TestLoginView:
    def test_login_page(self, client):
        response = client.get("/login/")
        assert response.status_code == 200
        assert "Iniciar Sesión" in response.content.decode()

    def test_login_success(self, client):
        User.objects.create_user(username="test", password="pass1234")
        response = client.post("/login/", {
            "username": "test", "password": "pass1234",
        }, follow=True)
        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated

    def test_login_failure(self, client):
        response = client.post("/login/", {
            "username": "wrong", "password": "wrong",
        }, follow=True)
        assert response.status_code == 200
        assert "Usuario o contraseña incorrectos" in response.content.decode()


class TestRegisterView:
    def test_register_page(self, client):
        response = client.get("/registro/")
        assert response.status_code == 200
        assert "Crear Cuenta" in response.content.decode()

    def test_register_success(self, client):
        response = client.post("/registro/", {
            "username": "newuser", "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }, follow=True)
        assert User.objects.filter(username="newuser").exists()
        assert "Cuenta creada exitosamente" in response.content.decode()

    def test_register_password_mismatch(self, client):
        response = client.post("/registro/", {
            "username": "newuser", "password1": "pass1234",
            "password2": "different",
        })
        assert response.status_code == 200
        assert not User.objects.filter(username="newuser").exists()


class TestLogoutView:
    def test_logout(self, client):
        User.objects.create_user(username="test", password="pass1234")
        client.login(username="test", password="pass1234")
        response = client.post("/logout/", follow=True)
        assert not response.wsgi_request.user.is_authenticated


class TestAuthRequired:
    def test_dashboard_redirects_when_anonymous(self, client):
        response = client.get("/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_product_list_redirects_when_anonymous(self, client):
        response = client.get("/productos/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_categories_redirects_when_anonymous(self, client):
        response = client.get("/categorias/")
        assert response.status_code == 302
        assert "/login/" in response.url
