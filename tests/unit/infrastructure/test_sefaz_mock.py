import pytest

from app.infrastructure.external.sefaz_client_mock import MockSEFAZClient


@pytest.fixture
def client():
    return MockSEFAZClient()


async def test_consult_returns_authorized(client):
    response = await client.consult("35240112345678000190550010000001230000000042")
    assert response.authorized is True
    assert response.status_code == 100
    assert "Autorizado" in response.motivo


async def test_consult_hash_deterministic(client):
    key = "35240112345678000190550010000001230000000042"
    r1 = await client.consult(key)
    r2 = await client.consult(key)
    assert r1 == r2
