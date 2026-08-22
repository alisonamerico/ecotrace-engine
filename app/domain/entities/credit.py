from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidStateTransitionException
from app.domain.value_objects.mass import RecyclableMass


class CreditStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    COMPENSATED = "COMPENSATED"
    CANCELLED = "CANCELLED"


@dataclass
class RecyclingCredit:
    """Recycling Credit backed by eligible recyclable mass."""

    invoice_id: UUID
    credit_code: str
    material_family: str
    total_weight: RecyclableMass
    id: UUID = field(default_factory=uuid4)
    status: CreditStatus = CreditStatus.AVAILABLE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def reserve(self) -> None:
        if self.status != CreditStatus.AVAILABLE:
            raise InvalidStateTransitionException(f"Cannot reserve credit in status {self.status}")
        self.status = CreditStatus.RESERVED

    def compensate(self) -> None:
        if self.status not in (CreditStatus.AVAILABLE, CreditStatus.RESERVED):
            raise InvalidStateTransitionException(
                f"Cannot compensate credit in status {self.status}"
            )
        self.status = CreditStatus.COMPENSATED

    def cancel(self) -> None:
        if self.status == CreditStatus.COMPENSATED:
            raise InvalidStateTransitionException(
                "Cannot cancel an already compensated recycling credit"
            )
        self.status = CreditStatus.CANCELLED
