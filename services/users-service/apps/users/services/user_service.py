import logging
from typing import Dict, Optional
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from users.models import User, UserProfile, EmailVerificationToken, PasswordResetToken
from users.utils.email_utils import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями."""
    
    @staticmethod
    @transaction.atomic
    def register_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra_fields
    ) -> User:
        """Регистрирует нового пользователя в системе."""
        logger.info(f'Начинаем регистрацию пользователя: {email}')
        
        if User.objects.email_exists(email):
            logger.warning(f'Попытка регистрации с существующим email: {email}')
            raise ValueError(f'Пользователь с email {email} уже существует.')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        
        UserProfile.objects.create(user=user)
        
        logger.info(f'Пользователь создан: {user.id} - {user.email}')
        
        # Отправляем email для верификации
        if settings.USER_SETTINGS.get('REQUIRE_EMAIL_VERIFICATION', True):
            try:
                UserService._create_and_send_verification_token(user)
            except Exception as e:
                logger.error(f'Ошибка при отправке письма верификации: {e}')
                # Не падаем, пользователь уже создан
                
        return user
    

    @staticmethod
    def _create_and_send_verification_token(user: User) -> EmailVerificationToken:
        """Создает токен верификации и отправляет email"""
        
        token = EmailVerificationToken.objects.create(user=user)
        
        # Отправляем письмо
        send_verification_email(user, token)
        
        logger.info(f'Токен верификации создан и отправлен: {user.email}')
        
        return token
    
    @staticmethod
    @transaction.atomic
    def verify_email(token_value: str) -> User:
        """
        Верифицирует email пользователя по токену.
        
        1) Находит токен по значению
        2) Проверяет что токен валиден (не истек, не использован)
        3) Помечает email как подтвержденный
        4) Помечает токен как использованный
        
        Пример: UserService.verify_email('3232-3-23-2323232-)
        """
        
        logger.info(f'Попытка верификации email с токеном: {token_value}')
        
        try:
            token = EmailVerificationToken.objects.get(token=token_value)
        except EmailVerificationToken.DoesNotExist:
            logger.warning(f'Токен не найден: {token_value}')
            raise ValueError('Токен верификации не найден.')
        
        if not token.is_valid():
            logger.warning(f'Токен невалиден: {token_value}, использован: {token.is_used}, истек: {token.is_expired}')
            raise ValueError('Токен верификации недействителен или истек.')
        
        # Обновляем пользователя
        user = token.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        
        # Помечаем токен как использованный
        token.is_used = True
        token.save(update_fields=['is_used'])
        
        logger.info(f'Email успешно верифицирован: {user.email}')
        
        return user
    
    @staticmethod
    def request_password_reset(email: str) -> None:
        """
        Инифиирует процесс сброса пароля.
        
        1) Находит пользователя по email
        2) Создает токен сброса пароля
        3) Отправляет письмо со ссылкой
        
        Пример: UserService.request_password_reset('test@example.com')
        """
        
        logger.info(f'Запрос на сброс пароля для: {email}')
        
        try:
            user = User.objects.get_by_email(email)
        except User.DoesNotExist:
            logger.warning(f'Попытка сброса пароля для несуществующего email: {email}')
            return
        
        token = PasswordResetToken.objects.create(user=user)
        
        # Отправляем письмо
        send_password_reset_email(user, token)
        
        logger.info(f'Письмо сброса пароля отправлено: {email}')
        
    @staticmethod
    @transaction.atomic
    def reset_password(token_value: str, new_password: str) -> User:
        """
        Сбрасывает пароль пользователя по токену.
        
        1) Находит токен
        2) Проверяет валидность
        3) Устанавливает новый пароль
        4) Помечает токен как использованный
        
        Пример: UserService.reset_password(
            '33232sdsk323023-2',
            'newpassword123'
        )
        """
        
        logger.info(f'Попытка сброса пароля с токеном: {token_value}')
        
        try:
            token = PasswordResetToken.objects.get(token=token_value)
        except PasswordResetToken.DoesNotExist:
            logger.warning(f'Токен сброса пароля не найден: {token_value}')
            raise ValueError('Токен сброса пароля не найден')
        
        if not token.is_valid:
            logger.warning(f'Токен сброса пароля невалиден: {token_value}')
            raise ValueError('Токен сброса пароля недействителен или истек')
        
        user = user.token
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        # Помечаем токен как использованный
        token.is_used = True
        token.save(update_fields=['is_useed'])
        
        logger.info(f'Пароль успешно сброшен для: {user.email}')
        
        return user
    
    @staticmethod
    @transaction.atomic
    def change_password(user: User, old_password: str, new_password: str) -> User:
        """
        Меняет пароль пользователя (требует знание старого пароля).
        
        1) Проверяет что старый пароль правильный
        2) Устанавливает новый пароль
        3) Логирует изменение
        
        Пример: UserService.change_password(user, 'oldpass', 'newpass')
        """
        
        logger.info(f'Попытка смены пароля для: {user.email}')
        
        # Проверяем старый пароль
        if not user.check_password(old_password):
            logger.warning(f'Неверный старый пароль для: {user.email}')
            raise ValueError('Неверный текущий пароль.')
        
        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        logger.info(f'Пароль успешно изменен для: {user.email}')
        
        return user
    
    @staticmethod
    def update_profile(user: User, **profile_data) -> User:
        """
        Обновляет профиль пользователя.
        
        Пример: user = UserService.update_profile(
            user,
            bio='Электрик',
            city='Москва'
        )
        """
        logger.info(f'Обновление профиля для: {user.email}')
        
        profile = user.profile
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.save()
        
        logger.info(f'Профиль обновлен для: {user.email}')
        
        return user
    
    @staticmethod
    def resend_verification_email(user: User) -> None:
        """
        Повторно отправляет письмо для верификации email.
        
        Пример: UserService.resend_verification_email(user)
        """
        
        if user.is_email_verified:
            raise ValueError('Email уже подтвержден')
        
        # Деактивируем старые токены
        EmailVerificationToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
        
        # Создаем и отправляем новый токен
        UserService._create_and_send_verification_token(user)
        
        logger.info(f'Письмо верификации отправлено повторно: {user.email}')
        
        
        
        
        
