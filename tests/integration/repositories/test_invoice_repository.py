from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.aggregates.invoice import InvoiceStatus
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM
from app.infrastructure.database.repositories.invoice_repository_impl import (
    InvoiceRepositoryImpl,
)

pytestmark = pytest.mark.integration


async def test_save_new_invoice_persists_aggregate_and_items(
    db_session, make_invoice
) -> None:
    invoice = make_invoice()
    repository = InvoiceRepositoryImpl(db_session)

    await repository.save(invoice)
    db_session.expunge_all()

    loaded = await repository.find_by_id(invoice.id)
    assert loaded is not None
    assert loaded.id == invoice.id
    assert loaded.tracking_id == invoice.tracking_id
    assert loaded.access_key.value == invoice.access_key.value
    assert loaded.hash_sha256 == invoice.hash_sha256
    assert loaded.issuer_cnpj.value == "11222333000181"
    assert loaded.recipient_cnpj.value == "04252011000110"
    assert loaded.status == InvoiceStatus.PENDING
    assert len(loaded.items) == 2


async def test_find_by_id_returns_none_when_missing(db_session) -> None:
    repository = InvoiceRepositoryImpl(db_session)
    assert await repository.find_by_id(uuid4()) is None


async def test_find_by_tracking_id_hash_and_access_key(
    db_session, make_invoice
) -> None:
    invoice = make_invoice()
    repository = InvoiceRepositoryImpl(db_session)
    await repository.save(invoice)
    db_session.expunge_all()

    by_tracking = await repository.find_by_tracking_id(invoice.tracking_id)
    by_hash = await repository.find_by_hash(invoice.hash_sha256)
    by_key = await repository.find_by_access_key(invoice.access_key.value)

    assert by_tracking is not None and by_tracking.id == invoice.id
    assert by_hash is not None and by_hash.id == invoice.id
    assert by_key is not None and by_key.id == invoice.id


async def test_update_persists_status_transition_and_new_items(
    db_session, make_invoice
) -> None:
    invoice = make_invoice()
    repository = InvoiceRepositoryImpl(db_session)

    await repository.save(invoice)
    invoice.start_processing()
    invoice.add_item(
        InvoiceItem(
            item_number=3,
            description="Papelao ondulado",
            ncm=NCM("47071000"),
            gross_weight=RecyclableMass("250.000"),
        )
    )
    await repository.save(invoice)
    db_session.expunge_all()

    loaded = await repository.find_by_id(invoice.id)
    assert loaded is not None
    assert loaded.status == InvoiceStatus.PROCESSING
    assert len(loaded.items) == 3
    eligible_total = loaded.total_eligible_mass()
    assert eligible_total.value_kg == Decimal("2250.500")


async def test_items_cascade_delete_on_replacement(db_session, make_invoice) -> None:
    invoice = make_invoice()
    repository = InvoiceRepositoryImpl(db_session)
    await repository.save(invoice)

    remaining = [item for item in invoice.items if item.item_number == 1]
    invoice.items.clear()
    for item in remaining:
        invoice.add_item(item)
    await repository.save(invoice)
    db_session.expunge_all()

    loaded = await repository.find_by_id(invoice.id)
    assert loaded is not None
    assert [item.item_number for item in loaded.items] == [1]


async def test_find_by_hash_returns_none_when_missing(db_session) -> None:
    repository = InvoiceRepositoryImpl(db_session)
    assert await repository.find_by_hash("f" * 64) is None
