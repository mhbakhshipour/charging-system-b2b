from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        return Response(
            {"message": exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, list):
            return Response(
                {"message": exc.detail[0]}, status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc.detail, dict):
            first_key = next(iter(exc.detail))
            first_msg = exc.detail[first_key]
            if isinstance(first_msg, list):
                return Response(
                    {"message": first_msg[0]}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response({"message": first_msg}, status=status.HTTP_400_BAD_REQUEST)

    return exception_handler(exc, context)
