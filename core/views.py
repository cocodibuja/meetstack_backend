from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Event, Role, UserRole
from .serializers import EventSerializer, RoleSerializer, UserRoleSerializer
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
import os
from supabase import create_client, Client
from django.contrib.auth.models import User


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

class UserRegistrationView(APIView):
    """
    Vista pública para registrar un nuevo usuario en Supabase y Django.
    """
    permission_classes = [AllowAny]  # <-- Esto hace que la vista sea pública
    authentication_classes = []      # <-- Sin autenticación para este endpoint

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        email = validated_data['email']
        password = validated_data['password']

        try:
            # 1. Conectar con Supabase usando la clave pública (anon key)
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")
            supabase: Client = create_client(supabase_url, supabase_key)

            # 2. Intentar registrar el usuario en Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })

            # Si el usuario ya existe, Supabase puede devolver un usuario sin sesión
            if not auth_response.user or not auth_response.session:
                 # Esta condición puede variar según la versión de la librería,
                 # pero la idea es detectar un registro fallido.
                 # El error específico de "usuario ya existe" se captura abajo.
                 raise Exception("El usuario podría ya existir o hubo un error en Supabase.")

            # 3. Si el registro en Supabase es exitoso, crea el usuario en Django
            supabase_user_id = auth_response.user.id
            
            # Usamos el ID de Supabase como 'username' para que sea único y fácil de vincular.
            user = User.objects.create_user(
                username=supabase_user_id,
                email=email
            )
            user.set_unusable_password() # No almacenamos la contraseña en Django
            user.save()

            # Devolvemos el token para que el frontend pueda iniciar sesión automáticamente
            return Response({
                "message": "Usuario registrado exitosamente. Por favor, verifica tu email.",
                "user_id": supabase_user_id,
                "access_token": auth_response.session.access_token,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Captura el error específico si el usuario ya existe
            if 'User already registered' in str(e):
                return Response(
                    {"error": "Un usuario con este email ya existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Para otros errores
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)