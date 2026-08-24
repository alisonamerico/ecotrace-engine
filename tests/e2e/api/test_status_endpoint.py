from collections.abc import Callable
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.dependencies import get_status_use_case
from app.application.use_cases.get_invoice_status import GetInvoiceStatus
from app.domain.aggregates.invoice import Invoice
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.main import app
from tests.unit.fakes import FakeInvoiceRepository


def _seeded_repository() -> FakeInvoiceRepository:
    invoice = Invoice(
        access_key=AccessKey("35240112345678000190550010000001230000000077"),
        issuer_cnpj=CNPJ("11222333000181"),
        recipient_cnpj=CNPJ("04252011000110"),
    )
    return FakeInvoiceRepository(existing_invoices=[invoice])


@pytest.fixture
def make_client() -> Callable[[FakeInvoiceRepository], AsyncClient]:
    def _make(repository: FakeInvoiceRepository) -> AsyncClient:
        use_case = GetInvoiceStatus(repository=repository)
        app.dependency_overrides[get_status_use_case] = lambda: use_case
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    return _make


@pytest.fixture(autouse=True)
def _cleanup_overrides() -> None:
    yield
    app.dependency_overrides.pop(get_status_use_case, None)


async def test_status_returns_200_for_known_tracking_id(make_client) -> None:
    repository = _seeded_repository()
    invoice = next(iter(repository.saved_by_hash().values()))
    client = make_client(repository)
    async with client as http:
        response = await http.get(f"/api/v1/nfe/status/{invoice.tracking_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["tracking_id"] == str(invoice.tracking_id)
    assert body["access_key"] == invoice.access_key.value
    assert body["status"] == "PENDING"
    assert body["created_at"] is not None


async def test_status_returns_404_for_unknown_tracking_id(make_client) -> None:
    client = make_client(FakeInvoiceRepository())
    async with client as http:
        response = await http.get(f"/api/v1/nfe/status/{uuid4()}")

    assert response.status_code == 404


async def test_status_returns_422_for_malformed_uuid(make_client) -> None:
    client = make_client(FakeInvoiceRepository())
    async with client as http:
        response = await http.get("/api/v1/nfe/status/not-a-uuid")

    assert response.status_code == 422
