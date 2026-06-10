from django.core.cache import cache
import redis
from decouple import config

ID_KEY = "url:id:counter"
def get_next_id():
    # Get the next unique ID for a new short URL
    
    try:
        return cache.incr(ID_KEY)
    except ValueError:
        cache.set(ID_KEY, 100000)
        return cache.incr(ID_KEY)


def cache_short_url(short_code, original_url, timeout=1800):
    # Cache the short URL with a timeout (default: 30 minutes)
    key = f"short_code:{short_code}"
    cache.set(
        key,
        {
            "original_url": original_url
        },
        timeout=timeout
    )


def get_cached_short_url(short_code):
    # Retrieve the original URL from the cache using the short code
    
    key = f"short_code:{short_code}"
    return cache.get(key)


def increment_click_count(short_code):
    # Increment the click count for the given short code
    
    count_key = f"clicks:{short_code}"

    cache.add(count_key, 0)  
    return cache.incr(count_key)