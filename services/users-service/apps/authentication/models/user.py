import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
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
    
class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=500, unique=True) # JWT string
    jti = models.CharField(max_length=255, unique=True, db_index=True) # JWT ID для blacklist
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_revoked = models.BooleanField(default=False) # для soft revocation
    revoked_at = models.DateTimeField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['jti']),
            models.Index(fields=['user_id', 'is_revoked']),
            models.Index(fields=['expires_at'])
        ]


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True) # random hash
    expires_at = models.DateTimeField() # 24 hours
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    

class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField() # 1 hours
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
