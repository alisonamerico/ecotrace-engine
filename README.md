# EcoTrace Engine

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.13-blue.svg?logo=python&logoColor=white" alt="Python 3.13">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.141-009688.svg?logo=fastapi&logoColor=white" alt="FastAPI 0.141">
  </a>
  <a href="https://docs.sqlalchemy.org/20/">
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0-CC0000.svg?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0">
  </a>
  <a href="https://docs.celeryq.dev/">
    <img src="https://img.shields.io/badge/Celery-5.6-59B245.svg?logo=celery&logoColor=white" alt="Celery 5.6">
  </a>
  <a href="https://docs.astral.sh/uv/">
    <img src="https://img.shields.io/badge/uv-0.10-261230.svg?logo=python&logoColor=white" alt="uv 0.10">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker_Compose-2496ED.svg?logo=docker&logoColor=white" alt="Docker Compose">
  </a>
  <a href="https://docs.ruff.sh/">
    <img src="https://img.shields.io/badge/Ruff-linter-FFD43B.svg?logo=ruff&logoColor=black" alt="Ruff">
  </a>
  <a href="https://mypy-lang.org/">
    <img src="https://img.shields.io/badge/MyPy-strict-2A6DB2.svg?logo=mypy&logoColor=white" alt="MyPy strict">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql&logoColor=white" alt="PostgreSQL 16">
  </a>
  <a href="https://redis.io/">
    <img src="https://img.shields.io/badge/Redis-7-DC382D.svg?logo=redis&logoColor=white" alt="Redis 7">
  </a>
  <a href="https://www.rabbitmq.com/">
    <img src="https://img.shields.io/badge/RabbitMQ-3-FF6600.svg?logo=rabbitmq&logoColor=white" alt="RabbitMQ 3">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  </a>
  <a href="https://github.com/alison/americo/ecotrace-engine/actions">
    <img src="https://img.shields.io/badge/tests-117%20passing-brightgreen.svg" alt="Tests">
  </a>
</p>

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

| Camada | Tecnologia | Documentação |
|---|---|---|
| Runtime | Python 3.13+ | [docs.python.org/3.13](https://docs.python.org/3.13/) |
| Framework API | FastAPI (Pydantic v2, async) | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| ORM & DB | SQLAlchemy 2.0 Async + Alembic + PostgreSQL 16 | [docs.sqlalchemy.org/20](https://docs.sqlalchemy.org/20/) |
| Mensageria | RabbitMQ 3.x + Celery (broker: RabbitMQ, backend: Redis) | [docs.celeryq.dev](https://docs.celeryq.dev/) |
| Cache & Lock | Redis 7.x (Redlock pattern) | [redis.io/docs](https://redis.io/docs/) |
| Observabilidade | Structlog (JSON) + OpenTelemetry + Prometheus + Grafana | [structlog.readthedocs.io](https://www.structlog.org/en/stable/) |
| Deploy | Docker + Kubernetes | [kubernetes.io/docs](https://kubernetes.io/docs/home/) |
| CI/CD | GitHub Actions | [docs.github.com/actions](https://docs.github.com/en/actions) |
| Qualidade | Ruff (lint/format), MyPy (strict), Pytest | [docs.ruff.sh](https://docs.ruff.sh/) |

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

## Documentação Técnica

| Documento | Descrição |
|---|---|
| [FASE_00_PRODUCT_DISCOVERY.md](docs/FASE_00_PRODUCT_DISCOVERY.md) | Descoberta do Produto |
| [FASE_01_PRD.md](docs/FASE_01_PRD.md) | Product Requirements Document (PRD) |
| [FASE_02_ARQUITETURA.md](docs/FASE_02_ARQUITETURA.md) | Arquitetura do Sistema |
| [FASE_03_MODELAGEM_DDD.md](docs/FASE_03_MODELAGEM_DDD.md) | Modelagem de Domínio (DDD) |
| [FASE_04_BANCO_DE_DADOS.md](docs/FASE_04_BANCO_DE_DADOS.md) | Schema do Banco de Dados |
| [FASE_05_ESTRUTURA_PROJETO.md](docs/FASE_05_ESTRUTURA_PROJETO.md) | Estrutura do Projeto |
| [FASE_06_PLANEJAMENTO_DESENVOLVIMENTO.md](docs/FASE_06_PLANEJAMENTO_DESENVOLVIMENTO.md) | Planejamento do Desenvolvimento |

## Licença

Propriedade — Eureciclo / EcoTrace Engine
