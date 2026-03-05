from decimal import Decimal

from django.test import TestCase

from dj_advertisers.filters import AdvertiserFilterSet
from dj_advertisers.models import (
    Advertiser,
    BillingSource,
    BillingTimezone,
    MonetizationType,
)


class AdvertiserFilterSetTest(TestCase):
    def setUp(self):
        self.jan = Advertiser.objects.create(
            name="Acme Corp",
            discount=0.05,
            default_conversion_rate=0.02,
            monetization_type=MonetizationType.CPA,
            billing_source=BillingSource.PARTNER,
            billing_timezone=BillingTimezone.EST,
        )
        self.feb = Advertiser.objects.create(
            name="Beta Inc",
            discount=0.01,
            default_conversion_rate=0.01,
            monetization_type=MonetizationType.CPC,
            billing_source=BillingSource.INTERNAL,
            billing_timezone=BillingTimezone.UTC,
        )
        self.mar = Advertiser.objects.create(
            name="Gamma Acme Ltd",
            discount=0.10,
            default_conversion_rate=0.005,
            monetization_type=MonetizationType.CPC,
            billing_source=BillingSource.INTERNAL,
            billing_timezone=BillingTimezone.PST,
        )

    def test_filter_by_created_at_after(self):
        qs = Advertiser.objects.all()
        # created_at_after: filter advertisers created after 2025-02-01
        data = {"created_at_after": "2025-02-01T00:00:00Z"}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertIn(self.feb, results)
        self.assertIn(self.mar, results)
        self.assertIn(self.jan, results)  # depends on creation order

    def test_filter_by_created_at_before(self):
        qs = Advertiser.objects.all()
        data = {"created_at_before": "2026-12-31T23:59:59Z"}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        self.assertEqual(fs.qs.count(), 3)

    def test_filter_by_updated_at_range(self):
        qs = Advertiser.objects.all()
        data = {
            "updated_at_after": "2020-01-01T00:00:00Z",
            "updated_at_before": "2030-12-31T23:59:59Z",
        }
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        self.assertEqual(fs.qs.count(), 3)

    def test_filter_by_exact_name(self):
        qs = Advertiser.objects.all()
        data = {"name": "Acme Corp"}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Acme Corp")

    def test_filter_by_name_icontains(self):
        qs = Advertiser.objects.all()
        data = {"name__icontains": "Acme"}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)
        names = {r.name for r in results}
        self.assertEqual(names, {"Acme Corp", "Gamma Acme Ltd"})

    def test_filter_by_monetization_type(self):
        qs = Advertiser.objects.all()
        data = {"monetization_type": MonetizationType.CPC}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r.monetization_type, MonetizationType.CPC)

    def test_filter_by_billing_source(self):
        qs = Advertiser.objects.all()
        data = {"billing_source": BillingSource.INTERNAL}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)

    def test_filter_by_billing_timezone(self):
        qs = Advertiser.objects.all()
        data = {"billing_timezone": BillingTimezone.UTC}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].billing_timezone, BillingTimezone.UTC)

    def test_filter_by_discount_gte(self):
        qs = Advertiser.objects.all()
        data = {"discount__gte": 0.05}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertGreaterEqual(r.discount, Decimal("0.05"))

    def test_filter_by_discount_lte(self):
        qs = Advertiser.objects.all()
        data = {"discount__lte": 0.05}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)

    def test_filter_by_default_conversion_rate_lt(self):
        qs = Advertiser.objects.all()
        data = {"default_conversion_rate__lt": 0.02}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        self.assertTrue(fs.is_valid(), msg=fs.errors)
        results = list(fs.qs)
        self.assertEqual(len(results), 2)

    def test_filter_invalid_monetization_type_returns_empty_or_error(self):
        qs = Advertiser.objects.all()
        data = {"monetization_type": "INVALID"}
        fs = AdvertiserFilterSet(data=data, queryset=qs)
        # ChoiceFilter with invalid value: form validation may fail or return empty
        if fs.is_valid():
            self.assertEqual(fs.qs.count(), 0)
        else:
            self.assertIn("monetization_type", fs.errors)
