from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm, UserAdminForm


def is_superuser(user):
    return user.is_superuser


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Inicia sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('profile_update')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'registration/profile_form.html', {'form': form})


# --- Admin de usuarios (solo superuser) ---

@login_required
@user_passes_test(is_superuser)
def user_list(request):
    users = User.objects.all().order_by('-is_superuser', '-is_staff', 'username')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
@user_passes_test(is_superuser)
def user_create(request):
    if request.method == 'POST':
        form = UserAdminForm(request.POST, is_create=True)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserAdminForm(is_create=True)
    return render(request, 'users/user_form.html', {'form': form, 'is_create': True})


@login_required
@user_passes_test(is_superuser)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = UserAdminForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'is_create': False, 'user_obj': user})


@login_required
@user_passes_test(is_superuser)
def user_toggle_staff(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'No puedes cambiarte el acceso de administrador a ti mismo.')
        return redirect('user_list')
    user.is_staff = not user.is_staff
    user.save(update_fields=['is_staff'])
    action = 'concedido' if user.is_staff else 'revocado'
    messages.success(request, f'Acceso de administrador {action} para {user.username}.')
    return redirect('user_list')


@login_required
@user_passes_test(is_superuser)
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('user_list')
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    action = 'activada' if user.is_active else 'desactivada'
    messages.success(request, f'Cuenta de {user.username} {action}.')
    return redirect('user_list')


@login_required
@user_passes_test(is_superuser)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('user_list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user_obj': user})
