from django.test import TestCase

from dj_advertisers.models import Advertiser
from dj_advertisers.serializers import AdvertiserSerializer


class AdvertiserSerializerTest(TestCase):
    def test_serialize_advertiser(self):
        a = Advertiser.objects.create(name="Acme")
        ser = AdvertiserSerializer(a)
        self.assertEqual(ser.data["name"], "Acme")
        self.assertIn("id", ser.data)
        self.assertIn("discount", ser.data)
        self.assertIn("monetization_type", ser.data)

    def test_deserialize_create(self):
        data = {"name": "New Advertiser"}
        ser = AdvertiserSerializer(data=data)
        self.assertTrue(ser.is_valid())
        obj = ser.save()
        self.assertEqual(obj.name, "New Advertiser")
