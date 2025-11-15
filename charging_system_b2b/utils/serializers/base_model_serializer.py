from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError


class BaseModelserializer(serializers.ModelSerializer):
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise DRFValidationError(e.message_dict)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise DRFValidationError(e.message_dict)
