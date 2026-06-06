from django.db import models
from account.models import User


class ShortURL(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='short_urls'
    )

    original_url = models.URLField()

    short_code = models.CharField(
        max_length=10, 
        unique=True
    )

    click_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the short URL has been accessed."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"