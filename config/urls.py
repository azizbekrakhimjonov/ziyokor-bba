from django.contrib import admin
from django.urls import path

from bba.views import bba_api, platform_home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/public/bba", bba_api),
    path("bba-platform.html", platform_home),
    path("", platform_home),
]
