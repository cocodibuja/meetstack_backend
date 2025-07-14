from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check, EventViewSet,RoleViewSet,UserRoleViewSet,UserRegistrationView

app_name = "core"

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"user-roles", UserRoleViewSet, basename="userrole")


urlpatterns = [path("health/", health_check,name="health-check"),
               path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
               path("", include(router.urls))]
