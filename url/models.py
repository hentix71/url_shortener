from django.db import models
from account.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class ShortURL(models.Model):

    class LifeDurationChoices(models.TextChoices):
        ONE_HOUR = '1h', _('1 Hour')
        ONE_DAY = '1d', _('1 Day')
        ONE_WEEK = '1w', _('1 Week')
        NEVER = 'never', _('Never') 

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='short_urls'
    )

    original_url = models.URLField()

    short_code = models.CharField(
        max_length=7, 
        unique=True
    )

    click_count = models.PositiveIntegerField(
        default=0,
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )


    life_time = models.CharField(
        max_length=10,
        default = LifeDurationChoices.NEVER,
        choices= LifeDurationChoices.choices,
        verbose_name = _("URL Duration")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name = _("Active Status")
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    @property
    def is_expired(self):
        return (
            self.expires_at is not None and self.expires_at <= timezone.now()
        )

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"