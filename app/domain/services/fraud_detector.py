from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.exceptions import FraudDetectedException


class FraudDetectorService:
    """Domain service to detect double-spending and fraudulent reuse of NF-e hash."""

    def verify_duplication(self, existing_invoice: Invoice | None, new_invoice: Invoice) -> bool:
        """Verify whether new_invoice attempts to duplicate an existing invoice."""
        if existing_invoice is None:
            return False

        # If existing invoice has the same SHA-256 hash
        if existing_invoice.hash_sha256 == new_invoice.hash_sha256:
            if existing_invoice.status == InvoiceStatus.APPROVED:
                raise FraudDetectedException(
                    f"Duplicate invoice detected: Hash {new_invoice.hash_sha256} "
                    f"was already approved on invoice {existing_invoice.id}"
                )
            if existing_invoice.status == InvoiceStatus.FRAUD_SUSPECT:
                raise FraudDetectedException(
                    f"Fraud suspect re-entry: Hash {new_invoice.hash_sha256} "
                    f"is previously flagged as fraudulent on invoice {existing_invoice.id}"
                )
            return True

        return False
