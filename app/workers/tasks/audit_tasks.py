import asyncio
from typing import Any

import structlog
from redis.asyncio import Redis

from app.core.config import get_settings
from app.domain.aggregates.invoice import Invoice, InvoiceStatus
from app.domain.services.fraud_detector import FraudDetectorService
from app.domain.services.ncm_parser import NCMParserService
from app.domain.value_objects.access_key import AccessKey
from app.domain.value_objects.cnpj import CNPJ
from app.infrastructure.cache.redis_lock import RedisLockManager
from app.infrastructure.database.repositories.credit_repository_impl import (
    CreditRepositoryImpl,
)
from app.infrastructure.database.repositories.invoice_repository_impl import (
    InvoiceRepositoryImpl,
)
from app.infrastructure.database.session import get_async_session_factory
from app.infrastructure.external.sefaz_client_mock import MockSEFAZClient
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)  # type: ignore[untyped-decorator]
def process_invoice_event(  # type: ignore[no-untyped-def]
    self, event_payload: dict[str, Any]
) -> dict[str, str]:
    """Celery task: async processing pipeline for a single NF-e (RF02-RF06)."""
    return asyncio.run(_handle(self, event_payload))


async def _handle(task: Any, payload: dict[str, Any]) -> dict[str, str]:
    logger = structlog.get_logger()
    settings = get_settings()
    hash_sha256 = payload["hash_sha256"]

    logger.info("processing_invoice", tracking_id=payload["tracking_id"], hash=hash_sha256)

    redis = Redis.from_url(settings.redis_connection_url)
    lock_manager = RedisLockManager(redis_client=redis)
    lock_key = f"lock:nfe:{hash_sha256}"

    try:
        acquired = await lock_manager.acquire(lock_key, ttl_seconds=300)
        if not acquired:
            logger.warning("lock_not_acquired", hash=hash_sha256)
            raise task.retry(countdown=60)

        try:
            return await _process_invoice(payload, hash_sha256, logger)
        finally:
            await lock_manager.release(lock_key)
    finally:
        await redis.aclose()


async def _process_invoice(
    payload: dict[str, Any], hash_sha256: str, logger: Any
) -> dict[str, str]:
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        invoice_repo = InvoiceRepositoryImpl(session)
        existing = await invoice_repo.find_by_hash(hash_sha256)

        fraud_detector = FraudDetectorService()
        if existing is not None:
            try:
                fraud_detector.verify_duplication(existing, existing)
            except Exception:
                existing.status = InvoiceStatus.FRAUD_SUSPECT
                existing.rejection_reason = f"Double use detected: hash {hash_sha256}"
                await invoice_repo.save(existing)
                await session.commit()
                logger.warning("fraud_detected", invoice_id=str(existing.id), hash=hash_sha256)
                return {"status": "FRAUD_SUSPECT", "invoice_id": str(existing.id)}

        invoice = Invoice(
            access_key=AccessKey(payload["access_key"]),
            issuer_cnpj=CNPJ(payload["issuer_cnpj"]),
            recipient_cnpj=CNPJ(payload["recipient_cnpj"]),
            status=InvoiceStatus.PROCESSING,
        )
        invoice.tracking_id = payload["tracking_id"]

        sefaz_response = await MockSEFAZClient().consult(payload["access_key"])

        if not sefaz_response.authorized:
            invoice.status = InvoiceStatus.REJECTED
            invoice.rejection_reason = sefaz_response.motivo
        else:
            invoice.status = InvoiceStatus.APPROVED
            invoice.sefaz_status = sefaz_response.motivo

        await invoice_repo.save(invoice)

        if invoice.status == InvoiceStatus.APPROVED:
            credits = NCMParserService().generate_credits_from_invoice(invoice)
            credit_repo = CreditRepositoryImpl(session)
            for credit in credits:
                await credit_repo.save(credit)

        await session.commit()

        logger.info("invoice_processed", invoice_id=str(invoice.id), status=invoice.status.value)
        return {"status": invoice.status.value, "invoice_id": str(invoice.id)}
