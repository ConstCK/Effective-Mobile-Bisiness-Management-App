from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/business/', include('companies.urls')),
    path('api/v1/activities/', include('activities.urls')),
]
