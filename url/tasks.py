from celery import shared_task
from django.db.models import F
from django.core.cache import cache
from .models import ShortURL


@shared_task
def sync_click_counts():
    client = cache.client.get_client()

    for key in client.scan_iter("clicks:*"):
        key_str = key.decode("utf-8") if isinstance(key, bytes) else key
        short_code = key_str.split(":", 1)[1]

        click_count = client.get(key)

        if not click_count:
            continue

        click_count_val = int(
            click_count.decode("utf-8")
            if isinstance(click_count, bytes)
            else click_count
        )

        if click_count_val <= 0:
            continue

        ShortURL.objects.filter(
            short_code=short_code
        ).update(
            click_count=F("click_count") + click_count_val
        )

        client.delete(key)