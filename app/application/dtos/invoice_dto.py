from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceItemRequest(BaseModel):
    """Payload for a single invoice item."""

    item_number: int = Field(ge=1)
    description: str = Field(min_length=1, max_length=255)
    ncm_code: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")
    gross_weight_kg: Decimal = Field(gt=0)


class IngestInvoiceRequest(BaseModel):
    """Request body for POST /api/v1/nfe/ingest."""

    access_key: str = Field(min_length=44, max_length=44, pattern=r"^\d{44}$")
    issuer_cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    recipient_cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    items: list[InvoiceItemRequest] = Field(min_length=1)


class IngestInvoiceResponse(BaseModel):
    """Response body for a successful asynchronous ingestion (HTTP 202)."""

    tracking_id: UUID
    status: str


class InvoiceStatusResponse(BaseModel):
    """Response body for GET /api/v1/nfe/status/{tracking_id}."""

    tracking_id: UUID
    access_key: str
    status: str
    sefaz_status: str | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
