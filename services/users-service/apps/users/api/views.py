from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from users.api.serializers import (
    UserSerializer, UserRegistrationSerializer, UserUpdateSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)
from users.api.permissions import IsOwnerOrAdmin
from users.services import UserService


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""
    
    queryset = User.objects.select_related('profile').active()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_email_verified', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    
    def get_queryset(self):
        """
        Кастомизирует queryset в зависимости от пользователя.

        Обычные пользователи видят только себя.
        Админы видят всех.
        """
        if self.request.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """
        Возвращает разные serializers для разных actions.

        - list/retrieve: UserSerializer (чтение)
        - update/partial_update: UserUpdateSerializer (обновление)
        - me: зависит от метода
        """              
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        Получить или обновить данные текущего пользователя.

        GET /api/v1/users/me/ - получить свои данные
        PATCH /api/v1/users/me/ - обновить свои данные

        @action - декоратор для создания кастомного endpoint
        detail=False - URL без ID (/users/me/ а не /users/{id}/me/)
        methods - какие HTTP методы разрешены
        """
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserUpdateSerializer(
                request.user,
                data=request.data,
                partial=True # Разрешаем частичное обновление
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(request.user).data)
        
    @action(detail=False, methods=['patch'], url_path='me/profile')
    def update_profile(self, request):
        """
        Обновить профиль текущего пользователя.

        PATCH /api/v1/users/me/profile/
        """   
        profile = request.user
        serializer = UserUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )   
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.data).data)
    
    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """
        Сменить пароль текущего пользователя.

        POST /api/v1/users/me/change-password/
        Body: {
            "old_password": "old",
            "new_password": "new",
            "new_password_confirm": "new"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )     
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен'},
            status=status.HTTP_200_OK
        )


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.

    POST /api/v1/users/register/
    Body: {
        "email": "user@example.com",
        "password": "SecurePass123",
        "password_confirm": "SecurePass123",
        "first_name": "Иван",
        "last_name": "Иванов"
    }

    CreateAPIView автоматически:
    - Принимает POST запрос
    - Валидирует через serializer
    - Вызывает serializer.save()
    - Возвращает созданный объект
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Переопределяем create для кастомного ответа."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'detail': 'Регистрация успешна. Проверьте email для подтверждения.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class EmailVerificationView(generics.GenericAPIView):
    """
    Подтверждение email адреса.

    POST /api/v1/users/verify-email/
    Body: {
        "token": "uuid-token"
    }
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'detail': 'Email успешно подтверждене',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )
        

class PasswordResetRequestView(generics.GenericAPIView):
    """
    Запрос на сброс пароля.

    POST /api/v1/users/password-reset/
    Body: {
        "email": "user@example.com"
    }
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Обрабатываем запрос на сброс пароля."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'detail': 'На ваш email отправлена инструкция по сбросу пароля.'
            },
            status=status.HTTP_200_OK
        )
 
 
class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Подтверждение сброса пароля.

    POST /api/v1/users/password-reset/confirm/
    Body: {
        "token": "uuid-token",
        "new_password": "NewPass123",
        "new_password_confirm": "NewPass123"
    }
    """     
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'detail': 'Пароль успешно изменен',
            },
            status=status.HTTP_200_OK
        )

class ResendVerificationEmailView(generics.GenericAPIView):
    """
    Повторная отправка письма верификации.

    POST /api/v1/users/resend-verification/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            UserService.resend_verification_email(request.user)
            return Response(
                {'detail': 'Письмо верификации отправлено повторно'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
