from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission: пользователь может редактировать только свой профиль, админ - любой.

    Используется в UserViewSet для методов update, partial_update, destroy.

    Пример:
        class UserViewSet(viewsets.ModelViewSet):
            permission_classes = [IsOwnerOrAdmin]
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверяет есть ли доступ к конкретному объекту."""
        # админ может все
        if request.user.is_staff:
            return True
        
        # Пользоватеоь может редактировать только себя
        return obj == request.user
    

class IsEmailVerified(permissions.BasePermission):
    """
    Permission: доступ только для пользователей с подтвержденным email.

    Можно использовать для защиты критичных endpoints.

    Пример:
        class SensitiveDataView(APIView):
            permission_classes = [IsAuthenticated, IsEmailVerified]
    """
    
    message = 'Подтвердите ваш email для доступа к этому ресурсу'
    
    def has_permission(self, request, view):
        """Проверяет подтвержден ли email у пользователя."""
        return request.user and request.user.is_authenticated and request.user.is_email_verified


class IsNotAuthenticated(permissions.BasePermission):
    """
    Permission: доступ только для неавторизованных пользователей.

    Используется для endpoints типа регистрация, вход.

    Пример:
        class RegisterView(APIView):
            permission_classes = [IsNotAuthenticated]
    """

    message = 'Вы уже авторизованы'
    
    def has_permission(self, request, view):
        """Проверяет что пользовател не авторизован."""
        return not (request.user and request.user.is_authenticated)

