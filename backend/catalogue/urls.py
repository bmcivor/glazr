from rest_framework.routers import DefaultRouter

from catalogue.views import DonutViewSet

router = DefaultRouter()
router.register("donuts", DonutViewSet)

urlpatterns = router.urls
