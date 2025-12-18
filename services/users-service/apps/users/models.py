from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from users.managers.user_manager import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        }
    )
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['uuid']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
        
        
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'.strip()
        return self.email
    
    def get_short_name(self):
        """Возвращает короткое имя(имя или email)"""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_profile_complete(self):
        """Проверяет заполнен ли профиль пользователя."""
        return bool(
            self.first_name and
            self.last_name and
            self.phone and
            self.is_email_verified
        )
        
    def update_last_login(self):
        """Обновляет время последнего входа."""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])
        
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    language = models.CharField(
        max_length=50,
        default='ru',
        choices=[
            ('ru', 'Русский'),
            ('en', 'English'),
        ]
    )
    timezone = models.CharField(max_length=50, default='Europe/Moscow')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        
    def __str__(self):
        return f'Профиль: {self.user.email}'
    
    @property
    def age(self):
        """Вычисляет возраст пользователя из даты рождения."""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        
class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        verbose_name='Пользователь'
    )
    token = models.UUIDField(default=uuid4, editable=False, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField('Действителен до')
    
    class Meta:
        db_table = 'email_verification_tokens'
        verbose_name = 'Токен верификации email'
        verbose_name_plural = 'Токены верификации email'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Токен верификации для {self.user.email}'
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем expires_at"""
        if not self.expires_at:
           timeout = settings.USER_SETTINGS.get('EMAIL_VERIFICATION_TIMEOUT', 86400)
           self.expires_at = timezone.now() + timedelta(seconds=timeout)
        super().save(*args, **kwargs)
        
    @property
    def is_expired(self):
        """Проверяет истек ли."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Проверяет валиден ли токен(не использован и не истек)."""
        return not self.is_used and not self.is_expired
    

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name='Пользователь'
    )
    token = models.UUIDField(default=uuid4, editable=False, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField('Действителен до')
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Токен сброса пароля'
        verbose_name_plural = 'Токены сброса пароля'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Токен сброса пароля для {self.user.email}'
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем expires_at"""
        if not self.expires_at:
           timeout = settings.USER_SETTINGS.get('PASSWORD_RESET_TIMEOUT', 3600)
           self.expires_at = timezone.now() + timedelta(seconds=timeout)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
