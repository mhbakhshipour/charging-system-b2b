from django.db import transaction

from transaction.models import Transaction
from vendor.models import Vendor
from customer.models import Customer


class TransactionService:

    @staticmethod
    @transaction.atomic
    def add_transaction(vendor: Vendor, amount: int, customer: Customer = None):
        new_transaction = Transaction.objects.create(
            vendor=vendor,
            customer=customer,
            amount=amount,
        )

        return new_transaction
