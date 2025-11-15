from django.db import transaction

from transaction.services import TransactionService

from vendor.models import Vendor
from customer.models import Customer


class CustomerService:

    @staticmethod
    @transaction.atomic
    def increase_credit(vendor: Vendor, amount: int, customer: Customer):
        new_transaction = TransactionService.add_transaction(
            vendor=vendor,
            customer=customer,
            amount=amount,
        )

        return new_transaction
