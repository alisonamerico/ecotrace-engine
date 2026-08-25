import logging
import sys

import structlog

_configured = False


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog with JSON rendering for production-ready structured logs."""
    global _configured  # noqa: PLW0603
    if _configured:
        return

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    _configured = True


def get_logger(**kwargs: object) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger (configure_logging must be called first)."""
    return structlog.get_logger(**kwargs)  # type: ignore[no-any-return]
