import jwt
from rest_framework import serializers
from django.conf import settings

from apps.authentication.models.refresh_token import RefreshToken

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
        
        return {
            'user': token.user
        }
