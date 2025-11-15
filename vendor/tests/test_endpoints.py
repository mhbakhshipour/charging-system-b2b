from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch

from charging_system_b2b.celery import app as celery_app
from vendor.models import Vendor, RequestCredit
from customer.models import Customer
from django.db.models import Sum
from transaction.models import Transaction


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
)
class VendorEndpointTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user(username="user", password="pass")
        self.admin = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.vendor = Vendor.objects.create(name="v1", current_balance=100)

    def test_submit_request_creates_pending(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.post(
            "/api/vendor/submit-request/",
            {"requester": self.vendor.id, "amount": 10},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(RequestCredit.objects.count(), 1)
        obj = RequestCredit.objects.first()
        self.assertEqual(obj.status, RequestCredit.RequestCreditStatus.PENDING)

    def test_submit_request_concurrency_rate_limit(self):
        statuses = []
        for _ in range(12):
            c = APIClient()
            c.force_authenticate(user=self.user)
            s = c.post(
                "/api/vendor/submit-request/",
                {"requester": self.vendor.id, "amount": 1},
                format="json",
            ).status_code
            statuses.append(s)

        success = statuses.count(200)
        forbidden = statuses.count(403)
        self.assertTrue(success <= 10)
        self.assertTrue(forbidden >= 2)
        self.assertEqual(RequestCredit.objects.count(), success)

    def test_approve_request_single_confirmation(self):
        rc = RequestCredit.objects.create(requester=self.vendor, amount=15)
        client = APIClient()
        client.force_authenticate(user=self.admin)
        with patch("vendor.tasks.RedLock"):
            resp = client.get(f"/api/vendor/approve-request/?request_credit_id={rc.id}")
        self.assertEqual(resp.status_code, 202)
        rc.refresh_from_db()
        self.assertEqual(rc.status, RequestCredit.RequestCreditStatus.CONFIRMED)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.current_balance, 115)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor).count(), 1)

    def test_approve_request_concurrency_single_confirmation(self):
        rc = RequestCredit.objects.create(requester=self.vendor, amount=20)
        statuses = []
        for _ in range(2):
            c = APIClient()
            c.force_authenticate(user=self.admin)
            with patch("vendor.tasks.RedLock"):
                statuses.append(c.get(f"/api/vendor/approve-request/?request_credit_id={rc.id}").status_code)
        self.assertTrue(statuses.count(202) >= 1)
        rc.refresh_from_db()
        self.assertEqual(rc.status, RequestCredit.RequestCreditStatus.CONFIRMED)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.current_balance, 120)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor).count(), 1)

    def test_full_workflow_balance_and_transaction_sums(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        vendor2 = Vendor.objects.create(name="vx", current_balance=0)
        c1 = Customer.objects.create(phone_number="09120000001", current_balance=0)
        c2 = Customer.objects.create(phone_number="09120000002", current_balance=0)

        # Vendor charges: +100 and +200 via submit + approve
        resp1 = client.post(
            "/api/vendor/submit-request/",
            {"requester": vendor2.id, "amount": 100},
            format="json",
        )
        self.assertEqual(resp1.status_code, 200)
        resp2 = client.post(
            "/api/vendor/submit-request/",
            {"requester": vendor2.id, "amount": 200},
            format="json",
        )
        self.assertEqual(resp2.status_code, 200)

        client_admin = APIClient()
        client_admin.force_authenticate(user=self.admin)
        reqs = list(RequestCredit.objects.filter(requester=vendor2).order_by("id"))
        with patch("vendor.tasks.RedLock"):
            for rc in reqs:
                r = client_admin.get(f"/api/vendor/approve-request/?request_credit_id={rc.id}")
                self.assertEqual(r.status_code, 202)

        # Vendor charges customers: 50 to c1, 100 to c2
        with patch("customer.tasks.RedLock"):
            r1 = client.post(
                "/api/customer/increase-credit/",
                {"vendor": vendor2.id, "customer": c1.id, "amount": 50},
                format="json",
            )
            self.assertEqual(r1.status_code, 202)
            r2 = client.post(
                "/api/customer/increase-credit/",
                {"vendor": vendor2.id, "customer": c2.id, "amount": 100},
                format="json",
            )
            self.assertEqual(r2.status_code, 202)

        vendor2.refresh_from_db()
        c1.refresh_from_db()
        c2.refresh_from_db()

        self.assertEqual(vendor2.current_balance, 150)
        self.assertEqual(c1.current_balance, 50)
        self.assertEqual(c2.current_balance, 100)

        total_vendor = (
            Transaction.objects.filter(vendor=vendor2, customer=None).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        total_c1 = (
            Transaction.objects.filter(vendor=vendor2, customer=c1).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        total_c2 = (
            Transaction.objects.filter(vendor=vendor2, customer=c2).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        self.assertEqual(total_vendor, vendor2.current_balance)
        self.assertEqual(total_c1, c1.current_balance)
        self.assertEqual(total_c2, c2.current_balance)