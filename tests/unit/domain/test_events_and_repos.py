from decimal import Decimal
from uuid import uuid4

from app.domain.entities.credit import CreditStatus, RecyclingCredit
from app.domain.events.invoice_events import (
    CreditIssuedEvent,
    FraudSuspectedEvent,
    InvoiceApprovedEvent,
    InvoiceReceivedEvent,
    InvoiceRejectedEvent,
)
from app.domain.value_objects.mass import RecyclableMass


def test_domain_events_instantiation() -> None:
    inv_id = uuid4()
    track_id = uuid4()
    credit_id = uuid4()

    event_received = InvoiceReceivedEvent(
        tracking_id=track_id,
        access_key="35240112345678000190550010000001231234567890",
        hash_sha256="abc123hash",
    )
    assert event_received.access_key == "35240112345678000190550010000001231234567890"

    event_approved = InvoiceApprovedEvent(
        invoice_id=inv_id,
        tracking_id=track_id,
        total_recyclable_kg=Decimal("1500.000"),
    )
    assert event_approved.total_recyclable_kg == Decimal("1500.000")

    event_rejected = InvoiceRejectedEvent(
        invoice_id=inv_id,
        tracking_id=track_id,
        reason="Nota rejeitada na SEFAZ",
    )
    assert event_rejected.reason == "Nota rejeitada na SEFAZ"

    event_fraud = FraudSuspectedEvent(
        invoice_id=inv_id,
        hash_sha256="hash123",
        reason="Chave duplicada",
    )
    assert event_fraud.reason == "Chave duplicada"

    event_credit = CreditIssuedEvent(
        credit_id=credit_id,
        invoice_id=inv_id,
        credit_code="CRED-2026-PLASTICO-001",
        material_family="PLASTICO",
        total_weight_kg=Decimal("1000.000"),
    )
    assert event_credit.material_family == "PLASTICO"


def test_credit_cancel_from_available() -> None:
    credit = RecyclingCredit(
        id=uuid4(),
        invoice_id=uuid4(),
        credit_code="CRED-2026-TEST",
        material_family="PAPEL",
        total_weight=RecyclableMass(Decimal("100.000")),
        status=CreditStatus.AVAILABLE,
    )
    credit.cancel()
    assert credit.status == CreditStatus.CANCELLED
