from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from charging_system_b2b.utils.filters import DjangoFilterBackend
from charging_system_b2b.utils.permissions import IsOwnerOrReadOnly
from charging_system_b2b.utils.pagination import ResultsSetPagination


class BaseModelViewSet(ModelViewSet):
    filterset_fields = "__all__"
    search_fields = "__all__"
    ordering_fields = "__all__"
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        has_pagination = request.GET.get("has_pagination", "true")

        if has_pagination == "false":
            self.pagination_class = None
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
