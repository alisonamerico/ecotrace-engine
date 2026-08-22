from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.exceptions import FraudDetectedException
from app.domain.services.fraud_detector import FraudDetectorService
from app.domain.services.ncm_parser import NCMParserService
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM


def create_invoice_with_key(key: str, status: InvoiceStatus = InvoiceStatus.PENDING) -> Invoice:
    return Invoice(
        id=uuid4(),
        tracking_id=uuid4(),
        access_key=AccessKey(key),
        issuer_cnpj=CNPJ("12345678000195"),
        recipient_cnpj=CNPJ("04252011000110"),
        status=status,
    )


def test_fraud_detector_detects_approved_duplicate() -> None:
    service = FraudDetectorService()
    key_str = "35240112345678000190550010000001231234567890"

    existing_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.APPROVED)
    new_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.PENDING)

    with pytest.raises(FraudDetectedException):
        service.verify_duplication(existing_invoice=existing_invoice, new_invoice=new_invoice)


def test_fraud_detector_detects_fraud_suspect_duplicate() -> None:
    service = FraudDetectorService()
    key_str = "35240112345678000190550010000001231234567890"

    existing_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.FRAUD_SUSPECT)
    new_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.PENDING)

    with pytest.raises(FraudDetectedException):
        service.verify_duplication(existing_invoice=existing_invoice, new_invoice=new_invoice)


def test_fraud_detector_pending_duplicate_returns_true() -> None:
    service = FraudDetectorService()
    key_str = "35240112345678000190550010000001231234567890"

    existing_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.PENDING)
    new_invoice = create_invoice_with_key(key_str, status=InvoiceStatus.PENDING)

    assert (
        service.verify_duplication(existing_invoice=existing_invoice, new_invoice=new_invoice)
        is True
    )


def test_fraud_detector_none_existing() -> None:
    service = FraudDetectorService()
    new_invoice = create_invoice_with_key("35240112345678000190550010000001231234567890")
    assert service.verify_duplication(existing_invoice=None, new_invoice=new_invoice) is False


def test_fraud_detector_allows_distinct_invoices() -> None:
    service = FraudDetectorService()
    key1 = "35240112345678000190550010000001231234567890"
    key2 = "35240112345678000190550010000001231234567891"

    existing_invoice = create_invoice_with_key(key1, status=InvoiceStatus.APPROVED)
    new_invoice = create_invoice_with_key(key2, status=InvoiceStatus.PENDING)

    is_duplicate = service.verify_duplication(
        existing_invoice=existing_invoice, new_invoice=new_invoice
    )
    assert is_duplicate is False


def test_ncm_parser_service_generates_credits() -> None:
    parser = NCMParserService()
    inv = create_invoice_with_key("35240112345678000190550010000001231234567890")

    item_plastic1 = InvoiceItem(
        id=uuid4(),
        item_number=1,
        description="Aparas de Polietileno",
        ncm=NCM("39151000"),
        gross_weight=RecyclableMass(Decimal("1000.000")),
    )
    item_plastic2 = InvoiceItem(
        id=uuid4(),
        item_number=2,
        description="Aparas de Poliestireno",
        ncm=NCM("39152000"),
        gross_weight=RecyclableMass(Decimal("500.000")),
    )
    item_paper = InvoiceItem(
        id=uuid4(),
        item_number=3,
        description="Papelao Kraft",
        ncm=NCM("47071000"),
        gross_weight=RecyclableMass(Decimal("2000.000")),
    )

    inv.add_item(item_plastic1)
    inv.add_item(item_plastic2)
    inv.add_item(item_paper)

    credits = parser.generate_credits_from_invoice(inv)
    assert len(credits) == 2

    plastic_credit = next(c for c in credits if c.material_family == "PLASTICO")
    paper_credit = next(c for c in credits if c.material_family == "PAPEL")

    assert plastic_credit.total_weight.value_kg == Decimal("1500.000")
    assert paper_credit.total_weight.value_kg == Decimal("2000.000")
