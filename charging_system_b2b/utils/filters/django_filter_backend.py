from django.db.models.fields import TextField
from django.db.models.fields.files import FileField, ImageField
from django_filters.rest_framework import DjangoFilterBackend

NOT_ALLOWED_FILTER_TYPES = FileField | ImageField | TextField


class DjangoFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        """
        Return the `FilterSet` class used to filter the queryset.
        """
        filterset_class = getattr(view, "filterset_class", None)
        filterset_fields = getattr(view, "filterset_fields", None)

        if filterset_fields == "__all__":
            filterset_fields = [
                field.name
                for field in queryset.model._meta.get_fields()
                if not isinstance(field, NOT_ALLOWED_FILTER_TYPES)
            ]

        if filterset_class:
            filterset_model = filterset_class._meta.model

            # FilterSets do not need to specify a Meta class
            if filterset_model and queryset is not None:
                assert issubclass(
                    queryset.model, filterset_model
                ), "FilterSet model %s does not match queryset model %s" % (
                    filterset_model,
                    queryset.model,
                )

            return filterset_class

        if filterset_fields and queryset is not None:
            MetaBase = getattr(self.filterset_base, "Meta", object)

            class AutoFilterSet(self.filterset_base):
                class Meta(MetaBase):
                    model = queryset.model
                    fields = filterset_fields

            return AutoFilterSet

        return None
