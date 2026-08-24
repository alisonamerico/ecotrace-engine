from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.entities.credit import CreditStatus, RecyclingCredit
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM
from app.infrastructure.database.mappers.credit_mapper import CreditMapper
from app.infrastructure.database.mappers.invoice_mapper import InvoiceMapper


def test_invoice_mapper_entity_to_model_and_back() -> None:
    inv_id = uuid4()
    item_id = uuid4()
    now = datetime.now(UTC)

    invoice = Invoice(
        id=inv_id,
        tracking_id=uuid4(),
        access_key=AccessKey("35240112345678000190550010000001231234567890"),
        issuer_cnpj=CNPJ("12345678000195"),
        recipient_cnpj=CNPJ("04252011000110"),
        status=InvoiceStatus.APPROVED,
        sefaz_status="100 - Autorizado",
        rejection_reason=None,
        created_at=now,
        updated_at=now,
    )
    item = InvoiceItem(
        id=item_id,
        item_number=1,
        description="Aparas de PET",
        ncm=NCM("39159000"),
        gross_weight=RecyclableMass(Decimal("2500.000")),
        created_at=now,
    )
    invoice.add_item(item)

    model = InvoiceMapper.to_model(invoice)
    assert model.id == inv_id
    assert model.access_key == "35240112345678000190550010000001231234567890"
    assert model.hash_sha256 == invoice.hash_sha256
    assert model.status == "APPROVED"
    assert len(model.items) == 1
    assert model.items[0].ncm_code == "39159000"
    assert model.items[0].gross_weight_kg == Decimal("2500.000")

    entity_restored = InvoiceMapper.to_entity(model)
    assert entity_restored.id == inv_id
    assert entity_restored.access_key.value == "35240112345678000190550010000001231234567890"
    assert entity_restored.status == InvoiceStatus.APPROVED
    assert len(entity_restored.items) == 1
    assert entity_restored.items[0].ncm.code == "39159000"
    assert entity_restored.items[0].gross_weight.value_kg == Decimal("2500.000")


def test_credit_mapper_entity_to_model_and_back() -> None:
    credit_id = uuid4()
    inv_id = uuid4()
    now = datetime.now(UTC)

    credit = RecyclingCredit(
        id=credit_id,
        invoice_id=inv_id,
        credit_code="CRED-2026-0001",
        material_family="PLASTICO",
        total_weight=RecyclableMass(Decimal("1500.000")),
        status=CreditStatus.AVAILABLE,
        created_at=now,
    )

    model = CreditMapper.to_model(credit)
    assert model.id == credit_id
    assert model.invoice_id == inv_id
    assert model.credit_code == "CRED-2026-0001"
    assert model.material_family == "PLASTICO"
    assert model.total_weight_kg == Decimal("1500.000")
    assert model.status == "AVAILABLE"

    entity_restored = CreditMapper.to_entity(model)
    assert entity_restored.id == credit_id
    assert entity_restored.invoice_id == inv_id
    assert entity_restored.credit_code == "CRED-2026-0001"
    assert entity_restored.material_family == "PLASTICO"
    assert entity_restored.total_weight.value_kg == Decimal("1500.000")
    assert entity_restored.status == CreditStatus.AVAILABLE
