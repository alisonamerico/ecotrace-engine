import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.aggregates.invoice import InvoiceStatus
from app.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.credit_model import CreditModel
    from app.infrastructure.database.models.item_model import InvoiceItemModel


class InvoiceModel(Base):
    """SQLAlchemy model for invoices table."""

    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    tracking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False
    )
    access_key: Mapped[str] = mapped_column(String(44), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    issuer_cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    recipient_cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        SAEnum(
            InvoiceStatus,
            name="invoice_status",
            native_enum=True,
            values_callable=lambda e: [member.value for member in e],
            validate_strings=True,
        ),
        nullable=False,
        default=InvoiceStatus.PENDING,
        server_default="PENDING",
    )
    sefaz_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=text("now()"),
        nullable=False,
    )

    items: Mapped[list["InvoiceItemModel"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan", lazy="selectin"
    )
    credits: Mapped[list["CreditModel"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("char_length(access_key) = 44", name="chk_access_key_length"),
        CheckConstraint("char_length(hash_sha256) = 64", name="chk_hash_sha256_length"),
        Index("idx_invoices_hash_sha256", "hash_sha256", postgresql_using="hash"),
        Index("idx_invoices_tracking_id", "tracking_id"),
        Index(
            "idx_invoices_status_created_at",
            "status",
            "created_at",
            postgresql_where=text("status IN ('PENDING', 'PROCESSING')"),
        ),
    )
