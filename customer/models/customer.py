from django.db import models

from charging_system_b2b.utils.models.base_model import BaseModel


class Customer(BaseModel):
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    current_balance = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(current_balance__gte=0),
                name="customer_current_balance_gte_0",
            )
        ]

    def __str__(self):
        return f"{self.phone_number}"
