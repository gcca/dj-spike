from rest_framework.routers import DefaultRouter

from .views import AdvertiserViewSet

router = DefaultRouter()
router.register("advertisers", AdvertiserViewSet, basename="advertiser")

urlpatterns = router.urls
