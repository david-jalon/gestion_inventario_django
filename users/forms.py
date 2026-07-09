from collections import defaultdict
from django import forms
from django.contrib.auth.models import User, Group, Permission


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput,
        help_text='Dejar en blanco para mantener la actual (solo en edición).',
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups', 'user_permissions']

    def __init__(self, *args, **kwargs):
        self.is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)
        if self.is_create:
            self.fields['password'].required = True
        perms = self.fields['user_permissions'].queryset.order_by(
            'content_type__app_label', 'content_type__model', 'codename'
        )
        grouped = defaultdict(list)
        for p in perms:
            grouped[(p.content_type.app_label, p.content_type.model)].append((p.pk, p.name))
        choices = []
        for (app_label, model_name), items in grouped.items():
            group_label = f'{app_label.title()} - {model_name.replace("_", " ").title()}'
            choices.append((group_label, items))
        self.fields['user_permissions'].choices = choices

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                pass
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500')
            else:
                field.widget.attrs.setdefault('class', 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500')

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
