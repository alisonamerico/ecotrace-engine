from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SEFAZResponse:
    authorized: bool
    motivo: str
    status_code: int


class SEFAZClient(ABC):
    """Port for SEFAZ NF-e authorization consultation (RF04)."""

    @abstractmethod
    async def consult(self, access_key: str) -> SEFAZResponse:
        """Query SEFAZ for NF-e authorization status."""
        raise NotImplementedError
