import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db(reset_sequences=True)
def test_health_check():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
