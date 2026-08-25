import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.credit import CreditStatus
from app.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.invoice_model import InvoiceModel


class CreditModel(Base):
    """SQLAlchemy model for recycling_credits table."""

    __tablename__ = "recycling_credits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    credit_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    material_family: Mapped[str] = mapped_column(String(50), nullable=False)
    total_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    status: Mapped[CreditStatus] = mapped_column(
        SAEnum(
            CreditStatus,
            name="credit_status",
            native_enum=True,
            values_callable=lambda e: [member.value for member in e],
            validate_strings=True,
        ),
        nullable=False,
        default=CreditStatus.AVAILABLE,
        server_default="AVAILABLE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=text("now()"),
        nullable=False,
    )

    invoice: Mapped["InvoiceModel"] = relationship(back_populates="credits")

    __table_args__ = (Index("idx_recycling_credits_material_status", "material_family", "status"),)
