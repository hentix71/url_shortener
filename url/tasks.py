from celery import shared_task
from django.db.models import F
from .models import ShortURL
from django.core.cache import cache

@shared_task
def sync_click_counts():
    client = cache.client.get_client()
    for key in client.scan_iter("clicks:*"):
        short_code = key.split(":", 1)[1]
        click_count = client.get(key)
        if not click_count or int(click_count) <= 0:
            continue
        ShortURL.objects.filter(short_code=short_code).update(
            click_count=F('click_count') + int(click_count)
        )
        client.delete(key)