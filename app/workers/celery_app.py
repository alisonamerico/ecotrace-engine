from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ecotrace_engine",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.audit_tasks.process_invoice_event": {
            "queue": "ecotrace.invoices",
        },
    },
    broker_transport_options={
        "confirm_publish": True,
        "queue_order_strategy": "fifo",
    },
)
