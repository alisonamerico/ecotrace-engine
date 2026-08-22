from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class InvoiceReceivedEvent(DomainEvent):
    tracking_id: UUID = field(default_factory=uuid4)
    access_key: str = ""
    hash_sha256: str = ""


@dataclass(frozen=True)
class InvoiceApprovedEvent(DomainEvent):
    invoice_id: UUID = field(default_factory=uuid4)
    tracking_id: UUID = field(default_factory=uuid4)
    total_recyclable_kg: Decimal = Decimal("0.000")


@dataclass(frozen=True)
class InvoiceRejectedEvent(DomainEvent):
    invoice_id: UUID = field(default_factory=uuid4)
    tracking_id: UUID = field(default_factory=uuid4)
    reason: str = ""


@dataclass(frozen=True)
class FraudSuspectedEvent(DomainEvent):
    invoice_id: UUID = field(default_factory=uuid4)
    hash_sha256: str = ""
    reason: str = ""


@dataclass(frozen=True)
class CreditIssuedEvent(DomainEvent):
    credit_id: UUID = field(default_factory=uuid4)
    invoice_id: UUID = field(default_factory=uuid4)
    credit_code: str = ""
    material_family: str = ""
    total_weight_kg: Decimal = Decimal("0.000")
