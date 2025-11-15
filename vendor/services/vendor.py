from django.db import transaction, models

from vendor.models import Vendor
from transaction.services import TransactionService


class VendorCreditService:

    @staticmethod
    @transaction.atomic
    def increase_credit(vendor: Vendor, amount: int):
        TransactionService.add_transaction(vendor=vendor, amount=amount)

        return vendor

    @staticmethod
    @transaction.atomic
    def decrease_credit(vendor: Vendor, amount: int):
        TransactionService.add_transaction(vendor=vendor, amount=amount)

        return vendor
