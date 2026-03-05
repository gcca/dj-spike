from django.test import TestCase

from dj_advertisers.models import (
    Advertiser,
    BillingSource,
    BillingTimezone,
    MonetizationType,
)


class AdvertiserModelTest(TestCase):
    def test_create_with_defaults(self):
        a = Advertiser.objects.create(name="Acme")
        self.assertEqual(a.discount, 0)
        self.assertEqual(a.default_conversion_rate, 0.01)
        self.assertEqual(a.monetization_type, MonetizationType.CPC)
        self.assertEqual(a.billing_source, BillingSource.INTERNAL)
        self.assertEqual(a.billing_timezone, BillingTimezone.UTC)

    def test_create_with_explicit_values(self):
        a = Advertiser.objects.create(
            name="Acme Corp",
            discount=0.05,
            default_conversion_rate=0.02,
            monetization_type=MonetizationType.CPA,
            billing_source=BillingSource.PARTNER,
            billing_timezone=BillingTimezone.EST,
        )
        self.assertEqual(a.name, "Acme Corp")
        self.assertEqual(a.discount, 0.05)
        self.assertEqual(a.default_conversion_rate, 0.02)
        self.assertEqual(a.monetization_type, MonetizationType.CPA)
        self.assertEqual(a.billing_source, BillingSource.PARTNER)
        self.assertEqual(a.billing_timezone, BillingTimezone.EST)
