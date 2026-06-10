from django.contrib.auth.models import UserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from typing import Any, Optional

def validate_email_address(email: str) -> None:
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError(_('Invalid email address'))

class CustomUserManager(UserManager):
    # Custom user manager to handle user creation with email as the unique identifier instead of username
    
    def _create_user(self, email: str, password: str, **extra_fields: Any) -> Any:
        if not email:
            raise ValueError(_('An email address is required'))

        if not password:
            raise ValueError(_('A password is required'))
        
        email = self.normalize_email(email)
        validate_email_address(email)
        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> Any:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
            
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)