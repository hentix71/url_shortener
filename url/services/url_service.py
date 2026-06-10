from ..models import ShortURL
from .redis_service import get_next_id
from .expiry_service import calculate_expiry
from ..utils.encoder import encode_base62, random_prefix


def create_short_url(user, validated_data):
    # Generate a unique short code and create a ShortURL instance

    # Extract necessary data from the request
    original_url = validated_data.get('original_url')
    life_time = validated_data.get('life_time', ShortURL.LifeDurationChoices.NEVER)
    short_code = validated_data.get('short_code')
    
    if not short_code:
        while True:
            # Generate a unique short code
            unique_id = get_next_id()
            base = encode_base62(unique_id)
            prefix = random_prefix(2)
            short_code = f"{prefix}{base}"

            if not ShortURL.objects.filter(short_code=short_code).exists():
                break
    
    expires_at = calculate_expiry(life_time)

    short_url_obj = ShortURL.objects.create(
        user=user,
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at
    )
    return short_url_obj