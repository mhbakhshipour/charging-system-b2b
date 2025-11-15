from django.db import models

from charging_system_b2b.utils.models.base_model import BaseModel


class Transaction(BaseModel):
    vendor = models.ForeignKey(
        "vendor.Vendor",
        on_delete=models.PROTECT,
        related_name="transactions_vendor",
        db_index=True,
    )
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.PROTECT,
        related_name="transactions_customer",
        db_index=True,
        blank=True,
        null=True,
    )
    amount = models.BigIntegerField(default=0)

    @property
    def is_vendor_credit(self):
        return bool(self.customer is None)

    def __str__(self):
        return f"vendor: {self.vendor.name} - customer: {self.customer.phone_number if self.customer else None} - {self.amount} - {self.created_at}"
