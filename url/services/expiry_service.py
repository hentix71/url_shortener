from datetime import timedelta
from django.utils import timezone


def calculate_expiry(life_time):
    now = timezone.now()

    match life_time:
        case "1h":
            return now + timedelta(hours=1)

        case "1d":
            return now + timedelta(days=1)

        case "1w":
            return now + timedelta(weeks=1)

        case "never":
            return None

        case _:
            return None