from uuid import uuid4

import pytest

from app.domain.entities.credit import CreditStatus
from app.infrastructure.database.repositories.credit_repository_impl import (
    CreditRepositoryImpl,
)
from app.infrastructure.database.repositories.invoice_repository_impl import (
    InvoiceRepositoryImpl,
)

pytestmark = pytest.mark.integration


async def test_save_and_roundtrip_credit(db_session, make_invoice, make_credit) -> None:
    invoice = make_invoice()
    await InvoiceRepositoryImpl(db_session).save(invoice)

    credit = make_credit(invoice.id)
    repository = CreditRepositoryImpl(db_session)
    await repository.save(credit)
    db_session.expunge_all()

    loaded = await repository.find_by_id(credit.id)
    assert loaded is not None
    assert loaded.invoice_id == invoice.id
    assert loaded.credit_code == "CRED-20260824-PLASTICO-TEST0001"
    assert loaded.material_family == "PLASTICO"
    assert loaded.status == CreditStatus.AVAILABLE
    assert str(loaded.total_weight) == "1500.000 kg"


async def test_find_by_id_returns_none_when_missing(db_session) -> None:
    repository = CreditRepositoryImpl(db_session)
    assert await repository.find_by_id(uuid4()) is None


async def test_find_by_invoice_id_returns_credits(
    db_session, make_invoice, make_credit
) -> None:
    invoice_a = make_invoice()
    invoice_b = make_invoice()
    invoice_repository = InvoiceRepositoryImpl(db_session)
    await invoice_repository.save(invoice_a)
    await invoice_repository.save(invoice_b)

    repository = CreditRepositoryImpl(db_session)
    credit_a = make_credit(invoice_a.id)
    credit_b = make_credit(invoice_b.id)
    credit_b.credit_code = "CRED-20260824-PLASTICO-TEST0002"
    await repository.save(credit_a)
    await repository.save(credit_b)
    db_session.expunge_all()

    credits_a = await repository.find_by_invoice_id(invoice_a.id)
    credits_b = await repository.find_by_invoice_id(invoice_b.id)

    assert [credit.credit_code for credit in credits_a] == [credit_a.credit_code]
    assert [credit.credit_code for credit in credits_b] == [credit_b.credit_code]


async def test_find_by_credit_code(db_session, make_invoice, make_credit) -> None:
    invoice = make_invoice()
    await InvoiceRepositoryImpl(db_session).save(invoice)

    credit = make_credit(invoice.id)
    repository = CreditRepositoryImpl(db_session)
    await repository.save(credit)
    db_session.expunge_all()

    found = await repository.find_by_credit_code(credit.credit_code)
    assert found is not None and found.id == credit.id
    assert await repository.find_by_credit_code("MISSING") is None


async def test_status_transition_is_persisted(db_session, make_invoice, make_credit):
    invoice = make_invoice()
    await InvoiceRepositoryImpl(db_session).save(invoice)

    credit = make_credit(invoice.id)
    repository = CreditRepositoryImpl(db_session)
    await repository.save(credit)

    credit.reserve()
    await repository.save(credit)
    db_session.expunge_all()

    loaded = await repository.find_by_id(credit.id)
    assert loaded is not None
    assert loaded.status == CreditStatus.RESERVED
