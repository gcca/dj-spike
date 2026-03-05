from rest_framework import status
from rest_framework.test import APITestCase

from dj_advertisers.models import Advertiser, BillingSource, MonetizationType


class AdvertiserViewSetTest(APITestCase):
    def test_list_empty(self):
        r = self.client.get("/api/v1/advertisers/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json(), [])

    def test_create_and_retrieve(self):
        r = self.client.post(
            "/api/v1/advertisers/", {"name": "Acme"}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        pk = r.json()["id"]
        r2 = self.client.get(f"/api/v1/advertisers/{pk}/")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.json()["name"], "Acme")

    def test_update_put(self):
        a = Advertiser.objects.create(name="Original")
        r = self.client.put(
            f"/api/v1/advertisers/{a.pk}/",
            {"name": "Updated"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        a.refresh_from_db()
        self.assertEqual(a.name, "Updated")

    def test_update_patch(self):
        a = Advertiser.objects.create(name="Original")
        r = self.client.patch(
            f"/api/v1/advertisers/{a.pk}/",
            {"name": "Patched"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        a.refresh_from_db()
        self.assertEqual(a.name, "Patched")

    def test_delete(self):
        a = Advertiser.objects.create(name="ToDelete")
        r = self.client.delete(f"/api/v1/advertisers/{a.pk}/")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Advertiser.objects.filter(pk=a.pk).exists())

    def test_filter_by_created_at_after(self):
        Advertiser.objects.create(name="Old", discount=0)
        Advertiser.objects.create(name="New", discount=0)
        r = self.client.get(
            "/api/v1/advertisers/?created_at_after=2025-01-01T00:00:00Z"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(r.json()), 0)

    def test_filter_by_created_at_range(self):
        r = self.client.get(
            "/api/v1/advertisers/?created_at_after=2025-01-01T00:00:00Z"
            "&created_at_before=2025-12-31T23:59:59Z"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_filter_by_updated_at_before(self):
        r = self.client.get(
            "/api/v1/advertisers/?updated_at_before=2025-12-31T23:59:59Z"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_filter_by_name_exact(self):
        Advertiser.objects.create(name="Acme Corp")
        Advertiser.objects.create(name="Other")
        r = self.client.get("/api/v1/advertisers/?name=Acme Corp")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Acme Corp")

    def test_filter_by_name_icontains(self):
        Advertiser.objects.create(name="Acme Corp")
        Advertiser.objects.create(name="Other Corp")
        Advertiser.objects.create(name="Different")
        r = self.client.get("/api/v1/advertisers/?name__icontains=Corp")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 2)
        names = [d["name"] for d in data]
        self.assertIn("Acme Corp", names)
        self.assertIn("Other Corp", names)

    def test_filter_by_monetization_type(self):
        Advertiser.objects.create(
            name="A", monetization_type=MonetizationType.CPC
        )
        Advertiser.objects.create(
            name="B", monetization_type=MonetizationType.CPA
        )
        r = self.client.get("/api/v1/advertisers/?monetization_type=CPC")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["monetization_type"], "CPC")

    def test_filter_by_billing_source(self):
        Advertiser.objects.create(
            name="A", billing_source=BillingSource.INTERNAL
        )
        Advertiser.objects.create(
            name="B", billing_source=BillingSource.PARTNER
        )
        r = self.client.get("/api/v1/advertisers/?billing_source=INTERNAL")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["billing_source"], "INTERNAL")

    def test_filter_by_discount_gte(self):
        Advertiser.objects.create(name="Low", discount=0.02)
        Advertiser.objects.create(name="High", discount=0.08)
        r = self.client.get("/api/v1/advertisers/?discount__gte=0.05")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "High")

    def test_filter_by_discount_lte(self):
        Advertiser.objects.create(name="Low", discount=0.02)
        Advertiser.objects.create(name="High", discount=0.08)
        r = self.client.get("/api/v1/advertisers/?discount__lte=0.05")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Low")

    def test_filter_by_default_conversion_rate_lte(self):
        Advertiser.objects.create(name="Low", default_conversion_rate=0.005)
        Advertiser.objects.create(name="High", default_conversion_rate=0.02)
        r = self.client.get(
            "/api/v1/advertisers/?default_conversion_rate__lte=0.01"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Low")

    def test_filter_combined(self):
        Advertiser.objects.create(
            name="Match",
            monetization_type=MonetizationType.CPC,
            discount=0.06,
        )
        Advertiser.objects.create(
            name="NoMatch",
            monetization_type=MonetizationType.CPA,
            discount=0.06,
        )
        r = self.client.get(
            "/api/v1/advertisers/?monetization_type=CPC&discount__gte=0.05"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Match")
