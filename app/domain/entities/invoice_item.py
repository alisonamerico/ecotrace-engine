from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM


@dataclass
class InvoiceItem:
    """Individual item of an NF-e invoice."""

    item_number: int
    description: str
    ncm: NCM
    gross_weight: RecyclableMass
    id: UUID = field(default_factory=uuid4)
    is_eligible: bool = field(init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.is_eligible = self.ncm.is_recyclable
