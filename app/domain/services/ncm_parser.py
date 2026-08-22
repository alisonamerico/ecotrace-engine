from datetime import UTC, datetime
from uuid import uuid4

from app.domain.aggregates.invoice import Invoice
from app.domain.entities.credit import CreditStatus, RecyclingCredit
from app.domain.value_objects.mass import RecyclableMass


class NCMParserService:
    """Domain service for grouping eligible recyclable items and issuing credits."""

    def generate_credits_from_invoice(self, invoice: Invoice) -> list[RecyclingCredit]:
        """Generate RecyclingCredit domain entities grouped by material family."""
        breakdown = invoice.material_breakdown()
        credits: list[RecyclingCredit] = []

        now = datetime.now(UTC)
        date_str = now.strftime("%Y%m%d")

        for family, weight_kg in breakdown.items():
            credit_code = f"CRED-{date_str}-{family}-{str(invoice.id)[:8].upper()}"
            credit = RecyclingCredit(
                id=uuid4(),
                invoice_id=invoice.id,
                credit_code=credit_code,
                material_family=family,
                total_weight=RecyclableMass(weight_kg),
                status=CreditStatus.AVAILABLE,
                created_at=now,
            )
            credits.append(credit)

        return credits
