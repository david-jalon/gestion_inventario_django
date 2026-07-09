import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='oldpass123', email='test@example.com')


@pytest.fixture
def client_auth(client, user):
    client.force_login(user)
    return client


class TestPasswordChange:
    def test_password_change_page(self, client_auth):
        response = client_auth.get('/perfil/cambiar-contrasena/')
        assert response.status_code == 200
        assert 'Cambiar Contraseña' in response.content.decode()

    def test_password_change_success(self, client_auth, user):
        response = client_auth.post('/perfil/cambiar-contrasena/', {
            'old_password': 'oldpass123',
            'new_password1': 'NewPass456!',
            'new_password2': 'NewPass456!',
        }, follow=True)
        user.refresh_from_db()
        assert user.check_password('NewPass456!')
        assert 'Contraseña cambiada' in response.content.decode()

    def test_password_change_wrong_old(self, client_auth):
        response = client_auth.post('/perfil/cambiar-contrasena/', {
            'old_password': 'wrongpass',
            'new_password1': 'NewPass456!',
            'new_password2': 'NewPass456!',
        })
        assert 'old_password' in response.context['form'].errors

    def test_password_change_redirects_anonymous(self, client):
        response = client.get('/perfil/cambiar-contrasena/')
        assert response.status_code == 302


class TestProfileUpdate:
    def test_profile_page(self, client_auth):
        response = client_auth.get('/perfil/editar/')
        assert response.status_code == 200
        assert 'Mi Perfil' in response.content.decode()

    def test_profile_update(self, client_auth, user):
        response = client_auth.post('/perfil/editar/', {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
        }, follow=True)
        user.refresh_from_db()
        assert user.first_name == 'Juan'
        assert user.last_name == 'Pérez'
        assert user.email == 'juan@example.com'
        assert 'Perfil actualizado' in response.content.decode()

    def test_profile_update_redirects_anonymous(self, client):
        response = client.get('/perfil/editar/')
        assert response.status_code == 302
