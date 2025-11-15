from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from charging_system_b2b.utils.views import BaseModelViewSet

from vendor.models import RequestCredit
from vendor.serializers import RequestCreditSerializer
from vendor.services import RequestCreditService


class RequestCreditViewSet(BaseModelViewSet):
    queryset = RequestCredit.objects.all()
    serializer_class = RequestCreditSerializer
    search_fields = ["requester__name"]
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve_request(self, request, pk=None):
        request_credit = self.get_object()
        RequestCreditService.confirm_request_credit(request_credit)
        return Response({"status": "Request credit approved"})
