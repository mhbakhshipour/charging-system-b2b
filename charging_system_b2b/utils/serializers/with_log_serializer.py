from rest_framework import serializers


class WithLogserializer(serializers.ModelSerializer):
    histories = serializers.ReadOnlyField()

    def to_representation(self, instance):
        response = super().to_representation(instance)

        response["histories"] = sorted(
            instance.histories, key=lambda obj: obj["change_date"], reverse=True
        )

        return response
