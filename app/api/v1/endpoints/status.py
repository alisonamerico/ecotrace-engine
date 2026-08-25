from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_status_use_case
from app.application.dtos.invoice_dto import InvoiceStatusResponse
from app.application.exceptions import InvoiceNotFoundError
from app.application.use_cases.get_invoice_status import GetInvoiceStatus

router = APIRouter()


@router.get("/status/{tracking_id}", response_model=InvoiceStatusResponse)
async def get_invoice_status(
    tracking_id: UUID,
    use_case: Annotated[GetInvoiceStatus, Depends(get_status_use_case)],
) -> InvoiceStatusResponse:
    """Return the processing status of an NF-e by its tracking id."""
    try:
        return await use_case.execute(tracking_id)
    except InvoiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
