from charging_system_b2b.utils.serializers.base_model_serializer import (
    BaseModelserializer,
)

from transaction.models import Transaction


class TransactionSerializer(BaseModelserializer):
    class Meta:
        model = Transaction
        fields = ["vendor", "customer", "amount", "created_at", "updated_at"]
