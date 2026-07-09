from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


INVENTORY_PERMS = {
    'add_category', 'change_category', 'delete_category', 'view_category',
    'add_product', 'change_product', 'delete_product', 'view_product',
    'add_stockmovement', 'change_stockmovement', 'delete_stockmovement', 'view_stockmovement',
}


class Command(BaseCommand):
    help = 'Crea los grupos predefinidos con sus permisos'

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name='Administradores')
        editor_group, _ = Group.objects.get_or_create(name='Editores')
        viewer_group, _ = Group.objects.get_or_create(name='Visualizadores')

        all_perms = Permission.objects.filter(codename__in=INVENTORY_PERMS)
        admin_group.permissions.set(all_perms)

        editor_codenames = {
            'add_category', 'change_category', 'view_category',
            'add_product', 'change_product', 'view_product',
            'add_stockmovement', 'view_stockmovement',
        }
        editor_perms = Permission.objects.filter(codename__in=editor_codenames)
        editor_group.permissions.set(editor_perms)

        viewer_codenames = {
            'view_category', 'view_product', 'view_stockmovement',
        }
        viewer_perms = Permission.objects.filter(codename__in=viewer_codenames)
        viewer_group.permissions.set(viewer_perms)

        self.stdout.write(self.style.SUCCESS(
            f'Grupos creados: Administradores ({admin_group.permissions.count()} permisos), '
            f'Editores ({editor_group.permissions.count()} permisos), '
            f'Visualizadores ({viewer_group.permissions.count()} permisos)'
        ))
