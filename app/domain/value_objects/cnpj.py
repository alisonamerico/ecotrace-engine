import re
from dataclasses import dataclass

from app.domain.exceptions import InvalidCNPJException


@dataclass(frozen=True)
class CNPJ:
    """Encapsulates a Brazilian CNPJ document with check-digit validation."""

    value: str

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\D", "", self.value.strip())
        if len(cleaned) != 14:
            raise InvalidCNPJException(f"CNPJ must have 14 digits, got {len(cleaned)}")

        # Check for known invalid repeated sequences
        if len(set(cleaned)) == 1:
            raise InvalidCNPJException("CNPJ cannot consist of repeated digits")

        if not self._validate_check_digits(cleaned):
            raise InvalidCNPJException("CNPJ check digits verification failed")

        object.__setattr__(self, "value", cleaned)

    @staticmethod
    def _validate_check_digits(cnpj: str) -> bool:
        weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        # First check digit
        total = sum(int(cnpj[i]) * weights_first[i] for i in range(12))
        remainder = total % 11
        first_digit = 0 if remainder < 2 else 11 - remainder

        if int(cnpj[12]) != first_digit:
            return False

        # Second check digit
        total = sum(int(cnpj[i]) * weights_second[i] for i in range(13))
        remainder = total % 11
        second_digit = 0 if remainder < 2 else 11 - remainder

        return int(cnpj[13]) == second_digit

    @property
    def formatted(self) -> str:
        """Return CNPJ formatted as XX.XXX.XXX/XXXX-XX."""
        c = self.value
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"

    def __str__(self) -> str:
        return self.value
