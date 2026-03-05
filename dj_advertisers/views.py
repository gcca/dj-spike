from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import AdvertiserFilterSet
from .models import Advertiser
from .serializers import AdvertiserSerializer


class AdvertiserViewSet(viewsets.ModelViewSet):
    queryset = Advertiser.objects.all()
    serializer_class = AdvertiserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertiserFilterSet
