from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active',)
    list_filter = ('role', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'patronymic', 'phone',)}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'phone'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Register your models here.
