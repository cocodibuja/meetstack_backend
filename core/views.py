import os
from datetime import date

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from supabase import create_client, Client

from users.models import UserProfile
from subscriptions.models import Plan, UserSubscription, DailyFreeQuota
from .models import Event, EventRoleMembership
from .serializers import (
    EventSerializer,
    EventRoleMembershipSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)

@api_view(["GET"])
@permission_classes([AllowAny])
@api_view(["GET"])
def health_check(_):
    """Una simple comprobación para ver si el servicio está en línea."""
    return Response({"status": "ok"})

class EventViewSet(viewsets.ModelViewSet):
    """
    Gestiona los eventos.
    TODO: Implementar permisos para que solo el propietario o staff pueda editar.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventRoleMembershipViewSet(viewsets.ModelViewSet):
    """
    Gestiona los roles de los usuarios dentro de los eventos.
    TODO: Implementar permisos para que solo el propietario del evento pueda asignar roles.
    """
    queryset = EventRoleMembership.objects.all()
    serializer_class = EventRoleMembershipSerializer

class UserRegistrationView(APIView):
    """
    Vista pública para registrar un nuevo usuario en Supabase
    y crear su perfil y suscripción gratuita en nuestra base de datos.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic # Si cualquier paso falla, se deshacen todos los cambios en la BD.
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # 1. Verificar la cuota diaria de registros gratuitos.
        # TODO: Hacer el límite de 40 configurable en settings.py o en un modelo.
        quota, _ = DailyFreeQuota.objects.get_or_create(date=date.today())
        if quota.registrations_count >= 40:
            return Response(
                {"error": "La cuota de registros para hoy ha sido alcanzada."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # 2. Registrar el usuario en el servicio de autenticación de Supabase.
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")
            supabase: Client = create_client(supabase_url, supabase_key)
            auth_response = supabase.auth.sign_up({"email": email, "password": password})

            if not auth_response.user or not auth_response.session:
                raise Exception("El usuario podría ya existir o hubo un error en Supabase.")

            supabase_user_id = auth_response.user.id

            # 3. Crear el perfil local (UserProfile) en nuestra base de datos.
            # Esta es la "sombra" del usuario de Supabase.
            profile = UserProfile.objects.create(
                id_supabase=supabase_user_id,
                email=email
            )

            # 4. Asignar el plan "free" por defecto al nuevo perfil.
            # Este paso asume que has creado un Plan con name='free' en el admin.
            free_plan = Plan.objects.get(name='free')
            UserSubscription.objects.create(user=profile, plan=free_plan)

            # 5. Incrementar la cuota de registros de hoy.
            quota.registrations_count += 1
            quota.save()

            # 6. Devolver una respuesta exitosa con el token para auto-login.
            return Response({
                "message": "Usuario registrado exitosamente y asignado al plan gratuito.",
                "profile_id": str(profile.id_supabase),
                "access_token": auth_response.session.access_token,
            }, status=status.HTTP_201_CREATED)

        except Plan.DoesNotExist:
            # Error crítico de configuración si el plan 'free' no existe.
            return Response(
                {"error": "Error de configuración del servidor: El plan 'free' no fue encontrado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Manejar errores comunes como "usuario ya existe".
            if 'User already registered' in str(e):
                return Response(
                    {"error": "Un usuario con este email ya existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Devolver cualquier otro error inesperado.
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    Vista pública para que un usuario inicie sesión.
    Esta vista solo interactúa con Supabase Auth y no toca nuestra base de datos.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")
            supabase: Client = create_client(supabase_url, supabase_key)

            # Iniciar sesión en Supabase para obtener el JWT.
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            return Response({
                "message": "Login exitoso.",
                "access_token": auth_response.session.access_token,
                "user_id": auth_response.user.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error en el login: {e}"}, status=status.HTTP_400_BAD_REQUEST)