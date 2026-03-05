from rest_framework import status
from rest_framework.test import APITestCase

from dj_advertisers.models import Advertiser


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
