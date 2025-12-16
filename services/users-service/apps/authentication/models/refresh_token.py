from uuid import uuid4
from django.db import models
from apps.authentication.models.user import User


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
