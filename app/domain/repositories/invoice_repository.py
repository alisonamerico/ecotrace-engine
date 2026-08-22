from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.aggregates.invoice import Invoice


class InvoiceRepositoryInterface(ABC):
    """Abstract interface for Invoice persistence operations."""

    @abstractmethod
    async def save(self, invoice: Invoice) -> Invoice:
        """Persist or update an invoice aggregate and its items."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, invoice_id: UUID) -> Invoice | None:
        """Find an invoice by primary UUID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_tracking_id(self, tracking_id: UUID) -> Invoice | None:
        """Find an invoice by tracking UUID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_hash(self, hash_sha256: str) -> Invoice | None:
        """Find an invoice by SHA-256 hash."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_access_key(self, access_key: str) -> Invoice | None:
        """Find an invoice by 44-digit access key."""
        raise NotImplementedError
