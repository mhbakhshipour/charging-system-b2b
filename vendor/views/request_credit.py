from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from vendor.models import RequestCredit
from vendor.serializers import RequestCreditSerializer
from vendor.services import RequestCreditService
from vendor.tasks import approve_request_credit_task


@api_view(["POST"])
def submit_request(request):
    serializer = RequestCreditSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"data": serializer.data})


@api_view(["GET"])
@permission_classes([IsAdminUser])
def approve_request(request):
    request_credit_id = request.query_params.get("request_credit_id")
    try:
        request_credit = RequestCredit.objects.get(id=request_credit_id)
    except RequestCredit.DoesNotExist:
        return Response({"error": "Bad Param"}, status=400)
    approve_request_credit_task.delay(request_credit.id)
    return Response({"status": "accepted"}, status=202)
