import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


async def test_health_endpoint_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == get_settings().ENVIRONMENT
    assert body["version"] == get_settings().APP_VERSION


async def test_unknown_route_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/unknown")

    assert response.status_code == 404
