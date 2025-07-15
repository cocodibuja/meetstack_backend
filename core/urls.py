from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCheckView, UserLoginView, EventViewSet,RoleViewSet,UserRoleViewSet,UserRegistrationView

app_name = "core"

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"user-roles", UserRoleViewSet, basename="userrole")


urlpatterns = [path("health/",      HealthCheckView.as_view(),    name="health-check"),
               path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
               path("auth/login/", UserLoginView.as_view(), name="user-login"),
               path("", include(router.urls))]
