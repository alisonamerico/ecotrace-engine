from uuid import UUID

from sqlalchemy import ColumnExpressionArgument, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.aggregates.invoice import Invoice
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface
from app.infrastructure.database.mappers.invoice_mapper import InvoiceMapper
from app.infrastructure.database.models.invoice_model import InvoiceModel


class InvoiceRepositoryImpl(InvoiceRepositoryInterface):
    """Async PostgreSQL implementation of the Invoice persistence contract."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, invoice: Invoice) -> Invoice:
        """Insert or update the aggregate and replace its items atomically."""
        model = await self._session.get(
            InvoiceModel, invoice.id, options=(selectinload(InvoiceModel.items),)
        )
        if model is None:
            self._session.add(InvoiceMapper.to_model(invoice))
        else:
            self._apply_entity(model, invoice)
        await self._session.flush()
        return invoice

    async def find_by_id(self, invoice_id: UUID) -> Invoice | None:
        return await self._find_one(InvoiceModel.id == invoice_id)

    async def find_by_tracking_id(self, tracking_id: UUID) -> Invoice | None:
        return await self._find_one(InvoiceModel.tracking_id == tracking_id)

    async def find_by_hash(self, hash_sha256: str) -> Invoice | None:
        return await self._find_one(InvoiceModel.hash_sha256 == hash_sha256)

    async def find_by_access_key(self, access_key: str) -> Invoice | None:
        return await self._find_one(InvoiceModel.access_key == access_key)

    async def _find_one(
        self, *criteria: ColumnExpressionArgument[bool]
    ) -> Invoice | None:
        statement = (
            select(InvoiceModel)
            .where(*criteria)
            .options(selectinload(InvoiceModel.items))
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return InvoiceMapper.to_entity(model)

    @staticmethod
    def _apply_entity(model: InvoiceModel, entity: Invoice) -> None:
        model.tracking_id = entity.tracking_id
        model.access_key = entity.access_key.value
        model.hash_sha256 = entity.hash_sha256
        model.issuer_cnpj = entity.issuer_cnpj.value
        model.recipient_cnpj = entity.recipient_cnpj.value
        model.status = entity.status
        model.sefaz_status = entity.sefaz_status
        model.rejection_reason = entity.rejection_reason
        model.updated_at = entity.updated_at
        model.items = [
            InvoiceMapper.to_item_model(item, entity.id) for item in entity.items
        ]
