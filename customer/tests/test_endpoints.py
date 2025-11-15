from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch

from charging_system_b2b.celery import app as celery_app
from vendor.models import Vendor
from customer.models import Customer
from transaction.models import Transaction


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
)
class CustomerEndpointTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user(username="user", password="pass")
        self.vendor = Vendor.objects.create(name="v2", current_balance=50)
        self.customer = Customer.objects.create(phone_number="09121234567", current_balance=0)

    def test_increase_credit_single(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        with patch("customer.tasks.RedLock"):
            resp = client.post(
                "/api/customer/increase-credit/",
                {"vendor": self.vendor.id, "customer": self.customer.id, "amount": 10},
                format="json",
            )
        self.assertEqual(resp.status_code, 202)
        self.vendor.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertEqual(self.vendor.current_balance, 40)
        self.assertEqual(self.customer.current_balance, 10)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor, customer=None).count(), 1)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor, customer=self.customer).count(), 1)

    def test_increase_credit_concurrency_aggregates(self):
        statuses = []
        for _ in range(2):
            c = APIClient()
            c.force_authenticate(user=self.user)
            with patch("customer.tasks.RedLock"):
                statuses.append(
                    c.post(
                        "/api/customer/increase-credit/",
                        {"vendor": self.vendor.id, "customer": self.customer.id, "amount": 5},
                        format="json",
                    ).status_code
                )
        self.assertTrue(all(s == 202 for s in statuses))
        self.vendor.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertEqual(self.vendor.current_balance, 40)
        self.assertEqual(self.customer.current_balance, 10)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor, customer=None).count(), 2)
        self.assertEqual(Transaction.objects.filter(vendor=self.vendor, customer=self.customer).count(), 2)