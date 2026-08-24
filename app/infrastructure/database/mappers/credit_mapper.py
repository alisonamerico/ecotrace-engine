from app.domain.entities.credit import RecyclingCredit
from app.domain.value_objects.mass import RecyclableMass
from app.infrastructure.database.models.credit_model import CreditModel


class CreditMapper:
    """Explicit mapper translating between RecyclingCredit entity and SQLAlchemy CreditModel."""

    @staticmethod
    def to_model(entity: RecyclingCredit) -> CreditModel:
        return CreditModel(
            id=entity.id,
            invoice_id=entity.invoice_id,
            credit_code=entity.credit_code,
            material_family=entity.material_family,
            total_weight_kg=entity.total_weight.value_kg,
            status=entity.status,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_entity(model: CreditModel) -> RecyclingCredit:
        return RecyclingCredit(
            id=model.id,
            invoice_id=model.invoice_id,
            credit_code=model.credit_code,
            material_family=model.material_family,
            total_weight=RecyclableMass(model.total_weight_kg),
            status=model.status,
            created_at=model.created_at,
        )
