from rest_framework import serializers
from .models import Event, EventRoleMembership
# El serializer de Role y UserRole se eliminan.

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        # Añadimos los nuevos campos que queremos exponer en la API
        fields = [
            'id', 'name', 'slug', 'subdomain', 'description', 
            'status', 'start_datetime', 'end_datetime'
        ]
        read_only_fields = ['id', 'slug', 'subdomain'] # Estos se generan automáticamente

class EventRoleMembershipSerializer(serializers.ModelSerializer):
    # Para poder ver el email del usuario y el nombre del evento en la respuesta
    user_email = serializers.EmailField(source='user.email', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = EventRoleMembership
        fields = ['id', 'event', 'user', 'role', 'user_email', 'event_name']

# Los serializers de Login y Registro se quedan como están, no dependen de nuestros modelos.
class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)