from uuid import uuid4
from django.db import models
from apps.authentication.models.user import User
from django.utils import timezone

class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
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

    def revoke(self):
        """Отозвать токен"""
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.save()
        
    def is_expired(self):
        """Проверка истечения"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Проверка валидности"""
        return not self.is_revoked and not self.is_expired()
    
    def __str__(self):
        return f'RefreshToken for {self.user.email} (jti={self.jti[:8]}...)'
