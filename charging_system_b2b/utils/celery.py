from celery import Task
from redlock import RedLock

from charging_system_b2b.settings import CELERY_BROKER_URL


class RedlockedTask(Task):
    def __call__(self, *args, **kwargs):
        dlm = RedLock(
            f"celery:task:{self.name}", connection_details=[{"url": CELERY_BROKER_URL}]
        )
        lock = dlm.acquire()
        if not lock:
            print(f"[{self.name}] Redlock not acquired.")
            return
        try:
            return super().__call__(*args, **kwargs)
        finally:
            dlm.release()
