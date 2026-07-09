from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', views.register, name='register'),
    path('perfil/cambiar-contrasena/', PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/perfil/contrasena-cambiada/',
    ), name='password_change'),
    path('perfil/contrasena-cambiada/', PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html',
    ), name='password_change_done'),
    path('perfil/editar/', views.profile_update, name='profile_update'),
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/nuevo/', views.user_create, name='user_create'),
    path('usuarios/<int:pk>/editar/', views.user_update, name='user_update'),
    path('usuarios/<int:pk>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),
    path('usuarios/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('usuarios/<int:pk>/eliminar/', views.user_delete, name='user_delete'),
]
