from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q

class UserQuerySet(models.QuerySet):
    """
    Кастомный QuerySet для модели User.

    QuerySet - это набор методов для работы с несколькими объектами.
    Позволяет делать цепочки фильтров: User.objects.active().verified()

    ВАЖНО: Методы QuerySet возвращают QuerySet, поэтому можно делать цепочки.
    """
    
    def active(self):
        """
        Возвращает только активных пользователей.
        
        User.objects.active()
        
        """
        return self.filter(is_active=True)
    
    def verified(self):
        """
        Возвращает пользователей с подтвержденным email.
        
        User.objects.verified()
        """
        return self.filter(is_email_verified=True)
    
    def unverified(self):
        """
        Возвращает пользователей с неподтвержденным email.
        
        User.objects.unverified()
        """
        return self.filter(is_email_verified=False)
    
    def staff(self):
        """
        Возвращает пользователей с доступом к админке.
        """
        return self.filter(is_staff=True)
    
    def search(self, query):
        """
        Поиск пользователей по email, имени или фамилии.
        
        User.objects.search('ivan')
        """
        return self.filter(
            Q(email__icontains=query),
            Q(first_name__icontains=query),
            Q(last_name__icontains=query)
        )
        

class UserManager(BaseUserManager):
    """
    Кастомный Manager для модели User.

    Manager отвечает за создание объектов и работу с QuerySet.
    Обязательно должен иметь методы create_user и create_superuser.

    РАЗНИЦА МЕЖДУ MANAGER И QUERYSET:
    - Manager: методы для создания объектов (create_user, create_superuser)
    - QuerySet: методы для фильтрации и получения объектов (filter, get, active)
    """
    
    def get_queryset(self):
        """
        Возвращает кастомный QuerySet для всех запросов.
        
        Теперь все запросы будут использовать UseQuerySet
        и получат доступ к методам active(), verified(), итд
        """
        
    def active(self):
        """Proxy метод для UserQuerySet.active()"""
        return self.get_queryset().active()
    
    def verified(self):
        return self.get_queryset().verified()
    
    def unverified(self):
        return self.get_queryset().unverified()

    def staff(self):
        return self.get_queryset().staff()
    
    def search(self, query):
        return self.get_queryset().search(query)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для создания пользователя')
        
        email = normalize_email(email)
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)

        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def get_by_email(self, email):
        """
        Получает пользователя по email (case-insensitive).

        Вспомогательный метод для получения пользователя по email.

        Пример:
            user = User.objects.get_by_email('User@Example.com')
        """   
        return self.get(email__iexact=email)
    
    def email_exists(self, email):
        """
        Проверяет существует ли пользователь с таким email.

        Пример:
            if User.objects.email_exists('test@example.com'):
                print('Email уже занят')
        """  
        return self.filter(email__iexact=email).exists()      
