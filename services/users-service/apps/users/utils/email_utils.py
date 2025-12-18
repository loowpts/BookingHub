import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_verification_email(user, token):
    """
    Отправляет письмо с ссылкой для верификации email.
    
    Пример: send_verification_email(user, verification_token)
    """
    subject = 'Подтвердите ваш email'
    
    verification_link = f'{settings.FRONTEND_URL}/verify-email/{token.token}'
    
    message = f"""
    Здраствуйте, {user.get_short_name()}!
    
    Спасибо за регистрацию. Пожалуйста, подтвердите ваш email адрес, перейдя по ссылке:
    
    {verification_link}
    
    Ссылка действительна в течение 24 часов.
    
    Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.
    
    С уважением,
    Команда сайта.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Письмо верификации отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки письма верификации на {user.email}: {e}')
        raise
    

def send_password_reset_email(user, token):
    """
    Отправляет письмо со ссылкой для сброса пароля.
    
    Пример: send_password_reset_email(user, reset_token)
    """
    
    subject = 'Сброс пароля'
    
    # Формируем ссылку для сброса пароля
    reset_link = f'{settings.FRONTEND_URL}/reset-password/{token.token}'
    
    message = f"""
    Здраствуйте, {user.get_short_name()}!
    
    Вы запросили сброс пароля. Перейдите по ссылке для установки нового пароля:
    
    {reset_link}
    
    Ссылка действительная в течение 1 часа.
    
    Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
    
    С уважением,
    Команда сайта
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Письмо сброса пароля отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки письма сброса пароля на {user.email}: {e}')
        raise
    
def send_welcome_email(user):
    """
    Отправляет приветственное письмо после верификации.
    
    send_welcome_email(user)
    """
    
    subject = 'Добро пожаловать'
    
    message = f"""
    Здраствуйте, {user.get_short_name()}!
    
    Спасибо за подтверждение email адреса!
    
    Теперь вы можете пользоваться всеми возможностями нашего сервиса.
    
    С уважением,
    Команда сайта
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Приветственное письмо отправлено на: {user.email}')
    except Exception as e:
        logger.error(f'Ошибка отправки приветственного письма на {user.email}: {e}')
        pass
    
    
