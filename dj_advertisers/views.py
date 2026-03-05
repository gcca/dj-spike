from rest_framework import viewsets

from .models import Advertiser
from .serializers import AdvertiserSerializer


class AdvertiserViewSet(viewsets.ModelViewSet):
    queryset = Advertiser.objects.all()
    serializer_class = AdvertiserSerializer
