from django.core.cache import cache


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
    
    cache.set(short_code, original_url, timeout)


def get_cached_short_url(short_code):
    # Retrieve the original URL from the cache using the short code
    
    return cache.get(short_code)


def increment_click_count(short_code):
    # Increment the click count for the given short code

    count_key = f"clicks:{short_code}"

    try:
        cache.incr(count_key)
    except ValueError:
        cache.set(count_key, 1)