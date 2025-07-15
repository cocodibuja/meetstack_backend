from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    # Solo para nuestra app “core”
    if sender.name != 'core':
        return

    default_roles = ["basic", "owner", "member", "speaker", "organizer"]
    for name in default_roles:
        Role.objects.get_or_create(name=name)