import pytest
import io
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from inventory.models import CompanySettings

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser():
    return User.objects.create_superuser(username='admin', password='admin123')


@pytest.fixture
def client_super(client, superuser):
    client.force_login(superuser)
    return client


@pytest.fixture
def user():
    return User.objects.create_user(username='regular', password='pass123')


@pytest.fixture
def client_user(client, user):
    client.force_login(user)
    return client


class TestCompanySettingsModel:
    def test_load_creates_default(self):
        settings = CompanySettings.load()
        assert settings.company_name == 'Mi Empresa'
        assert settings.currency_symbol == '$'
        assert settings.pk == 1

    def test_load_returns_same_instance(self):
        s1 = CompanySettings.load()
        s2 = CompanySettings.load()
        assert s1.pk == s2.pk

    def test_update_values(self):
        settings = CompanySettings.load()
        settings.company_name = 'Mi Tienda'
        settings.currency_symbol = '€'
        settings.save()
        settings.refresh_from_db()
        assert settings.company_name == 'Mi Tienda'
        assert settings.currency_symbol == '€'

    def test_singleton_prevents_second_instance(self):
        CompanySettings.load()
        second = CompanySettings(company_name='Otra', currency_symbol='€')
        second.save()
        assert CompanySettings.objects.count() == 1
        assert CompanySettings.load().company_name == 'Otra'


class TestCompanySettingsView:
    def test_superuser_can_access(self, client_super):
        response = client_super.get('/configuracion/')
        assert response.status_code == 200
        assert 'Configuración' in response.content.decode()

    def test_regular_user_redirected(self, client_user):
        response = client_user.get('/configuracion/')
        assert response.status_code == 302

    def test_anonymous_redirected(self, client):
        response = client.get('/configuracion/')
        assert response.status_code == 302

    def test_update_settings(self, client_super):
        response = client_super.post('/configuracion/', {
            'company_name': 'Nueva Empresa',
            'currency_symbol': '€',
        })
        assert response.status_code == 302
        settings = CompanySettings.load()
        assert settings.company_name == 'Nueva Empresa'
        assert settings.currency_symbol == '€'

    def test_upload_logo(self, client_super):
        image = SimpleUploadedFile(
            'logo.png', b'fake-image-content', content_type='image/png',
        )
        response = client_super.post('/configuracion/', {
            'company_name': 'Con Logo',
            'currency_symbol': '$',
            'logo': image,
        })
        assert response.status_code == 302
        settings = CompanySettings.load()
        assert settings.logo is not None
        assert 'logo' in settings.logo.name


class TestContextProcessor:
    def test_company_name_in_context(self, client_super):
        settings = CompanySettings.load()
        settings.company_name = 'TestCorp'
        settings.save()
        response = client_super.get('/')
        content = response.content.decode()
        assert 'TestCorp' in content

    def test_currency_symbol_in_dashboard(self, client_super):
        CompanySettings.load()
        response = client_super.get('/')
        content = response.content.decode()
        assert '$' in content

    def test_custom_currency_in_dashboard(self, client_super):
        settings = CompanySettings.load()
        settings.currency_symbol = '€'
        settings.save()
        response = client_super.get('/')
        content = response.content.decode()
        assert '€' in content
