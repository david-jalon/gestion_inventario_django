import pytest
from django.contrib.auth.models import User, Group, Permission
from inventory.models import Category, Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def groups():
    admin_group, _ = Group.objects.get_or_create(name='Administradores')
    editor_group, _ = Group.objects.get_or_create(name='Editores')
    viewer_group, _ = Group.objects.get_or_create(name='Visualizadores')

    inventory_perms = Permission.objects.filter(
        content_type__app_label='inventory',
    )
    admin_group.permissions.set(inventory_perms)

    editor_codenames = {
        'add_category', 'change_category', 'view_category',
        'add_product', 'change_product', 'view_product',
        'add_stockmovement', 'view_stockmovement',
    }
    editor_group.permissions.set(
        Permission.objects.filter(codename__in=editor_codenames)
    )

    viewer_codenames = {
        'view_category', 'view_product', 'view_stockmovement',
    }
    viewer_group.permissions.set(
        Permission.objects.filter(codename__in=viewer_codenames)
    )

    return admin_group, editor_group, viewer_group


@pytest.fixture
def admin_user(groups):
    u = User.objects.create_user(username='admin_user', password='pass1234')
    u.groups.add(groups[0])
    return u


@pytest.fixture
def editor_user(groups):
    u = User.objects.create_user(username='editor_user', password='pass1234')
    u.groups.add(groups[1])
    return u


@pytest.fixture
def viewer_user(groups):
    u = User.objects.create_user(username='viewer_user', password='pass1234')
    u.groups.add(groups[2])
    return u


@pytest.fixture
def no_perm_user():
    return User.objects.create_user(username='noperm', password='pass1234')


@pytest.fixture
def category():
    return Category.objects.create(name="Test")


class TestPermissionDecorator:
    def test_admin_can_create_product(self, client, admin_user, category):
        client.force_login(admin_user)
        response = client.get('/productos/nuevo/')
        assert response.status_code == 200

    def test_editor_can_create_product(self, client, editor_user, category):
        client.force_login(editor_user)
        response = client.get('/productos/nuevo/')
        assert response.status_code == 200

    def test_viewer_cannot_create_product(self, client, viewer_user):
        client.force_login(viewer_user)
        response = client.get('/productos/nuevo/', follow=True)
        assert 'No tienes permiso' in response.content.decode()
        assert response.redirect_chain[-1][0].endswith('/')

    def test_noperm_cannot_create_product(self, client, no_perm_user):
        client.force_login(no_perm_user)
        response = client.get('/productos/nuevo/', follow=True)
        assert 'No tienes permiso' in response.content.decode()

    def test_editor_cannot_delete(self, client, editor_user):
        cat = Category.objects.create(name='Test')
        prod = Product.objects.create(name='P', category=cat, price=10, stock=5)
        client.force_login(editor_user)
        response = client.post(f'/productos/{prod.pk}/eliminar/', follow=True)
        assert 'No tienes permiso' in response.content.decode()

    def test_viewer_cannot_delete(self, client, viewer_user):
        cat = Category.objects.create(name='Test2')
        prod = Product.objects.create(name='P2', category=cat, price=10, stock=5)
        client.force_login(viewer_user)
        response = client.post(f'/productos/{prod.pk}/eliminar/', follow=True)
        assert 'No tienes permiso' in response.content.decode()


class TestSeedGroupsCommand:
    def test_seed_groups(self):
        from django.core.management import call_command
        call_command('seed_groups')
        assert Group.objects.filter(name='Administradores').exists()
        assert Group.objects.filter(name='Editores').exists()
        assert Group.objects.filter(name='Visualizadores').exists()
        admin_group = Group.objects.get(name='Administradores')
        editor_group = Group.objects.get(name='Editores')
        viewer_group = Group.objects.get(name='Visualizadores')
        assert admin_group.permissions.count() == 12
        assert editor_group.permissions.count() == 8
        assert viewer_group.permissions.count() == 3


class TestTemplatePermissions:
    def test_viewer_sees_no_create_button(self, client, viewer_user):
        from inventory.models import Category, Product
        cat = Category.objects.create(name='Test')
        Product.objects.create(name='P', category=cat, price=10, stock=5)
        client.force_login(viewer_user)
        response = client.get('/productos/')
        content = response.content.decode()
        assert 'Nuevo Producto' not in content
        assert 'Editar' not in content
        assert 'Eliminar' not in content

    def test_editor_sees_create_and_edit_but_not_delete(self, client, editor_user):
        from inventory.models import Category, Product
        cat = Category.objects.create(name='Test')
        Product.objects.create(name='P', category=cat, price=10, stock=5)
        client.force_login(editor_user)
        response = client.get('/productos/')
        content = response.content.decode()
        assert 'Nuevo Producto' in content
        assert 'Editar' in content
        assert 'Eliminar' not in content

    def test_admin_sees_all_buttons(self, client, admin_user):
        from inventory.models import Category, Product
        cat = Category.objects.create(name='Test')
        Product.objects.create(name='P', category=cat, price=10, stock=5)
        client.force_login(admin_user)
        response = client.get('/productos/')
        content = response.content.decode()
        assert 'Nuevo Producto' in content
        assert 'Editar' in content
        assert 'Eliminar' in content
