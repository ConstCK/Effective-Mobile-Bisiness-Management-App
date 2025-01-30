from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from accounts.views import UserViewSet

router = routers.DefaultRouter()
router.register('', UserViewSet)

urlpatterns = router.urls



