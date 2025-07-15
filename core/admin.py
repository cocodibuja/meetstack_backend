# core/admin.py
from django.contrib import admin
from .models import Event, EventRoleMembership

admin.site.register(Event)
admin.site.register(EventRoleMembership)