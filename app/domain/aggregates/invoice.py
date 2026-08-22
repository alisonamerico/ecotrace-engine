from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.entities.invoice_item import InvoiceItem
from app.domain.exceptions import InvalidMassException, InvalidStateTransitionException
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass


class InvoiceStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FRAUD_SUSPECT = "FRAUD_SUSPECT"


@dataclass
class Invoice:
    """Aggregate Root representing an NF-e lifecycle and its items."""

    access_key: AccessKey
    issuer_cnpj: CNPJ
    recipient_cnpj: CNPJ
    id: UUID = field(default_factory=uuid4)
    tracking_id: UUID = field(default_factory=uuid4)
    status: InvoiceStatus = InvoiceStatus.PENDING
    sefaz_status: str | None = None
    rejection_reason: str | None = None
    items: list[InvoiceItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def hash_sha256(self) -> str:
        return self.access_key.hash_sha256

    def add_item(self, item: InvoiceItem) -> None:
        self.items.append(item)
        self._touch()

    def start_processing(self) -> None:
        if self.status != InvoiceStatus.PENDING:
            raise InvalidStateTransitionException(
                f"Cannot start processing invoice in status {self.status}"
            )
        self.status = InvoiceStatus.PROCESSING
        self._touch()

    def approve(self, sefaz_status: str = "100 - Autorizado") -> None:
        if self.status != InvoiceStatus.PROCESSING:
            raise InvalidStateTransitionException(
                f"Cannot approve invoice in status {self.status} (must be PROCESSING)"
            )
        self.status = InvoiceStatus.APPROVED
        self.sefaz_status = sefaz_status
        self._touch()

    def reject(self, reason: str, sefaz_status: str | None = None) -> None:
        if self.status in (InvoiceStatus.APPROVED, InvoiceStatus.FRAUD_SUSPECT):
            raise InvalidStateTransitionException(
                f"Cannot reject invoice in terminal status {self.status}"
            )
        self.status = InvoiceStatus.REJECTED
        self.rejection_reason = reason
        if sefaz_status:
            self.sefaz_status = sefaz_status
        self._touch()

    def flag_fraud(self, reason: str) -> None:
        self.status = InvoiceStatus.FRAUD_SUSPECT
        self.rejection_reason = reason
        self._touch()

    def total_eligible_mass(self) -> RecyclableMass:
        eligible_items = [item for item in self.items if item.is_eligible]
        if not eligible_items:
            raise InvalidMassException("Invoice has no eligible recyclable items")

        total = sum((item.gross_weight.value_kg for item in eligible_items), Decimal("0.000"))
        return RecyclableMass(total)

    def material_breakdown(self) -> dict[str, Decimal]:
        breakdown: dict[str, Decimal] = {}
        for item in self.items:
            if item.is_eligible and item.ncm.material_family:
                family = item.ncm.material_family
                breakdown[family] = (
                    breakdown.get(family, Decimal("0.000")) + item.gross_weight.value_kg
                )
        return breakdown

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
