from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.entities.credit import CreditStatus, RecyclingCredit
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.exceptions import InvalidMassException, InvalidStateTransitionException
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM


def create_sample_invoice() -> Invoice:
    return Invoice(
        id=uuid4(),
        tracking_id=uuid4(),
        access_key=AccessKey("35240112345678000190550010000001231234567890"),
        issuer_cnpj=CNPJ("12345678000195"),
        recipient_cnpj=CNPJ("04252011000110"),
    )


def test_invoice_creation_defaults() -> None:
    inv = create_sample_invoice()
    assert inv.status == InvoiceStatus.PENDING
    assert inv.sefaz_status is None
    assert inv.rejection_reason is None
    assert len(inv.items) == 0


def test_invoice_start_processing_transition() -> None:
    inv = create_sample_invoice()
    inv.start_processing()
    assert inv.status == InvoiceStatus.PROCESSING


def test_invoice_approve_transition() -> None:
    inv = create_sample_invoice()
    inv.start_processing()
    inv.approve(sefaz_status="100 - Autorizado")
    assert inv.status == InvoiceStatus.APPROVED
    assert inv.sefaz_status == "100 - Autorizado"


def test_invoice_invalid_transition() -> None:
    inv = create_sample_invoice()
    # Cannot approve directly from PENDING
    with pytest.raises(InvalidStateTransitionException):
        inv.approve()

    inv.start_processing()
    inv.approve()
    # Cannot reject an already approved invoice
    with pytest.raises(InvalidStateTransitionException):
        inv.reject("Attempt to reject approved")


def test_invoice_invalid_start_processing() -> None:
    inv = create_sample_invoice()
    inv.start_processing()
    with pytest.raises(InvalidStateTransitionException):
        inv.start_processing()


def test_invoice_rejection() -> None:
    inv = create_sample_invoice()
    inv.start_processing()
    inv.reject(reason="Nota fiscal cancelada na SEFAZ", sefaz_status="101 - Cancelado")
    assert inv.status == InvoiceStatus.REJECTED
    assert inv.rejection_reason == "Nota fiscal cancelada na SEFAZ"


def test_invoice_flag_fraud() -> None:
    inv = create_sample_invoice()
    inv.start_processing()
    inv.flag_fraud(reason="Chave de acesso ja utilizada em lote anterior")
    assert inv.status == InvoiceStatus.FRAUD_SUSPECT
    assert inv.rejection_reason == "Chave de acesso ja utilizada em lote anterior"


def test_invoice_items_and_mass_calculation() -> None:
    inv = create_sample_invoice()
    item1 = InvoiceItem(
        id=uuid4(),
        item_number=1,
        description="Aparas de plastico PEAD",
        ncm=NCM("39151000"),
        gross_weight=RecyclableMass(Decimal("1000.500")),
    )
    item2 = InvoiceItem(
        id=uuid4(),
        item_number=2,
        description="Sucata de Papelao Ondulado",
        ncm=NCM("47071000"),
        gross_weight=RecyclableMass(Decimal("2500.000")),
    )
    item3 = InvoiceItem(
        id=uuid4(),
        item_number=3,
        description="Equipamento de escritorio",
        ncm=NCM("84713012"),  # Not recyclable
        gross_weight=RecyclableMass(Decimal("50.000")),
    )

    inv.add_item(item1)
    inv.add_item(item2)
    inv.add_item(item3)

    assert len(inv.items) == 3
    assert item1.is_eligible is True
    assert item2.is_eligible is True
    assert item3.is_eligible is False

    total_eligible = inv.total_eligible_mass()
    assert total_eligible.value_kg == Decimal("3500.500")


def test_invoice_total_eligible_mass_empty() -> None:
    inv = create_sample_invoice()
    with pytest.raises(InvalidMassException):
        _ = inv.total_eligible_mass()


def test_recycling_credit_reserve() -> None:
    credit = RecyclingCredit(
        id=uuid4(),
        invoice_id=uuid4(),
        credit_code="CRED-2026-0001",
        material_family="PLASTICO",
        total_weight=RecyclableMass(Decimal("1000.000")),
        status=CreditStatus.AVAILABLE,
        created_at=datetime.now(UTC),
    )
    credit.reserve()
    assert credit.status == CreditStatus.RESERVED


def test_recycling_credit_compensate() -> None:
    credit = RecyclingCredit(
        id=uuid4(),
        invoice_id=uuid4(),
        credit_code="CRED-2026-0001",
        material_family="PLASTICO",
        total_weight=RecyclableMass(Decimal("1000.000")),
        status=CreditStatus.RESERVED,
        created_at=datetime.now(UTC),
    )
    credit.compensate()
    assert credit.status == CreditStatus.COMPENSATED

    with pytest.raises(InvalidStateTransitionException):
        credit.cancel()  # Cannot cancel already compensated credit


def test_recycling_credit_invalid_transitions() -> None:
    credit = RecyclingCredit(
        id=uuid4(),
        invoice_id=uuid4(),
        credit_code="CRED-2026-0002",
        material_family="VIDRO",
        total_weight=RecyclableMass(Decimal("500.000")),
        status=CreditStatus.CANCELLED,
    )
    with pytest.raises(InvalidStateTransitionException):
        credit.reserve()
    with pytest.raises(InvalidStateTransitionException):
        credit.compensate()
