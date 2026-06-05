from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

from account.managers import CustomUserManager
class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    email = models.EmailField(
        verbose_name=_('email address'), 
        unique=True
    )
    username = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_('username')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]

    def __str__(self):
        return self.email