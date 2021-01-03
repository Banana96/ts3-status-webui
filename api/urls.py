from rest_framework.routers import DefaultRouter

from api.views import *


router = DefaultRouter()
router.register("status", StatusViewSet, basename="status")

urlpatterns = router.urls
