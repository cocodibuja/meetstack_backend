import uuid
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    """
    Perfil extendido del usuario Supabase.
    No maneja autenticación ni contraseñas, solo metadata para enriquecer la experiencia.
    """

    id_supabase = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text='Clave primaria. Coincide con el ID de Supabase.'
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    about_me = models.TextField(
        blank=True,
        null=True,
        help_text="Texto donde el usuario puede presentarse o compartir intereses personales."
    )
    birthdate = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        SUSPENDED = 'suspended', 'Suspendido'
        PENDING = 'pending', 'Pendiente'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['-created_at']

    def __str__(self):
        return self.email
