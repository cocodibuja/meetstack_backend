from django.db import models
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    """
    Define los diferentes planes de suscripción disponibles en la plataforma (ej: Free, Pro).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    event_creation_limit = models.PositiveIntegerField(default=1, help_text="Número de eventos que un usuario puede crear con este plan.")
    is_public = models.BooleanField(default=True, help_text="Determina si los usuarios pueden seleccionar este plan al registrarse o actualizar.")

    def __str__(self):
        return f"{self.name} (${self.price})"

class UserSubscription(models.Model):
    """
    Vincula a un Usuario con un Plan específico, gestionando el estado de su suscripción.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, help_text="Si el plan se borra, la suscripción no, para mantener el historial.")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True, help_text="Nulo para suscripciones que no expiran.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        plan_name = self.plan.name if self.plan else "Ninguno"
        return f"Suscripción de {self.user.email} al plan {plan_name}"

class DailyFreeQuota(models.Model):
    """
    Lleva un registro de cuántos usuarios con plan gratuito se han registrado cada día.
    """
    date = models.DateField(unique=True, default=timezone.now)
    registrations_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Cuota Diaria de Registros Gratuitos"
        verbose_name_plural = "Cuotas Diarias de Registros Gratuitos"

    def __str__(self):
        return f"{self.date}: {self.registrations_count} registros"

class Coupon(models.Model):
    """
    Define cupones de descuento que se pueden aplicar a la compra de planes.
    """
    code = models.CharField(max_length=50, unique=True, help_text="El código que el usuario introduce.")
    
    class DiscountType(models.TextChoices):
        FIXED = 'fixed', 'Cantidad Fija'
        PERCENTAGE = 'percentage', 'Porcentaje'

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="La cantidad o el porcentaje a descontar.")
    usage_limit = models.PositiveIntegerField(default=1, help_text="Cuántas veces se puede usar el cupón en total.")
    times_used = models.PositiveIntegerField(default=0, editable=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Comprueba si el cupón es actualmente válido y no ha alcanzado su límite de uso."""
        now = timezone.now()
        return self.is_active and self.times_used < self.usage_limit and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.code