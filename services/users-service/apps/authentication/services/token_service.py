import jwt
from uuid import uuid4
from datetime import datetime, timedelta
from django.db import models
from apps.authentication.models.refresh_token import RefreshToken 
from django.conf import settings


def generate_access_token(user):
    payload = {
        'token_type': 'access',
        'user_id': str(user.id),
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow(),
        'jti': str(uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

def generate_refresh_token(user):
    jti = str(uuid4())
    payload = {
        'token_type': 'refresh',
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(days=7),
        'jti': jti
    }
    token_string = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    
    RefreshToken.objects.create(
        user=user,
        token=token_string,
        jti=jti,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
