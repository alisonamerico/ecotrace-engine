from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_metrics_endpoint_returns_prometheus_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "# HELP" in text or "# EOF" in text
