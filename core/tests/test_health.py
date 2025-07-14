from django.urls import reverse
import pytest
from rest_framework.test import APIClient
from meetstack_backend import settings # quizas sería mejor un config  ... pero bueno quedara para la próxima no tengo tanto tiempo 

@pytest.mark.django_db(reset_sequences=True)
def test_health_check():
    client = APIClient()
    url_health = reverse(f"{settings.API_VERSION}:health-check")
    response = client.get(url_health)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
