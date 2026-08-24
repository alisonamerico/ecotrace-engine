from uuid import UUID

from sqlalchemy import ColumnExpressionArgument, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.credit import RecyclingCredit
from app.domain.repositories.credit_repository import CreditRepositoryInterface
from app.infrastructure.database.mappers.credit_mapper import CreditMapper
from app.infrastructure.database.models.credit_model import CreditModel


class CreditRepositoryImpl(CreditRepositoryInterface):
    """Async PostgreSQL implementation of the RecyclingCredit persistence contract."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, credit: RecyclingCredit) -> RecyclingCredit:
        """Insert or update a recycling credit."""
        model = await self._session.get(CreditModel, credit.id)
        if model is None:
            self._session.add(CreditMapper.to_model(credit))
        else:
            self._apply_entity(model, credit)
        await self._session.flush()
        return credit

    async def find_by_id(self, credit_id: UUID) -> RecyclingCredit | None:
        return await self._find_one(CreditModel.id == credit_id)

    async def find_by_invoice_id(self, invoice_id: UUID) -> list[RecyclingCredit]:
        result = await self._session.execute(
            select(CreditModel).where(CreditModel.invoice_id == invoice_id)
        )
        return [CreditMapper.to_entity(model) for model in result.scalars().all()]

    async def find_by_credit_code(self, credit_code: str) -> RecyclingCredit | None:
        return await self._find_one(CreditModel.credit_code == credit_code)

    async def _find_one(
        self, *criteria: ColumnExpressionArgument[bool]
    ) -> RecyclingCredit | None:
        result = await self._session.execute(select(CreditModel).where(*criteria))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return CreditMapper.to_entity(model)

    @staticmethod
    def _apply_entity(model: CreditModel, entity: RecyclingCredit) -> None:
        model.invoice_id = entity.invoice_id
        model.credit_code = entity.credit_code
        model.material_family = entity.material_family
        model.total_weight_kg = entity.total_weight.value_kg
        model.status = entity.status
