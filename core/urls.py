# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ----- ¡Importaciones actualizadas! -----
from .views import (
    health_check, 
    EventViewSet, 
    EventRoleMembershipViewSet, #
    UserRegistrationView,
    UserLoginView
)
# RoleViewSet es eliminado

app_name = "core"

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

router.register(r"event-memberships", EventRoleMembershipViewSet, basename="eventrole-membership")

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
    path("auth/login/", UserLoginView.as_view(), name="user-login"),
    path("", include(router.urls)),
]