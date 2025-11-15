import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "charging_system_b2b.settings")

app = Celery("task")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
