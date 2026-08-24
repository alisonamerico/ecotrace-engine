from uuid import uuid4

import pytest

from app.application.exceptions import InvoiceNotFoundError
from app.application.use_cases.get_invoice_status import GetInvoiceStatus
from app.domain.aggregates.invoice import Invoice
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM
from tests.unit.fakes import FakeInvoiceRepository


def _build_invoice() -> Invoice:
    invoice = Invoice(
        access_key=AccessKey("35240112345678000190550010000001230000000042"),
        issuer_cnpj=CNPJ("11222333000181"),
        recipient_cnpj=CNPJ("04252011000110"),
    )
    invoice.add_item(
        InvoiceItem(
            item_number=1,
            description="Aparas de PET",
            ncm=NCM("39159000"),
            gross_weight=RecyclableMass("1500.000"),
        )
    )
    return invoice


async def test_returns_status_response_for_existing_invoice() -> None:
    invoice = _build_invoice()
    repository = FakeInvoiceRepository(existing_invoices=[invoice])
    use_case = GetInvoiceStatus(repository=repository)

    response = await use_case.execute(invoice.tracking_id)

    assert response.tracking_id == invoice.tracking_id
    assert response.access_key == invoice.access_key.value
    assert response.status == "PENDING"
    assert response.sefaz_status is None
    assert response.rejection_reason is None
    assert response.created_at == invoice.created_at
    assert response.updated_at == invoice.updated_at


async def test_raises_not_found_for_unknown_tracking_id() -> None:
    use_case = GetInvoiceStatus(repository=FakeInvoiceRepository())

    with pytest.raises(InvoiceNotFoundError):
        await use_case.execute(uuid4())
