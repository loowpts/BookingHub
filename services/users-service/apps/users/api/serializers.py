from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from users.models import User, UserProfile
from users.services import UserService
from users.utils.validators import validate_phone_number


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer для профиля пользователя."""
    age = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'birth_date', 'age', 'country', 'city',
            'address', 'language', 'timezone'
        ]

class UserSerializer(serializers.ModelSerializer):
    """Serializer для чтения информации о пользователе."""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_profile_complete = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'is_email_verified', 'is_profile_complete', 'is_active',
            'created_at', 'last_login_at', 'profile'
        ]
        read_only_fields = [
            'id', 'uuid', 'email', 'is_email_verified', 'is_active',
            'created_at', 'last_login_at'
        ]
        
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer для регистрации нового пользователя."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'},
                                     validators=[validate_password])
    password_confirm = serializers.CharField(writy_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return attrs
    
    def create(self, validated_data):
        return UserService.register_user(**validated_data)
    

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления данных пользователя."""
    phone = serializers.CharField(required=False, allow_blank=True, validators=[validate_phone_number])
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления профиля пользователя."""
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'birth_date', 'country', 'city',
            'address', 'language', 'timezone'
        ]
    
    def update(self, instance, validated_data):
        user = instance.user
        UserService.update_profile(user, **validated_data)
        instance.refresh_from_db()
        return instance
    
class ChangePasswordSerializer(serializers.Serializer):
    """Serializer для смены пароля."""
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'},
                                         validators=[validate_password])
    
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Пароли не совпадают'})
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        UserService.change_password(user=user, old_password=self.validated_data['old_password'],
                                    new_password=self.validated_data['new_password'])        


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer для запроса сброса пароля."""
    email = serializers.EmailField(required=True)

    def save(self, **kwargs):
        UserService.request_password_reset(email=self.validated_data['email'])


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer для подтверждения сброса пароля."""
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'},
                                        validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Пароли не совпадают'})
        return attrs

    def save(self, **kwargs):
        UserService.reset_password(token_value=str(self.validated_data['token']),
                                  new_password=self.validated_data['new_password'])


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer для верификации email."""
    token = serializers.UUIDField(required=True)

    def save(self, **kwargs):
        return UserService.verify_email(token_value=str(self.validated_data['token']))
