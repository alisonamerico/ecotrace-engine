from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.message_broker import MessageBroker
from app.application.use_cases.get_invoice_status import GetInvoiceStatus
from app.application.use_cases.ingest_invoice import IngestInvoice
from app.domain.repositories.invoice_repository import InvoiceRepositoryInterface
from app.infrastructure.database.repositories.invoice_repository_impl import (
    InvoiceRepositoryImpl,
)
from app.infrastructure.database.session import get_db_session

get_session = get_db_session


def get_message_broker(request: Request) -> MessageBroker:
    """Return the application-scoped event publisher wired in the lifespan."""
    broker: MessageBroker = request.app.state.message_publisher
    return broker


def get_invoice_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvoiceRepositoryInterface:
    return InvoiceRepositoryImpl(session)


def get_ingest_use_case(
    repository: Annotated[InvoiceRepositoryInterface, Depends(get_invoice_repository)],
    broker: Annotated[MessageBroker, Depends(get_message_broker)],
) -> IngestInvoice:
    return IngestInvoice(repository=repository, broker=broker)


def get_status_use_case(
    repository: Annotated[InvoiceRepositoryInterface, Depends(get_invoice_repository)],
) -> GetInvoiceStatus:
    return GetInvoiceStatus(repository=repository)
