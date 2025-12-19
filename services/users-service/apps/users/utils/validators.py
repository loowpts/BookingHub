import re
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Проверяет корректность номер телефона.
    
    Пример: phone = serializers.CharField(validators=[validate_phone_number])
    """

    if not value:
        return
    
    # Убираем все кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', value)
    
    pattern = r'^\+?[78][\d]{10}$'
    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('Некорректный формат номер телефона. Используйте формат: +79991234567'),
            code='invalid_phone'
        )

def validate_password_strength(password):
    """
    Проверяет надежность пароля.
    
    Пример:
    validate_password_strength('MyPass123) # Ok
    validate_password_strength('weak) # ValidationError
    """
    
    if len(password) < 8:
        raise ValidationError(
            _('Пароль должен содержать минимум 8 символов.'),
            code='password_too_short'
        )
        
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну заглавную букву'),
            code='password_no_upper'
        )
        
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну строчную букву'),
            code='password_no_lower'
        )
    
    if not re.search(r'\d', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну цифру'),
            code='password_no_digit'
        )
        
def validate_age(birth_date):
    """Проверяет что пользователю есть 18 лет."""
    if not birth_date:
        return
    
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    
    if age < 18:
        raise ValidationError(
            _('Вам должно быть минимум 18 лет.'),
            code='age_too_young'
        )
    
    
    
