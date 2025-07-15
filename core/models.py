import uuid
from django.db import models
from django.conf import settings


class Event(models.Model):
    name = models.CharField(max_length=255, help_text="El nombre del evento.")
    slug = models.SlugField(unique=True, help_text="La URL-friendly version del nombre.")
    subdomain = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Subdominio único para el evento.")
    description = models.TextField(blank=True)
    venue = models.TextField(blank=True, help_text="Lugar físico del evento, si aplica.")
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=100, default='UTC')
    banner = models.CharField(max_length=255, blank=True, null=True, help_text="URL de la imagen del banner.")

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        PUBLISHED = 'published', 'Publicado'
        FINISHED = 'finished', 'Finalizado'
        CANCELLED = 'cancelled', 'Cancelado'

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # La conexión con los usuarios se define a través de EventRoleMembership
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='EventRoleMembership', 
        related_name='events_membered'
    )

    def __str__(self):
        return self.name

class EventRoleMembership(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_memberships")

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Propietario'
        ADMIN = 'ADMIN', 'Administrador'
        STAFF = 'STAFF', 'Staff'
        SPEAKER = 'SPEAKER', 'Ponente'
        ATTENDEE = 'ATTENDEE', 'Asistente'

    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario no puede tener el mismo rol dos veces en un mismo evento.
        unique_together = ('event', 'user', 'role')

    def __str__(self):
        return f"{self.user.email} es {self.get_role_display()} en {self.event.name}"