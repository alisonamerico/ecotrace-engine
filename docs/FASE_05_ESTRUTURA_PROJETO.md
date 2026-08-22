# FASE 05 — Estrutura do Projeto

## 1. Árvore de Diretórios (Clean Architecture / DDD)

```text
ecotrace-engine/
├── app/
│   ├── api/             # Endpoints FastAPI, Middlewares, Schemas HTTP
│   ├── application/     # Casos de Uso (Use Cases), DTOs, Interfaces
│   ├── core/            # Configurações, Logging, Segurança, Telemetria
│   ├── domain/          # Value Objects, Aggregates, Domain Services, Interfaces
│   ├── infrastructure/  # SQLAlchemy, Redis Locks, RabbitMQ, Clientes HTTP
│   └── workers/         # Instância Celery, Tarefas Assíncronas (Tasks)
├── deploy/              # Manifestos Kubernetes (Deployments, Services, HPA)
├── docker/              # Dockerfile e docker-compose.yml
├── migrations/          # Versionamento com Alembic Assíncrono
├── tests/               # Unitários, Integração e End-to-End
├── pyproject.toml       # Gerenciamento via uv (Python 3.13)
└── README.md
```

## Full view:

```text
ecotrace-engine/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── deploy/
│   └── k8s/
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── postgres-pvc.yaml
│       ├── api-deployment.yaml
│       ├── api-service.yaml
│       ├── worker-deployment.yaml
│       ├── hpa.yaml
│       └── ingress.yaml
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── prometheus.yml
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── telemetry.py
│   │   └── security.py
│   ├── domain/
│   │   ├── exceptions.py
│   │   ├── value_objects/
│   │   │   ├── access_key.py
│   │   │   ├── cnpj.py
│   │   │   ├── ncm.py
│   │   │   └── mass.py
│   │   ├── entities/
│   │   │   ├── invoice_item.py
│   │   │   └── credit.py
│   │   ├── aggregates/
│   │   │   └── invoice.py
│   │   ├── events/
│   │   │   └── invoice_events.py
│   │   ├── services/
│   │   │   ├── fraud_detector.py
│   │   │   └── ncm_parser.py
│   │   └── repositories/
│   │       ├── invoice_repository.py
│   │       └── credit_repository.py
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── invoice_dto.py
│   │   │   └── credit_dto.py
│   │   ├── use_cases/
│   │   │   ├── ingest_invoice.py
│   │   │   ├── process_invoice_audit.py
│   │   │   └── get_invoice_status.py
│   │   └── interfaces/
│   │       ├── message_broker.py
│   │       ├── lock_manager.py
│   │       └── sefaz_client.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   ├── models/
│   │   │   │   ├── invoice_model.py
│   │   │   │   ├── item_model.py
│   │   │   │   └── credit_model.py
│   │   │   ├── mappers/
│   │   │   │   └── invoice_mapper.py
│   │   │   └── repositories/
│   │   │       ├── invoice_repository_impl.py
│   │   │       └── credit_repository_impl.py
│   │   ├── messaging/
│   │   │   ├── rabbitmq.py
│   │   │   └── publisher.py
│   │   ├── cache/
│   │   │   └── redis_lock.py
│   │   └── external/
│   │       └── sefaz_client_mock.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py
│   │   │   ├── endpoints/
│   │   │   │   ├── ingest.py
│   │   │   │   ├── status.py
│   │   │   │   └── health.py
│   │   │   └── dependencies.py
│   │   └── middlewares/
│   │       ├── correlation_id.py
│   │       └── metrics_middleware.py
│   └── workers/
│       ├── celery_app.py
│       └── tasks/
│           ├── audit_tasks.py
│           └── reconciliation_tasks.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   ├── integration/
│   │   ├── repositories/
│   │   └── messaging/
│   └── e2e/
│       └── api/
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── ruff.toml
└── README.md
```
