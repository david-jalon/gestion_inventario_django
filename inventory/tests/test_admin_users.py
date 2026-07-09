import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        username='admin', password='admin123', email='admin@example.com'
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        username='regular', password='pass1234', email='regular@example.com'
    )


@pytest.fixture
def client_superuser(client, superuser):
    client.force_login(superuser)
    return client


@pytest.fixture
def client_regular(client, regular_user):
    client.force_login(regular_user)
    return client


class TestUserList:
    def test_superuser_can_access(self, client_superuser):
        response = client_superuser.get('/usuarios/')
        assert response.status_code == 200

    def test_regular_user_redirected(self, client_regular):
        response = client_regular.get('/usuarios/')
        assert response.status_code == 302

    def test_anonymous_redirected(self, client):
        response = client.get('/usuarios/')
        assert response.status_code == 302

    def test_lists_all_users(self, client_superuser, regular_user):
        response = client_superuser.get('/usuarios/')
        assert 'regular' in response.content.decode()
        assert 'admin' in response.content.decode()


class TestUserCreate:
    def test_create_user_get(self, client_superuser):
        response = client_superuser.get('/usuarios/nuevo/')
        assert response.status_code == 200

    def test_create_user_post(self, client_superuser):
        response = client_superuser.post('/usuarios/nuevo/', {
            'username': 'newuser',
            'password': 'Pass1234!',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'is_active': True,
            'is_staff': False,
        }, follow=True)
        assert User.objects.filter(username='newuser').exists()
        assert 'Usuario creado' in response.content.decode()

    def test_create_user_requires_password(self, client_superuser):
        response = client_superuser.post('/usuarios/nuevo/', {
            'username': 'nopass',
            'password': '',
            'email': 'nopass@example.com',
        })
        assert 'password' in response.context['form'].errors

    def test_regular_cannot_create(self, client_regular):
        response = client_regular.get('/usuarios/nuevo/')
        assert response.status_code == 302


class TestUserUpdate:
    def test_update_user_get(self, client_superuser, regular_user):
        response = client_superuser.get(f'/usuarios/{regular_user.pk}/editar/')
        assert response.status_code == 200

    def test_update_user_post(self, client_superuser, regular_user):
        response = client_superuser.post(f'/usuarios/{regular_user.pk}/editar/', {
            'username': 'regular',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True,
        }, follow=True)
        regular_user.refresh_from_db()
        assert regular_user.email == 'updated@example.com'
        assert regular_user.first_name == 'Updated'
        assert regular_user.is_staff
        assert 'Usuario actualizado' in response.content.decode()

    def test_regular_cannot_edit(self, client_regular, superuser):
        response = client_regular.get(f'/usuarios/{superuser.pk}/editar/')
        assert response.status_code == 302


class TestUserToggleStaff:
    def test_toggle_staff(self, client_superuser, regular_user):
        response = client_superuser.post(f'/usuarios/{regular_user.pk}/toggle-staff/', follow=True)
        regular_user.refresh_from_db()
        assert regular_user.is_staff
        assert 'concedido' in response.content.decode()

        response = client_superuser.post(f'/usuarios/{regular_user.pk}/toggle-staff/', follow=True)
        regular_user.refresh_from_db()
        assert not regular_user.is_staff
        assert 'revocado' in response.content.decode()

    def test_cannot_toggle_self(self, client_superuser, superuser):
        response = client_superuser.post(f'/usuarios/{superuser.pk}/toggle-staff/', follow=True)
        assert 'No puedes cambiarte' in response.content.decode()


class TestUserToggleActive:
    def test_toggle_active(self, client_superuser, regular_user):
        response = client_superuser.post(f'/usuarios/{regular_user.pk}/toggle-active/', follow=True)
        regular_user.refresh_from_db()
        assert not regular_user.is_active
        assert 'desactivada' in response.content.decode()

        response = client_superuser.post(f'/usuarios/{regular_user.pk}/toggle-active/', follow=True)
        regular_user.refresh_from_db()
        assert regular_user.is_active
        assert 'activada' in response.content.decode()

    def test_cannot_deactivate_self(self, client_superuser, superuser):
        response = client_superuser.post(f'/usuarios/{superuser.pk}/toggle-active/', follow=True)
        assert 'No puedes desactivar' in response.content.decode()


class TestUserDelete:
    def test_delete_user_post(self, client_superuser, regular_user):
        pk = regular_user.pk
        response = client_superuser.post(f'/usuarios/{pk}/eliminar/', follow=True)
        assert not User.objects.filter(pk=pk).exists()
        assert 'eliminado' in response.content.decode()

    def test_delete_user_get_shows_form(self, client_superuser, regular_user):
        response = client_superuser.get(f'/usuarios/{regular_user.pk}/eliminar/')
        assert response.status_code == 200
        assert regular_user.username in response.content.decode()

    def test_cannot_delete_self(self, client_superuser, superuser):
        response = client_superuser.get(f'/usuarios/{superuser.pk}/eliminar/', follow=True)
        assert 'No puedes eliminar' in response.content.decode()
