import jwt
import os
from rest_framework import authentication, exceptions
from users.models import UserProfile  # <-- ¡CAMBIO IMPORTANTE! Importamos nuestro nuevo modelo.

class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Clase de autenticación de Django REST Framework para validar JWTs de Supabase.

    Extrae el token 'Bearer' del encabezado de la petición, lo valida contra
    el secreto de Supabase y, si es válido, obtiene o crea un perfil de usuario
    local (UserProfile) correspondiente.
    
    El perfil recuperado se adjunta a `request.user` para su uso en las vistas.
    """

    def authenticate(self, request):
        """
        Punto de entrada para el proceso de autenticación.
        Busca el token en el encabezado 'Authorization'.
        """
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b'bearer':
            # Si no hay encabezado 'Bearer', no intentamos autenticar con este método.
            return None

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed('Token inválido. No se proporcionaron credenciales.')
        elif len(auth_header) > 2:
            raise exceptions.AuthenticationFailed('Token inválido. El token no debe contener espacios.')

        try:
            token = auth_header[1].decode('utf-8')
            return self.authenticate_credentials(token)
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Token inválido. Contiene caracteres no válidos.')

    def authenticate_credentials(self, token):
        """
        Valida el token y recupera el perfil de usuario.
        """
        try:
            # Decodificamos el JWT usando el secreto de Supabase.
            payload = jwt.decode(
                token,
                os.environ.get("SUPABASE_JWT_SECRET"),
                algorithms=["HS256"],
                audience='authenticated',
                leeway=30  # Permite una pequeña diferencia de tiempo entre servidores
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('El token ha expirado.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('El token es inválido.')

        # El 'sub' claim en el JWT de Supabase contiene el ID del usuario.
        supabase_user_id = payload.get('sub')
        if not supabase_user_id:
            raise exceptions.AuthenticationFailed('El token no contiene un identificador de usuario.')

        # --- ¡LÓGICA CENTRAL ACTUALIZADA! ---
        # En lugar de buscar un User, buscamos o creamos un UserProfile.
        # Esto sincroniza el usuario de Supabase con nuestro perfil local.
        try:
            profile, created = UserProfile.objects.get_or_create(
                id_supabase=supabase_user_id,
                # 'defaults' se usa solo si el objeto necesita ser CREADO.
                defaults={'email': payload.get('email')}
            )
        except Exception as e:
            # Captura cualquier error inesperado de la base de datos.
            raise exceptions.AuthenticationFailed(f"No se pudo obtener o crear el perfil de usuario: {e}")

        # El objeto 'profile' (nuestro UserProfile) se adjuntará a request.user.
        # La tupla (usuario, token) es el valor de retorno estándar de DRF.
        return (profile, token)