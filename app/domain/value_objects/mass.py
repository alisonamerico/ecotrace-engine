from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Self

from app.domain.exceptions import InvalidMassException


@dataclass(frozen=True)
class RecyclableMass:
    """Encapsulates recyclable mass in kilograms with 3 decimal precision."""

    value_kg: Decimal

    def __init__(self, value: Decimal | float | int | str) -> None:
        dec_value = value if isinstance(value, Decimal) else Decimal(str(value))
        normalized = dec_value.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        if normalized <= Decimal("0.000"):
            raise InvalidMassException(
                f"Recyclable mass must be strictly positive, got {normalized} kg"
            )

        object.__setattr__(self, "value_kg", normalized)

    def to_tons(self) -> Decimal:
        """Convert mass in kg to metric tons."""
        return (self.value_kg / Decimal("1000")).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        return self.__class__(self.value_kg + other.value_kg)

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        result = self.value_kg - other.value_kg
        if result <= Decimal("0.000"):
            raise InvalidMassException("Subtracted mass cannot result in zero or negative value")
        return self.__class__(result)

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        return self.value_kg < other.value_kg

    def __le__(self, other: Self) -> bool:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        return self.value_kg <= other.value_kg

    def __gt__(self, other: Self) -> bool:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        return self.value_kg > other.value_kg

    def __ge__(self, other: Self) -> bool:
        if not isinstance(other, RecyclableMass):
            return NotImplemented
        return self.value_kg >= other.value_kg

    def __str__(self) -> str:
        return f"{self.value_kg} kg"
