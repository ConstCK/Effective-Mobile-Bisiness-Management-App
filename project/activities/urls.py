from rest_framework import routers

from activities.views import NewsViewSet, MeetingViewSet

router = routers.DefaultRouter()
router.register('news', NewsViewSet)
router.register('meeting', MeetingViewSet)

urlpatterns = router.urls
