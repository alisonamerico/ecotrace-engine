# FASE 06 — Planejamento do Desenvolvimento

## 1. Mapa de Milestones

| Milestone | Escopo | Estimativa | Entregável Vital |
| :--- | :--- | :--- | :--- |
| **M1** | Tooling & Docker Base | 2h | `pyproject.toml` (`uv`), Linter (`ruff`), Typecheck (`mypy`), `docker-compose.yml` |
| **M2** | Core Domain & PostgreSQL | 4h | Agregados DDD, Mappers SQLAlchemy 2.0 e Migrações Alembic |
| **M3** | FastAPI Ingest & RabbitMQ | 4h | API com resposta 202 Accepted (<50ms) e Publisher AMQP |
| **M4** | Workers, Redis Lock & Fraud | 5h | Celery Workers com detecção de dupla contagem e Distributed Lock |
| **M5** | Observabilidade Total | 3h | Structured JSON Logs, Prometheus Metrics & OpenTelemetry Tracing |
| **M6** | K8s, CI/CD & Docs | 4h | Manifestos K8s, GitHub Actions e Documentação Técnica |

## 2. Próxima Etapa do Pipeline
Início da **FASE 7 — Implementação Prática (Milestone 1)** com a entrega dos arquivos de infraestrutura, dependências com `uv` e dockerização local dos serviços auxiliares.
