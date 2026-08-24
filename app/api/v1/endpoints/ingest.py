from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_ingest_use_case
from app.application.dtos.invoice_dto import IngestInvoiceRequest, IngestInvoiceResponse
from app.application.exceptions import DuplicateInvoiceError
from app.application.use_cases.ingest_invoice import IngestInvoice

router = APIRouter()


@router.post(
    "/ingest",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestInvoiceResponse,
)
async def ingest_invoice(
    request: IngestInvoiceRequest,
    use_case: Annotated[IngestInvoice, Depends(get_ingest_use_case)],
) -> IngestInvoiceResponse:
    """Accept an NF-e for asynchronous processing and return its tracking id."""
    try:
        return await use_case.execute(request)
    except DuplicateInvoiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=exc.message
        ) from exc
