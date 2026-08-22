from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.credit import RecyclingCredit


class CreditRepositoryInterface(ABC):
    """Abstract interface for RecyclingCredit persistence operations."""

    @abstractmethod
    async def save(self, credit: RecyclingCredit) -> RecyclingCredit:
        """Persist or update a recycling credit."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, credit_id: UUID) -> RecyclingCredit | None:
        """Find a recycling credit by its UUID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_invoice_id(self, invoice_id: UUID) -> list[RecyclingCredit]:
        """Find all recycling credits generated for an invoice."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_credit_code(self, credit_code: str) -> RecyclingCredit | None:
        """Find a recycling credit by its unique credit code."""
        raise NotImplementedError
