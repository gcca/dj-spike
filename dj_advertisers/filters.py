import django_filters
from django_filters import (
    CharFilter,
    ChoiceFilter,
    IsoDateTimeFromToRangeFilter,
    NumberFilter,
)

from .models import Advertiser, BillingSource, BillingTimezone, MonetizationType


class AdvertiserFilterSet(django_filters.FilterSet):
    created_at = IsoDateTimeFromToRangeFilter(field_name="created_at")
    updated_at = IsoDateTimeFromToRangeFilter(field_name="updated_at")
    name = CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = CharFilter(field_name="name", lookup_expr="icontains")
    monetization_type = ChoiceFilter(
        field_name="monetization_type",
        choices=MonetizationType.choices,
    )
    billing_source = ChoiceFilter(
        field_name="billing_source",
        choices=BillingSource.choices,
    )
    billing_timezone = ChoiceFilter(
        field_name="billing_timezone",
        choices=BillingTimezone.choices,
    )
    discount = NumberFilter(field_name="discount", lookup_expr="exact")
    discount__gte = NumberFilter(field_name="discount", lookup_expr="gte")
    discount__lte = NumberFilter(field_name="discount", lookup_expr="lte")
    discount__gt = NumberFilter(field_name="discount", lookup_expr="gt")
    discount__lt = NumberFilter(field_name="discount", lookup_expr="lt")
    default_conversion_rate = NumberFilter(
        field_name="default_conversion_rate", lookup_expr="exact"
    )
    default_conversion_rate__gte = NumberFilter(
        field_name="default_conversion_rate", lookup_expr="gte"
    )
    default_conversion_rate__lte = NumberFilter(
        field_name="default_conversion_rate", lookup_expr="lte"
    )
    default_conversion_rate__gt = NumberFilter(
        field_name="default_conversion_rate", lookup_expr="gt"
    )
    default_conversion_rate__lt = NumberFilter(
        field_name="default_conversion_rate", lookup_expr="lt"
    )

    class Meta:
        model = Advertiser
        fields = []
