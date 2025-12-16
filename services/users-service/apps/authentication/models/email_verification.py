from uuid import uuid4
from django.db import models
from apps.authentication.models.user import User


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True) # random hash
    expires_at = models.DateTimeField() # 24 hours
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
