from rest_framework import routers

from activities.views import NewsViewSet, MeetingViewSet, CalendarViewSet, TaskViewSet

router = routers.DefaultRouter()
router.register('news', NewsViewSet)
router.register('meeting', MeetingViewSet)
router.register('calendar', CalendarViewSet)
router.register('task', TaskViewSet)

urlpatterns = router.urls
