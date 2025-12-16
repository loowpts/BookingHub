import jwt
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from apps.authentication.models.refresh_token import RefreshToken
from django.conf import settings
from django.core import exceptions
from models.user import User

        
class UserRegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password',
            'password_confirm'
        ]
    
    def validate_email(self, value):
        """Проверка уникальности email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def validate_username(self, value):
        """Проверка уникальности username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        
        return value
    
    def validate_password(self, value):
        """Валидация пароля"""
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.message))
        return value
    
    def validate(self, attrs):
        """Проверка совпадений пароля."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return attrs
    
    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create_user(**validated_data)
        
        # UserProfile.object.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.filter(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        if not user.is_active:
            raise serializers.ValidationError('Account is inactive')
        
        if not user.is_email_verified:
            raise serializers.ValidationError('Email not verified')
        
        attrs['user'] = user
        
        return attrs
    
    
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
        
