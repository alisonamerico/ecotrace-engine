import json
from decimal import Decimal

import pytest

from app.application.dtos.invoice_dto import IngestInvoiceRequest
from app.application.exceptions import DuplicateInvoiceError
from app.application.interfaces.message_broker import MessageBroker
from app.application.use_cases.ingest_invoice import (
    NFE_EXCHANGE,
    NFE_RECEIVED_ROUTING_KEY,
    IngestInvoice,
)
from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.exceptions import InvalidAccessKeyException, InvalidCNPJException
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from tests.unit.fakes import FakeInvoiceRepository, RecordingBroker

_KEY_SEQUENCE = iter(range(1000))


def _make_request() -> IngestInvoiceRequest:
    sequence = str(next(_KEY_SEQUENCE)).zfill(10)
    return IngestInvoiceRequest(
        access_key=f"3524011234567800019055001000000123{sequence}",
        issuer_cnpj="11222333000181",
        recipient_cnpj="04252011000110",
        items=[
            {
                "item_number": 1,
                "description": "Aparas de PET",
                "ncm_code": "39159000",
                "gross_weight_kg": Decimal("1500.000"),
            }
        ],
    )


def _seed_invoice(request: IngestInvoiceRequest, status: InvoiceStatus) -> Invoice:
    invoice = Invoice(
        access_key=AccessKey(request.access_key),
        issuer_cnpj=CNPJ(request.issuer_cnpj),
        recipient_cnpj=CNPJ(request.recipient_cnpj),
        status=status,
    )
    return invoice


async def test_execute_persists_pending_invoice_and_publishes_event() -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    use_case = IngestInvoice(repository=repository, broker=broker)

    response = await use_case.execute(_make_request())

    assert response.status == InvoiceStatus.PENDING.value
    saved = repository.saved_by_hash()
    assert len(saved) == 1
    invoice = next(iter(saved.values()))
    assert str(invoice.tracking_id) == str(response.tracking_id)
    assert len(invoice.items) == 1

    assert len(broker.published) == 1
    exchange, routing_key, _payload = broker.published[0]
    assert exchange == NFE_EXCHANGE
    assert routing_key == NFE_RECEIVED_ROUTING_KEY


async def test_published_event_carries_identifiers() -> None:
    repository = FakeInvoiceRepository()
    broker = RecordingBroker()
    use_case = IngestInvoice(repository=repository, broker=broker)
    request = _make_request()

    response = await use_case.execute(request)

    _, _, payload = broker.published[0]
    event = json.loads(payload)
    assert event["tracking_id"] == str(response.tracking_id)
    assert event["access_key"] == request.access_key
    assert event["hash_sha256"]
    assert len(event["hash_sha256"]) == 64


async def test_duplicate_approved_hash_raises_duplicate_error() -> None:
    request = _make_request()
    existing = _seed_invoice(request, InvoiceStatus.APPROVED)
    repository = FakeInvoiceRepository(existing_invoices=[existing])
    use_case = IngestInvoice(repository=repository, broker=RecordingBroker())

    with pytest.raises(DuplicateInvoiceError):
        await use_case.execute(request)


async def test_fraud_suspect_reentry_raises_duplicate_error() -> None:
    request = _make_request()
    existing = _seed_invoice(request, InvoiceStatus.FRAUD_SUSPECT)
    repository = FakeInvoiceRepository(existing_invoices=[existing])
    use_case = IngestInvoice(repository=repository, broker=RecordingBroker())

    with pytest.raises(DuplicateInvoiceError):
        await use_case.execute(request)


async def test_duplicate_does_not_publish_or_persist_again() -> None:
    request = _make_request()
    existing = _seed_invoice(request, InvoiceStatus.APPROVED)
    repository = FakeInvoiceRepository(existing_invoices=[existing])
    broker = RecordingBroker()
    use_case = IngestInvoice(repository=repository, broker=broker)

    with pytest.raises(DuplicateInvoiceError):
        await use_case.execute(request)

    assert broker.published == []
    assert len(repository.saved_by_hash()) == 1


async def test_invalid_access_key_propagates_domain_exception() -> None:
    repository = FakeInvoiceRepository()
    use_case = IngestInvoice(repository=repository, broker=RecordingBroker())
    request = _make_request()
    broken = request.model_copy(update={"access_key": "123"})

    with pytest.raises(InvalidAccessKeyException):
        await use_case.execute(broken)


async def test_invalid_issuer_cnpj_propagates_domain_exception() -> None:
    repository = FakeInvoiceRepository()
    use_case = IngestInvoice(repository=repository, broker=RecordingBroker())
    request = _make_request()
    broken = request.model_copy(update={"issuer_cnpj": "11222333000199"})

    with pytest.raises(InvalidCNPJException):
        await use_case.execute(broken)


def test_fakes_satisfy_ports() -> None:
    assert issubclass(FakeInvoiceRepository, InvoiceRepositoryInterface)
    assert issubclass(RecordingBroker, MessageBroker)
