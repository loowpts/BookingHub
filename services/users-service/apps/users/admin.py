from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from users.models import User, UserProfile, EmailVerificationToken, PasswordResetToken


class UserProfileInline(admin.StackedInline):
    """
    Inline для профиля пользователя.

    Позволяет редактировать профиль прямо на странице пользователя.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админка для модели User.

    Кастомизирует отображение пользователей в админ-панели.
    """
    inlines = (UserProfileInline,)

    list_display = [
        'email', 'first_name', 'last_name', 'is_email_verified',
        'is_active', 'is_staff', 'created_at'
    ]
    list_filter = ['is_email_verified', 'is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified')}),
        ('Важные даты', {'fields': ('last_login', 'last_login_at', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login', 'last_login_at', 'uuid']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей."""
    list_display = ['user', 'country', 'city', 'language', 'created_at']
    list_filter = ['language', 'country']
    search_fields = ['user__email', 'city', 'country']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Админка для токенов верификации email."""
    list_display = ['user', 'token', 'is_used', 'is_expired', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']

    def is_expired(self, obj):
        """Показывает истек ли токен."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Истек'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Админка для токенов сброса пароля."""
    list_display = ['user', 'token', 'is_used', 'is_expired', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']

    def is_expired(self, obj):
        """Показывает истек ли токен."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Истек'
