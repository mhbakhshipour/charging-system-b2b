from charging_system_b2b.utils.views import BaseModelViewSet

from transaction.models import Transaction
from transaction.serializers import TransactionSerializer


class TransactionViewSet(BaseModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    search_fields = ["vendor_name", "customer_phone_number"]
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save()
