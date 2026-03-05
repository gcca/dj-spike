from rest_framework import serializers

from .models import Advertiser


class AdvertiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertiser
        fields = [
            "id",
            "name",
            "discount",
            "default_conversion_rate",
            "monetization_type",
            "billing_source",
            "billing_timezone",
            "created_at",
            "updated_at",
        ]
