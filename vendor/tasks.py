from celery.utils.log import get_task_logger
from redlock import RedLock

from charging_system_b2b.celery import app
from charging_system_b2b.settings import CELERY_BROKER_URL

from vendor.models import RequestCredit
from vendor.services import RequestCreditService


logger = get_task_logger(__name__)


@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 10, "countdown": 5})
def approve_request_credit_task(self, request_credit_id: int):
    dlm = RedLock(
        f"approve_request_credit:{request_credit_id}",
        connection_details=[{"url": CELERY_BROKER_URL}],
    )
    lock = dlm.acquire()
    if not lock:
        return
    try:
        request_credit = RequestCredit.objects.get(id=request_credit_id)
        RequestCreditService.confirm_request_credit(request_credit)
    finally:
        dlm.release()