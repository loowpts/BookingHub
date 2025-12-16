from uuid import uuid4
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=50, unique=True) # Для ссылки bookinghub.com/{username}
    password_hash = models.CharField(max_length=255)
    role = models.CharField(choices=['provider', 'admin'], default=['provider'])
    is_active = models.BooleanField(default=False) # Активируем после подтверждения email
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True)
    

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return self.email
