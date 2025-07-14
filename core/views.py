from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Event, Role, UserRole
from .serializers import EventSerializer, RoleSerializer, UserRoleSerializer

@api_view(["GET"])
def health_check(_):
    return Response({"status": "ok"})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer