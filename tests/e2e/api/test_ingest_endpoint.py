from collections.abc import AsyncIterator, Callable
from decimal import Decimal
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.dependencies import get_ingest_use_case
from app.application.use_cases.ingest_invoice import IngestInvoice
from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.main import app
from tests.unit.fakes import FakeInvoiceRepository, RecordingBroker


def _payload(access_key: str = "35240112345678000190550010000001230000000001") -> dict:
    return {
        "access_key": access_key,
        "issuer_cnpj": "11222333000181",
        "recipient_cnpj": "04252011000110",
        "items": [
            {
                "item_number": 1,
                "description": "Aparas de PET",
                "ncm_code": "39159000",
                "gross_weight_kg": str(Decimal("1500.000")),
            }
        ],
    }


@pytest.fixture
async def make_client() -> AsyncIterator[
    Callable[[FakeInvoiceRepository, RecordingBroker], AsyncClient]
]:
    def _make(repository: FakeInvoiceRepository, broker: RecordingBroker) -> AsyncClient:
        use_case = IngestInvoice(repository=repository, broker=broker)
        app.dependency_overrides[get_ingest_use_case] = lambda: use_case
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    yield _make
    app.dependency_overrides.pop(get_ingest_use_case, None)


async def test_ingest_returns_202_with_tracking_id(make_client) -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    client = make_client(repository, broker)
    async with client as http:
        response = await http.post("/api/v1/nfe/ingest", json=_payload())

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "PENDING"
    UUID(body["tracking_id"])
    assert len(broker.published) == 1


async def test_ingest_persists_invoice_for_async_pipeline(make_client) -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    client = make_client(repository, broker)
    async with client as http:
        await http.post("/api/v1/nfe/ingest", json=_payload())

    saved = repository.saved_by_hash()
    assert len(saved) == 1
    invoice = next(iter(saved.values()))
    assert invoice.status == InvoiceStatus.PENDING
    assert len(invoice.items) == 1


async def test_duplicate_hash_returns_409_conflict(make_client) -> None:
    request_payload = _payload()
    existing = Invoice(
        access_key=AccessKey(request_payload["access_key"]),
        issuer_cnpj=CNPJ(request_payload["issuer_cnpj"]),
        recipient_cnpj=CNPJ(request_payload["recipient_cnpj"]),
        status=InvoiceStatus.APPROVED,
    )
    repository = FakeInvoiceRepository(existing_invoices=[existing])
    broker = RecordingBroker()
    client = make_client(repository, broker)
    async with client as http:
        response = await http.post("/api/v1/nfe/ingest", json=request_payload)

    assert response.status_code == 409
    assert "already been ingested" in response.json()["detail"]
    assert broker.published == []


async def test_malformed_access_key_returns_422(make_client) -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    payload = _payload(access_key="short-key")
    client = make_client(repository, broker)
    async with client as http:
        response = await http.post("/api/v1/nfe/ingest", json=payload)

    assert response.status_code == 422
    assert broker.published == []


async def test_invalid_check_digit_cnpj_returns_422(make_client) -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    payload = _payload()
    payload["issuer_cnpj"] = "11222333000199"
    client = make_client(repository, broker)
    async with client as http:
        response = await http.post("/api/v1/nfe/ingest", json=payload)

    assert response.status_code == 422
