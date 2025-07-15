import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Event, Role, UserRole

BASE = "/api/v1/events/"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def setup_roles(db):
    # Seed de roles básicos
    for name in ["owner", "member"]:
        Role.objects.get_or_create(name=name)

@pytest.fixture
def user(db):
    return User.objects.create_user(username="u1", password="testpass")

@pytest.mark.django_db
def test_create_event_and_owner_role(api_client, user):
    api_client.force_authenticate(user=user)
    resp = api_client.post(BASE, {"name": "Evento A"})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    ur = UserRole.objects.get(user=user, event__id=data["id"])
    assert ur.role.name == "owner"

@pytest.mark.django_db
def test_limit_two_events(api_client, user):
    api_client.force_authenticate(user=user)
    api_client.post(BASE, {"name": "E1"})
    api_client.post(BASE, {"name": "E2"})
    resp = api_client.post(BASE, {"name": "E3"})
    assert resp.status_code == 400
    # Verificamos que el mensaje aparezca en la respuesta
    assert "Solo puedes crear 2 eventos" in str(resp.json())

@pytest.mark.django_db
def test_join_event_unlimited(api_client, user):
    api_client.force_authenticate(user=user)
    e1 = Event.objects.create(name="Externo 1")
    e2 = Event.objects.create(name="Externo 2")
    for e in (e1, e2):
        resp = api_client.post(f"{BASE}{e.id}/join/")
        assert resp.status_code == 201
        ur = UserRole.objects.get(user=user, event=e)
        assert ur.role.name == "member"

@pytest.mark.django_db
def test_list_events_shows_created_and_joined(api_client, user):
    api_client.force_authenticate(user=user)
    # Crear un evento como owner
    eid1 = api_client.post(BASE, {"name": "Evento Owner"}).json()["id"]
    # Crear otro evento “externo” y unirse como member
    ext = Event.objects.create(name="Evento Externo")
    api_client.post(f"{BASE}{ext.id}/join/")
    # Listar eventos
    list_resp = api_client.get(BASE)
    assert list_resp.status_code == 200
    events = list_resp.json()
    ids = {e["id"] for e in events}
    assert eid1 in ids
    assert str(ext.id) in ids
    assert len(events) == 2