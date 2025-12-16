from uuid import uuid4
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, username, password, **extra_fields)
        

class User(AbstractBaseUser):
    
    ROLE_CHOICES = [
        ('Provider', 'provider'),
        ('Admin', 'admin')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=50, unique=True) # Для ссылки bookinghub.com/{username}
    password_hash = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, default='provider')
    is_active = models.BooleanField(default=False) # Активируем после подтверждения email
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']    

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active'])
        ]
    
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        """Хеширование и сохранение пароля"""
        return super().make_password(raw_password)

    def check_password(self, raw_password):
        """Проверка пароля"""
        return super().check_password(raw_password, self.password)
    
    
