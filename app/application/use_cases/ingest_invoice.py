import json

from app.application.dtos.invoice_dto import IngestInvoiceRequest, IngestInvoiceResponse
from app.application.exceptions import DuplicateInvoiceError
from app.application.interfaces.message_broker import MessageBroker
from app.domain.aggregates.invoice import Invoice
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.exceptions import FraudDetectedException
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface
from app.domain.services.fraud_detector import FraudDetectorService
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM

NFE_EXCHANGE = "ecotrace.events"
NFE_RECEIVED_ROUTING_KEY = "nfe.received"


class IngestInvoice:
    """Use case: validate, persist and hand off an NF-e for async processing."""

    def __init__(
        self,
        repository: InvoiceRepositoryInterface,
        broker: MessageBroker,
    ) -> None:
        self._repository = repository
        self._broker = broker
        self._fraud_detector = FraudDetectorService()

    async def execute(self, request: IngestInvoiceRequest) -> IngestInvoiceResponse:
        invoice = self._build_aggregate(request)

        existing = await self._repository.find_by_hash(invoice.hash_sha256)
        self._guard_against_duplication(existing, invoice)

        await self._repository.save(invoice)
        await self._publish_received_event(invoice)

        return IngestInvoiceResponse(
            tracking_id=invoice.tracking_id,
            status=invoice.status.value,
        )

    @staticmethod
    def _build_aggregate(request: IngestInvoiceRequest) -> Invoice:
        invoice = Invoice(
            access_key=AccessKey(request.access_key),
            issuer_cnpj=CNPJ(request.issuer_cnpj),
            recipient_cnpj=CNPJ(request.recipient_cnpj),
        )
        for item in request.items:
            invoice.add_item(
                InvoiceItem(
                    item_number=item.item_number,
                    description=item.description,
                    ncm=NCM(item.ncm_code),
                    gross_weight=RecyclableMass(item.gross_weight_kg),
                )
            )
        return invoice

    def _guard_against_duplication(self, existing: Invoice | None, incoming: Invoice) -> None:
        try:
            is_duplicate = self._fraud_detector.verify_duplication(existing, incoming)
        except FraudDetectedException as exc:
            raise DuplicateInvoiceError(incoming.hash_sha256) from exc
        if is_duplicate:
            raise DuplicateInvoiceError(incoming.hash_sha256)

    async def _publish_received_event(self, invoice: Invoice) -> None:
        event = {
            "tracking_id": str(invoice.tracking_id),
            "invoice_id": str(invoice.id),
            "access_key": invoice.access_key.value,
            "hash_sha256": invoice.hash_sha256,
        }
        await self._broker.publish(
            NFE_EXCHANGE,
            NFE_RECEIVED_ROUTING_KEY,
            json.dumps(event).encode("utf-8"),
        )
