from rest_framework.decorators import api_view
from rest_framework.response import Response

from customer.services import CustomerService
from customer.serializers import IncreaseCustomerCreditSerializer


@api_view(["POST"])
def increase_credit(request):
    serializer = IncreaseCustomerCreditSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    CustomerService.increase_credit(**serializer.validated_data)

    return Response({"data": serializer.data})
