from rest_framework import routers

from companies.views import CompanyViewSet

router = routers.DefaultRouter()
router.register('', CompanyViewSet)


urlpatterns = router.urls
