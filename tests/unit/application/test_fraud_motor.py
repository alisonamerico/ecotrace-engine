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


def _make_invoice(status: InvoiceStatus = InvoiceStatus.APPROVED) -> Invoice:
    return Invoice(
        access_key=AccessKey("35240112345678000190550010000001230000000042"),
        issuer_cnpj=CNPJ("11222333000181"),
        recipient_cnpj=CNPJ("04252011000110"),
        status=status,
    )


def test_fraud_detector_raises_on_approved_duplicate():
    detector = FraudDetectorService()
    existing = _make_invoice(InvoiceStatus.APPROVED)
    new = _make_invoice(InvoiceStatus.PENDING)
    with pytest.raises(FraudDetectedException, match="Duplicate invoice detected"):
        detector.verify_duplication(existing, new)


def test_fraud_detector_allows_first_occurrence():
    detector = FraudDetectorService()
    result = detector.verify_duplication(None, _make_invoice())
    assert result is False


def test_fraud_detector_raises_on_fraud_reentry():
    detector = FraudDetectorService()
    existing = _make_invoice(InvoiceStatus.FRAUD_SUSPECT)
    with pytest.raises(FraudDetectedException, match="Fraud suspect re-entry"):
        detector.verify_duplication(existing, _make_invoice())


def test_ncm_parser_generates_credits():
    invoice = _make_invoice()
    invoice.add_item(
        InvoiceItem(
            item_number=1,
            description="Aparas de PET",
            ncm=NCM("39159000"),
            gross_weight=RecyclableMass("1500.000"),
        )
    )
    parser = NCMParserService()
    credits = parser.generate_credits_from_invoice(invoice)
    assert len(credits) >= 1
    assert credits[0].total_weight.value_kg > 0
