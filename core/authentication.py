import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth.models import User
from supabase import create_client, Client
import os

class SupabaseAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b'bearer':
            return None

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth_header) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token = auth_header[1].decode('utf-8')
            return self.authenticate_credentials(token)
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')

    def authenticate_credentials(self, token):
        try:
            payload = jwt.decode(
                token,
                os.environ.get("SUPABASE_JWT_SECRET"),
                algorithms=["HS256"],
                audience='authenticated',
                leeway=30
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('User identifier not found in token.')

        # Aquí es donde "sincronizamos" el usuario de Supabase con el de Django.
        # La primera vez que un usuario se autentica, se crea un usuario correspondiente en Django.
        user, created = User.objects.get_or_create(
            username=user_id,  # Usamos el ID de Supabase como username para garantizar unicidad.
            defaults={'email': payload.get('email')}
        )

        if created:
            user.set_unusable_password()
            user.save()

        # Puedes adjuntar los permisos del evento al objeto de usuario si lo necesitas más adelante en las vistas.
        # request.user.event_permissions = payload.get('event_permissions', {})

        return (user, token)