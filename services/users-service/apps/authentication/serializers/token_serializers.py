import logging
import jwt
from rest_framework import serializers
from django.conf import settings
from apps.utils.redis_client import redis_client

from apps.authentication.models.refresh_token import RefreshToken


logger = logging.getLogger(__name__)

class TokenRefreshSerializer(serializers.Serializer):
    
    def validate(self, attrs):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Invalid request context')
        
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            raise serializers.ValidationError('Refresh token not provided')
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Token expired')
        except jwt.InvalidTokenError:
            raise serializers.ValidationError('Invalid token')
        
        jti = payload.get('jti')
        if not jti:
            raise serializers.ValidationError('Invalid token')
        
        if redis_client.sismember('token_blacklist', jti):
            raise serializers.ValidationError('Token revoked')
        
        token = RefreshToken.objects.filter(jti=jti).select_related('user').first()
        if not token:
            raise serializers.ValidationError('Invalid token')
        
        if token.is_revoked():
            logger.warning(f'Attempt to use revoked token: {jti}, user={token.user.email}')
            RefreshToken.objects.filter(user=token.user).update(is_revoked=True)
            raise serializers.ValidationError('Token revoked. All sessions terminated for security.')
            
        return {
            'user': token.user
        }
