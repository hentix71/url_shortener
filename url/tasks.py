from celery import shared_task
from django.db.models import F


from .models import ShortURL
from .services.redis_service import redis_client

@shared_task
def sync_click_counts():

    print("starting syncing click counts...")
    for key in redis_client.scan_iter("clicks:*"):
        short_code = key.split(":",1 )[1]

        click_count = redis_client.get(key)
        if not click_count:
            continue

        if click_count <= 0:
            continue
        click_count = int(click_count)
        ShortURL.objects.filter(
            short_code=short_code
            ).update(
                click_count=F('click_count') + click_count
                )
        redis_client.delete(key)    
    print("Finished syncing click counts.")