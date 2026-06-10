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

app.conf.beat_scheduler = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)

app.conf.beat_schedule = {
    "sync-click-counts-every-60-seconds": {
        "task": "url.tasks.sync_click_counts",
        "schedule": 60.0,
    },
}