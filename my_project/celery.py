from celery import Celery
import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "my_project.settings"
)

app = Celery("my_project")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()

# for django-celery-beat
app.conf.beat_scheduler = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)