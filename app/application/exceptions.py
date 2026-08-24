"""Application-layer exceptions mapped to HTTP semantics by the API edge."""


class ApplicationError(Exception):
    """Base exception for application use case failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DuplicateInvoiceError(ApplicationError):
    """Raised when an invoice with the same SHA-256 hash was already ingested."""

    def __init__(self, hash_sha256: str) -> None:
        super().__init__(
            f"Invoice with hash {hash_sha256} has already been ingested "
            "and cannot be processed again"
        )
        self.hash_sha256 = hash_sha256


class InvoiceNotFoundError(ApplicationError):
    """Raised when no invoice matches the requested tracking identifier."""

    def __init__(self, tracking_id: str) -> None:
        super().__init__(f"No invoice found for tracking_id {tracking_id}")
        self.tracking_id = tracking_id
