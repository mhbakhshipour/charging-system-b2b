from django.http import HttpRequest
from django.db.models.query import QuerySet
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from charging_system_b2b.utils.pagination import ResultsSetPagination


def prepare_response(
    queryset: QuerySet,
    request: HttpRequest,
    serializer: Serializer,
    is_serializer_many: bool = False,
    has_pagination: bool = False,
) -> Response:
    # Paginate the queryset
    paginator = ResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Serialize the paginated queryset
    serialized_data = serializer(
        paginated_queryset, many=is_serializer_many, context={"request": request}
    )

    if not has_pagination:
        response = serialized_data.data
        return Response(response)

    # Return the paginated response
    response = paginator.get_paginated_response(serialized_data.data)
    return response
