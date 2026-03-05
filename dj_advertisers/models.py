from django.db import models

from .fields import PostgreSQLEnumField


class MonetizationType(models.TextChoices):
    CPC = "CPC", "CPC"
    CPA = "CPA", "CPA"


class BillingSource(models.TextChoices):
    INTERNAL = "INTERNAL", "Internal"
    PARTNER = "PARTNER", "Partner"


class BillingTimezone(models.TextChoices):
    UTC = "UTC", "UTC"
    EST = "EST", "Eastern"
    CST = "CST", "Central"
    PST = "PST", "Pacific"


class Advertiser(models.Model):
    name = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    default_conversion_rate = models.DecimalField(
        max_digits=6, decimal_places=4, default=0.01
    )
    monetization_type = PostgreSQLEnumField(
        "monetizationtype",
        max_length=20,
        choices=MonetizationType.choices,
        default=MonetizationType.CPC,
    )
    billing_source = PostgreSQLEnumField(
        "billingsource",
        max_length=20,
        choices=BillingSource.choices,
        default=BillingSource.INTERNAL,
    )
    billing_timezone = PostgreSQLEnumField(
        "timezone",
        max_length=10,
        choices=BillingTimezone.choices,
        default=BillingTimezone.UTC,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
