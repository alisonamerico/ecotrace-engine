import hashlib
import re
from dataclasses import dataclass, field

from app.domain.exceptions import InvalidAccessKeyException


@dataclass(frozen=True)
class AccessKey:
    """Encapsulates a 44-digit NF-e Access Key and its SHA-256 hash."""

    value: str
    hash_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\D", "", self.value.strip())
        if len(cleaned) != 44:
            raise InvalidAccessKeyException(
                f"Invalid access key length: expected 44 digits, got {len(cleaned)}"
            )

        object.__setattr__(self, "value", cleaned)
        computed_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
        object.__setattr__(self, "hash_sha256", computed_hash)

    def __str__(self) -> str:
        return self.value
