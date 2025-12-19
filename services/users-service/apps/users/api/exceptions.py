from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF.

    Вызывается при любой ошибке в API.
    Форматирует ответ в единый формат:
    {
        "error": {
            "message": "Текст ошибки",
            "code": "error_code",
            "details": {...}
        }
    }
    """
    
    # Вызываем стандартный обработчик
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'error': {
                'message': str(exc),
                'code': getattr(exc, 'default_code', 'error'),
            }
        }
        
        # Добавляем детали, если есть
        if isinstance(response.data, dict):
            custom_response['error']['details'] = response.data
        else:
            custom_response['error']['details'] = {'detail': response.data}
        
        response.data = custom_response
    
    return response

class EmailAlreadyExistsError(APIException):
    """Исключение когда email уже существует."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Пользоватеоь с таким email уже существует'
    default_code = 'email_exists'
    
    
class InvalidTokenError(APIException):
     """Исключение когда токен невалиден."""
     status_code = status.HTTP_400_BAD_REQUEST
     default_detail = 'Токен невалиден или истек'
     default_code = 'invalid_token'
     
     
class InvalidCredentialsError(APIException):
    """Исключение когда неверные данные для входа."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Неверный email или пароль'
    default_code = 'invalid_credentials'
