from uuid import UUID

from app.application.dtos.invoice_dto import InvoiceStatusResponse
from app.application.exceptions import InvoiceNotFoundError
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface


class GetInvoiceStatus:
    """Use case: expose the pipeline status of an ingested NF-e (RF07)."""

    def __init__(self, repository: InvoiceRepositoryInterface) -> None:
        self._repository = repository

    async def execute(self, tracking_id: UUID) -> InvoiceStatusResponse:
        invoice = await self._repository.find_by_tracking_id(tracking_id)
        if invoice is None:
            raise InvoiceNotFoundError(str(tracking_id))

        return InvoiceStatusResponse(
            tracking_id=invoice.tracking_id,
            access_key=invoice.access_key.value,
            status=invoice.status.value,
            sefaz_status=invoice.sefaz_status,
            rejection_reason=invoice.rejection_reason,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )
