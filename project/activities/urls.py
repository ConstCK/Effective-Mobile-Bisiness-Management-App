from rest_framework import routers

from activities.views import NewsViewSet

router = routers.DefaultRouter()
router.register('', NewsViewSet)

urlpatterns = router.urls
