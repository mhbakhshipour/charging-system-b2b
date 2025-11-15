from rest_framework import serializers


from charging_system_b2b.utils.serializers.base_model_serializer import (
    BaseModelserializer,
)

from customer.models.customer import Customer
from transaction.models import Transaction


class CustomerSerializer(BaseModelserializer):
    class Meta:
        model = Customer
        fields = ["phone_number", "current_balance", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class IncreaseCustomerCreditSerializer(BaseModelserializer):
    customer = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Customer.objects.all()
    )

    class Meta:
        model = Transaction
        fields = ["vendor", "customer", "amount", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
