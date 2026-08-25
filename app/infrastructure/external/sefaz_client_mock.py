import hashlib

from app.application.interfaces.sefaz_client import SEFAZResponse


class MockSEFAZClient:
    """Simulated SEFAZ client for development/testing (RF04)."""

    AUTHORIZED_STATUS = 100
    AUTHORIZED_MESSAGE = "Autorizado o uso da NF-e"

    async def consult(self, access_key: str) -> SEFAZResponse:
        digest = hashlib.sha256(access_key.encode()).hexdigest()
        is_authorized = int(digest[:8], 16) % 100 != 0
        if is_authorized:
            return SEFAZResponse(
                authorized=True,
                motivo=self.AUTHORIZED_MESSAGE,
                status_code=self.AUTHORIZED_STATUS,
            )
        return SEFAZResponse(
            authorized=False,
            motivo="Rejeição: Nacionalidade do emitente inválida",
            status_code=257,
        )
