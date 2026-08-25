"""Initial schema: invoices, invoice_items, recycling_credits (FASE_04 DDL).

Revision ID: 0001
Revises:
Create Date: 2026-08-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "invoices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("access_key", sa.String(length=44), nullable=False),
        sa.Column("hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("issuer_cnpj", sa.String(length=14), nullable=False),
        sa.Column("recipient_cnpj", sa.String(length=14), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "PROCESSING",
                "APPROVED",
                "REJECTED",
                "FRAUD_SUSPECT",
                name="invoice_status",
            ),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("sefaz_status", sa.String(length=50), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tracking_id"),
        sa.UniqueConstraint("hash_sha256"),
        sa.CheckConstraint("char_length(access_key) = 44", name="chk_access_key_length"),
        sa.CheckConstraint("char_length(hash_sha256) = 64", name="chk_hash_sha256_length"),
    )
    op.create_index(
        "idx_invoices_hash_sha256",
        "invoices",
        ["hash_sha256"],
        unique=False,
        postgresql_using="hash",
    )
    op.create_index("idx_invoices_tracking_id", "invoices", ["tracking_id"], unique=False)
    op.create_index(
        "idx_invoices_status_created_at",
        "invoices",
        ["status", "created_at"],
        unique=False,
        postgresql_where=sa.text("status IN ('PENDING', 'PROCESSING')"),
    )

    op.create_table(
        "invoice_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("ncm_code", sa.String(length=8), nullable=False),
        sa.Column(
            "gross_weight_kg",
            sa.Numeric(12, 3),
            server_default=sa.text("0.000"),
            nullable=False,
        ),
        sa.Column("is_eligible", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_invoice_items_invoice_id", "invoice_items", ["invoice_id"], unique=False)

    op.create_table(
        "recycling_credits",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credit_code", sa.String(length=50), nullable=False),
        sa.Column("material_family", sa.String(length=50), nullable=False),
        sa.Column("total_weight_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "AVAILABLE",
                "RESERVED",
                "COMPENSATED",
                "CANCELLED",
                name="credit_status",
            ),
            server_default="AVAILABLE",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id"),
        sa.UniqueConstraint("credit_code"),
    )
    op.create_index(
        "idx_recycling_credits_material_status",
        "recycling_credits",
        ["material_family", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_recycling_credits_material_status", table_name="recycling_credits")
    op.drop_table("recycling_credits")
    op.drop_index("idx_invoice_items_invoice_id", table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index("idx_invoices_status_created_at", table_name="invoices")
    op.drop_index("idx_invoices_tracking_id", table_name="invoices")
    op.drop_index("idx_invoices_hash_sha256", table_name="invoices")
    op.drop_table("invoices")
    op.execute("DROP TYPE IF EXISTS credit_status")
    op.execute("DROP TYPE IF EXISTS invoice_status")
