from collections.abc import AsyncGenerator, Generator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer

from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.entities.credit import CreditStatus, RecyclingCredit
from app.domain.entities.invoice_item import InvoiceItem
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.domain.value_objects.mass import RecyclableMass
from app.domain.value_objects.ncm import NCM
from app.infrastructure.database.models.base import Base


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str]:
    """Start an isolated PostgreSQL 16 container for the whole test session."""
    with PostgresContainer(
        "postgres:16-alpine", username="ecotrace", password="ecotrace", dbname="ecotrace_test"
    ) as postgres:
        url = postgres.get_connection_url().replace("+psycopg2", "+asyncpg")
        yield url


@pytest.fixture
async def db_session(postgres_url: str) -> AsyncGenerator[AsyncSession]:
    """Provide a clean-schema AsyncSession backed by the container database."""
    engine = create_async_engine(postgres_url, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            await conn.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            yield session

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    finally:
        await engine.dispose()


_INVOICE_KEY_SEQUENCE = iter(range(1, 1000))


@pytest.fixture
def make_invoice():
    """Build a valid Invoice aggregate with default eligible items."""

    def _factory(
        status: InvoiceStatus = InvoiceStatus.PENDING,
        items: list[InvoiceItem] | None = None,
    ) -> Invoice:
        sequence = str(next(_INVOICE_KEY_SEQUENCE)).zfill(10)
        invoice = Invoice(
            access_key=AccessKey(f"3524011234567800019055001000000123{sequence}"),
            issuer_cnpj=CNPJ("11222333000181"),
            recipient_cnpj=CNPJ("04252011000110"),
            status=status,
        )
        if items is None:
            items = [
                InvoiceItem(
                    item_number=1,
                    description="Aparas de PET",
                    ncm=NCM("39159000"),
                    gross_weight=RecyclableMass("1500.000"),
                ),
                InvoiceItem(
                    item_number=2,
                    description="Sucata de aluminio",
                    ncm=NCM("76020000"),
                    gross_weight=RecyclableMass("500.500"),
                ),
            ]
        for item in items:
            invoice.add_item(item)
        return invoice

    return _factory


@pytest.fixture
def make_credit():
    """Build a valid RecyclingCredit entity bound to an invoice."""

    def _factory(invoice_id) -> RecyclingCredit:
        return RecyclingCredit(
            invoice_id=invoice_id,
            credit_code="CRED-20260824-PLASTICO-TEST0001",
            material_family="PLASTICO",
            total_weight=RecyclableMass("1500.000"),
            status=CreditStatus.AVAILABLE,
        )

    return _factory
