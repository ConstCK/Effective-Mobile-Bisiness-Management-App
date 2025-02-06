from rest_framework import routers

from accounts.views import UserViewSet

router = routers.DefaultRouter()
router.register('', UserViewSet)

urlpatterns = router.urls
