# EcoTrace Engine

Motor distribuído de ingestão e conciliação antifraude de Notas Fiscais para o ecossistema Eureciclo.

## Visão Geral

O EcoTrace Engine valida NF-e em tempo real, detecta fraude por dupla contagem e gera Recycling Credits auditáveis — tudo via pipeline assíncrono de alta performance.

**Fluxo principal:**

```
                ┌──────────────┐
  NF-e ──────► │  FastAPI API  │ ──► 202 Accepted + tracking_id
  (JSON)       │  POST /nfe    │
                └──────┬───────┘
                       │ publica evento
                       ▼
                ┌──────────────┐
                │   RabbitMQ   │ (exchange: ecotrace.events)
                └──────┬───────┘
                       │ consome
                       ▼
                ┌──────────────┐    ┌─────────────┐
                │ Celery Worker│───►│ Redis Lock   │
                │ (fraud motor)│    │ SET NX EX   │
                └──┬───┬───┬──┘    └─────────────┘
                   │   │   │
          ┌────────┘   │   └────────┐
          ▼            ▼            ▼
     ┌─────────┐ ┌──────────┐ ┌──────────┐
     │PostgreSQL│ │Mock SEFAZ│ │  Credits  │
     │ (Status) │ │(auth/deny)│ │(approved) │
     └─────────┘ └──────────┘ └──────────┘
```

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Runtime | Python 3.13+ |
| Framework API | FastAPI (Pydantic v2, async) |
| ORM & DB | SQLAlchemy 2.0 Async + Alembic + PostgreSQL 16 |
| Mensageria | RabbitMQ 3.x + Celery (broker: RabbitMQ, backend: Redis) |
| Cache & Lock | Redis 7.x (Redlock pattern) |
| Observabilidade | Structlog (JSON) + OpenTelemetry + Prometheus + Grafana |
| Deploy | Docker + Kubernetes |
| CI/CD | GitHub Actions |
| Qualidade | Ruff (lint/format), MyPy (strict), Pytest |

## Estrutura do Projeto

```
ecotrace-engine/
├── app/
│   ├── api/v1/            # Endpoints FastAPI (ingest, status, health, metrics)
│   ├── application/       # Casos de uso, DTOs, interfaces (ports)
│   ├── core/              # Config, logging, telemetry
│   ├── domain/            # Value Objects, Aggregates, Domain Services
│   ├── infrastructure/    # SQLAlchemy, Redis, RabbitMQ, SEFAZ mock
│   └── workers/           # Celery app + audit tasks
├── deploy/k8s/            # Manifestos Kubernetes
├── docker/                # Dockerfile + docker-compose.yml + Prometheus
├── migrations/            # Alembic async migrations
├── tests/                 # Unit, integration (testcontainers), e2e
└── .github/workflows/     # CI/CD pipeline
```

## Início Rápido

### Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gerenciador de dependências)
- Docker (para PostgreSQL, Redis, RabbitMQ)

### Setup Local

```bash
# Instalar dependências
uv sync

# Subar infraestrutura local
docker compose -f docker/docker-compose.yml up -d

# Rodar migrações
uv run alembic upgrade head

# Iniciar API
uv run uvicorn app.main:app --reload --port 8000

# Iniciar worker
uv run celery -A app.workers.celery_app:celery_app worker -l info -Q ecotrace.invoices
```

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/nfe/ingest` | Ingestão de NF-e → 202 Accepted |
| `GET` | `/api/v1/nfe/status/{tracking_id}` | Consulta status por tracking_id |
| `GET` | `/metrics` | Métricas Prometheus |

### Exemplo de Uso

```bash
# Ingerir NF-e
curl -X POST http://localhost:8000/api/v1/nfe/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "access_key": "35240112345678000190550010000001230000000042",
    "issuer_cnpj": "11222333000181",
    "recipient_cnpj": "04252011000110",
    "items": [
      {
        "item_number": 1,
        "description": "Aparas de PET",
        "ncm": "39159000",
        "gross_weight": "1500.000"
      }
    ]
  }'

# Consultar status
curl http://localhost:8000/api/v1/nfe/status/{tracking_id}
```

## Deploy com Kubernetes

```bash
# Aplicar todos os manifests
kubectl apply -f deploy/k8s/

# Verificar pods
kubectl -n ecotrace get pods

# Logs
kubectl -n ecotrace logs -f deployment/ecotrace-api
kubectl -n ecotrace logs -f deployment/ecotrace-worker
```

## Desenvolvimento

### Rodar testes

```bash
# Unitários
uv run pytest tests/unit/ -q

# Integração (requer Docker)
uv run pytest tests/integration/ -q -m integration

# Todos
uv run pytest -q
```

### Qualidade

```bash
uv run ruff check .         # lint
uv run ruff format .        # format
uv run mypy app/            # type check
```

## Arquitetura de Domínio (DDD)

O projeto segue Clean Architecture com Domain-Driven Design:

- **Domain Layer** (`app/domain/`): Pure Python, zero dependências externas
- **Application Layer** (`app/application/`): Use cases, DTOs, interfaces (ports)
- **Infrastructure Layer** (`app/infrastructure/`): Adaptadores concretos (SQLAlchemy, Redis, RabbitMQ)
- **API Layer** (`app/api/`): FastAPI endpoints, orquestração HTTP
- **Workers Layer** (`app/workers/`): Celery tasks, pipeline assíncrono

## Licença

Propriedade — Eureciclo / EcoTrace Engine
