from uuid import UUID

from app.domain.aggregates.invoice import Invoice
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM
from app.infrastructure.database.models.invoice_model import InvoiceModel
from app.infrastructure.database.models.item_model import InvoiceItemModel


class InvoiceMapper:
    """Explicit mapper translating between Invoice aggregate and SQLAlchemy InvoiceModel."""

    @staticmethod
    def to_model(entity: Invoice) -> InvoiceModel:
        model = InvoiceModel(
            id=entity.id,
            tracking_id=entity.tracking_id,
            access_key=entity.access_key.value,
            hash_sha256=entity.hash_sha256,
            issuer_cnpj=entity.issuer_cnpj.value,
            recipient_cnpj=entity.recipient_cnpj.value,
            status=entity.status,
            sefaz_status=entity.sefaz_status,
            rejection_reason=entity.rejection_reason,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        model.items = [InvoiceMapper.to_item_model(item, entity.id) for item in entity.items]
        return model

    @staticmethod
    def to_entity(model: InvoiceModel) -> Invoice:
        items = [InvoiceMapper.to_item_entity(item_model) for item_model in model.items]
        return Invoice(
            id=model.id,
            tracking_id=model.tracking_id,
            access_key=AccessKey(model.access_key),
            issuer_cnpj=CNPJ(model.issuer_cnpj),
            recipient_cnpj=CNPJ(model.recipient_cnpj),
            status=model.status,
            sefaz_status=model.sefaz_status,
            rejection_reason=model.rejection_reason,
            items=items,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_item_model(item: InvoiceItem, invoice_id: UUID) -> InvoiceItemModel:
        return InvoiceItemModel(
            id=item.id,
            invoice_id=invoice_id,
            item_number=item.item_number,
            description=item.description,
            ncm_code=item.ncm.code,
            gross_weight_kg=item.gross_weight.value_kg,
            is_eligible=item.is_eligible,
            created_at=item.created_at,
        )

    @staticmethod
    def to_item_entity(model: InvoiceItemModel) -> InvoiceItem:
        return InvoiceItem(
            id=model.id,
            item_number=model.item_number,
            description=model.description,
            ncm=NCM(model.ncm_code),
            gross_weight=RecyclableMass(model.gross_weight_kg),
            created_at=model.created_at,
        )
