"""In-memory fakes for application-layer unit tests (no infrastructure)."""

from uuid import UUID

from app.application.interfaces.message_broker import MessageBroker
from app.domain.aggregates.invoice import Invoice
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface


class FakeInvoiceRepository(InvoiceRepositoryInterface):
    """Fake repository storing invoices keyed by their SHA-256 hash."""

    def __init__(self, existing_invoices: list[Invoice] | None = None) -> None:
        self._invoices_by_hash: dict[str, Invoice] = {}
        for invoice in existing_invoices or []:
            self._invoices_by_hash[invoice.hash_sha256] = invoice

    def saved_by_hash(self) -> dict[str, Invoice]:
        return dict(self._invoices_by_hash)

    async def save(self, invoice: Invoice) -> Invoice:
        self._invoices_by_hash[invoice.hash_sha256] = invoice
        return invoice

    async def find_by_id(self, invoice_id: UUID) -> Invoice | None:
        for invoice in self._invoices_by_hash.values():
            if invoice.id == invoice_id:
                return invoice
        return None

    async def find_by_tracking_id(self, tracking_id: UUID) -> Invoice | None:
        for invoice in self._invoices_by_hash.values():
            if invoice.tracking_id == tracking_id:
                return invoice
        return None

    async def find_by_hash(self, hash_sha256: str) -> Invoice | None:
        return self._invoices_by_hash.get(hash_sha256)

    async def find_by_access_key(self, access_key: str) -> Invoice | None:
        for invoice in self._invoices_by_hash.values():
            if invoice.access_key.value == access_key:
                return invoice
        return None


class RecordingBroker(MessageBroker):
    """Fake broker capturing published messages in memory."""

    def __init__(self) -> None:
        self.published: list[tuple[str, str, bytes]] = []

    async def publish(self, exchange: str, routing_key: str, payload: bytes) -> None:
        self.published.append((exchange, routing_key, payload))
