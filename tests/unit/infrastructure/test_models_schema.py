from sqlalchemy import Index

from app.domain.aggregates.invoice import InvoiceStatus
from app.domain.entities.credit import CreditStatus
from app.infrastructure.database.models.credit_model import CreditModel
from app.infrastructure.database.models.invoice_model import InvoiceModel
from app.infrastructure.database.models.item_model import InvoiceItemModel


def _index_by_name(model: type, name: str) -> Index:
    indexes = {idx.name: idx for idx in model.__table__.indexes}
    assert name in indexes, f"Index {name} not found on {model.__tablename__}"
    return indexes[name]


def _constraint_names(model: type) -> set[str]:
    return {constraint.name for constraint in model.__table__.constraints if constraint.name}


def test_invoice_constraints_match_fase04() -> None:
    constraints = _constraint_names(InvoiceModel)
    assert "chk_access_key_length" in constraints
    assert "chk_hash_sha256_length" in constraints


def test_invoice_native_enum_types_match_fase04() -> None:
    status_type = InvoiceModel.__table__.c.status.type
    assert status_type.name == "invoice_status"
    assert status_type.enum_class is InvoiceStatus


def test_invoice_performance_indexes_match_reference_sql() -> None:
    hash_idx = _index_by_name(InvoiceModel, "idx_invoices_hash_sha256")
    assert hash_idx.dialect_options["postgresql"]["using"] == "hash"

    tracking_idx = _index_by_name(InvoiceModel, "idx_invoices_tracking_id")
    assert [col.name for col in tracking_idx.columns] == ["tracking_id"]

    status_idx = _index_by_name(InvoiceModel, "idx_invoices_status_created_at")
    assert [col.name for col in status_idx.columns] == ["status", "created_at"]
    where_clause = str(status_idx.dialect_options["postgresql"]["where"])
    assert "PENDING" in where_clause and "PROCESSING" in where_clause


def test_invoice_item_index_matches_reference_sql() -> None:
    idx = _index_by_name(InvoiceItemModel, "idx_invoice_items_invoice_id")
    assert [col.name for col in idx.columns] == ["invoice_id"]


def test_credit_schema_matches_fase04() -> None:
    status_type = CreditModel.__table__.c.status.type
    assert status_type.name == "credit_status"
    assert status_type.enum_class is CreditStatus

    idx = _index_by_name(CreditModel, "idx_recycling_credits_material_status")
    assert [col.name for col in idx.columns] == ["material_family", "status"]

    invoice_id_column = CreditModel.__table__.c.invoice_id
    assert invoice_id_column.unique
