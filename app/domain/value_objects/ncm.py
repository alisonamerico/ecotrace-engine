import re
from dataclasses import dataclass
from typing import ClassVar

from app.domain.exceptions import InvalidNCMException


@dataclass(frozen=True)
class NCM:
    """Encapsulates Mercosul NCM classification and recyclable material mapping."""

    code: str

    RECYCLABLE_MAP: ClassVar[dict[str, str]] = {
        "3915": "PLASTICO",  # Resíduos, desperdícios e aparas de plásticos
        "4707": "PAPEL",  # Papel ou cartão para reciclar
        "7001": "VIDRO",  # Cacos de vidro e outros desperdícios de vidro
        "7204": "METAL",  # Desperdícios e resíduos de ferro fundido/ferro/aço
        "7602": "METAL",  # Desperdícios e resíduos de alumínio
    }

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\D", "", self.code.strip())
        if len(cleaned) != 8:
            raise InvalidNCMException(f"NCM code must have 8 digits, got {len(cleaned)}")

        object.__setattr__(self, "code", cleaned)

    @property
    def is_recyclable(self) -> bool:
        """Check if the NCM code belongs to recognized recyclable material chapters."""
        prefix = self.code[:4]
        return prefix in self.RECYCLABLE_MAP

    @property
    def material_family(self) -> str | None:
        """Return material family if recyclable, else None."""
        prefix = self.code[:4]
        return self.RECYCLABLE_MAP.get(prefix)

    def __str__(self) -> str:
        return self.code
