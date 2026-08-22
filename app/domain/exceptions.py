"""Pure domain exceptions for EcoTrace Engine."""


class DomainException(Exception):
    """Base exception for all domain layer errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidAccessKeyException(DomainException):
    """Raised when an NF-e access key is syntactically or structurally invalid."""


class InvalidCNPJException(DomainException):
    """Raised when a CNPJ fails verification or formatting constraints."""


class InvalidNCMException(DomainException):
    """Raised when an NCM code is invalid."""


class InvalidMassException(DomainException):
    """Raised when a recyclable mass value is invalid or <= 0."""


class InvalidStateTransitionException(DomainException):
    """Raised when an illegal aggregate state transition is attempted."""


class FraudDetectedException(DomainException):
    """Raised when a potential fraud / double-spending is detected."""


class CreditGenerationException(DomainException):
    """Raised when recycling credit issuance fails domain rules."""
