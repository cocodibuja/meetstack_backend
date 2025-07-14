from django.contrib import admin
from django.urls import path, include

from meetstack_backend import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        f"api/{settings.API_VERSION}/",
        include(("core.urls", "core"), namespace=settings.API_VERSION),
    ),
]
