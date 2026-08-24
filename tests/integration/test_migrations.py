import asyncio
from pathlib import Path

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.integration


def _alembic_config(database_url: str) -> Config:
    alembic_cfg = Config(str(MIGRATIONS_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    return alembic_cfg


def _swap_database(url: str, database: str) -> str:
    head = url.rpartition("/")[0]
    return f"{head}/{database}"


def _raw_dsn(url: str) -> str:
    """Strip the SQLAlchemy driver suffix for plain asyncpg connections."""
    return url.replace("+asyncpg", "")


async def _create_database(admin_url: str, database: str) -> None:
    conn = await asyncpg.connect(_raw_dsn(admin_url))
    try:
        await conn.execute(f'CREATE DATABASE "{database}"')
    finally:
        await conn.close()


async def _drop_database(admin_url: str, database: str) -> None:
    conn = await asyncpg.connect(_raw_dsn(admin_url))
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')
    finally:
        await conn.close()


async def _introspect(url: str) -> tuple[str | None, str | None, str | None]:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            tables = await conn.scalar(
                text(
                    "SELECT string_agg(tablename, ',' ORDER BY tablename) "
                    "FROM pg_tables WHERE schemaname = 'public'"
                )
            )
            enums = await conn.scalar(
                text(
                    "SELECT string_agg(typname, ',' ORDER BY typname) "
                    "FROM pg_type WHERE typtype = 'e'"
                )
            )
            partial_index = await conn.scalar(
                text(
                    "SELECT indexdef FROM pg_indexes "
                    "WHERE indexname = 'idx_invoices_status_created_at'"
                )
            )
            return tables, enums, partial_index
    finally:
        await engine.dispose()


def test_upgrade_head_creates_fase04_schema(postgres_url: str) -> None:
    admin_url = _swap_database(postgres_url, "postgres")
    migration_db = _swap_database(postgres_url, "ecotrace_migration_test")
    asyncio.run(_drop_database(admin_url, "ecotrace_migration_test"))
    asyncio.run(_create_database(admin_url, "ecotrace_migration_test"))

    try:
        command.upgrade(_alembic_config(migration_db), "head")

        tables, enums, partial_index = asyncio.run(_introspect(migration_db))

        assert tables is not None
        for table in ("invoices", "invoice_items", "recycling_credits"):
            assert table in tables
        assert enums is not None
        for enum in ("invoice_status", "credit_status"):
            assert enum in enums
        assert partial_index is not None
        assert "PENDING" in str(partial_index)

        command.downgrade(_alembic_config(migration_db), "base")
        tables_after_downgrade, _, _ = asyncio.run(_introspect(migration_db))
        assert tables_after_downgrade is not None
        assert "invoices" not in tables_after_downgrade
        assert "recycling_credits" not in tables_after_downgrade
    finally:
        asyncio.run(_drop_database(admin_url, "ecotrace_migration_test"))
