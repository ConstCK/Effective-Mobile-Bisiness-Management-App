from rest_framework import routers

from companies.views import CompanyViewSet, StructureViewSet

router = routers.DefaultRouter()
router.register('companies', CompanyViewSet)
router.register('structures', StructureViewSet)

urlpatterns = router.urls
