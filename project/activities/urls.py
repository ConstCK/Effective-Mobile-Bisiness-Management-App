from rest_framework import routers

from activities.views import ActivityViewSet

router = routers.DefaultRouter()
router.register('', ActivityViewSet)

urlpatterns = router.urls
