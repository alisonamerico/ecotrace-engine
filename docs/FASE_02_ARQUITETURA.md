# FASE 02 — Arquitetura de Software

## 1. Visão Geral da Arquitetura
A arquitetura adota os princípios de **Clean Architecture**, **DDD** e **Event-Driven Architecture (EDA)**.

## 2. Diagramas de Container e Componentes

### Diagrama de Containers (C4 Level 2)
```mermaid
C4Container
    title Diagrama de Containers - EcoTrace Engine

    Person(client, "Cliente / API Consumer", "Cooperativa ou Sistema Integrado")

    System_Boundary(b1, "EcoTrace Boundary") {
        Container(api, "FastAPI Web Application", "Python 3.13, Uvicorn", "Recebe requisições, valida schema, emite tracking_id, publica eventos no broker")
        ContainerDb(redis, "Cache & Lock", "Redis 7.x", "Locks distribuídos (Redlock) e controle de Idempotência")
        Container(broker, "Message Broker", "RabbitMQ 3.x", "Gerencia filas de ingestão e Dead Letter Exchanges (DLX)")
        Container(worker, "Celery Async Workers", "Python 3.13, Celery", "Consome tarefas, valida SEFAZ, checa fraude e gera créditos")
        ContainerDb(postgres, "Database", "PostgreSQL 16", "Armazena NF-es, histórico e Créditos de Reciclagem")
    }

    Rel(client, api, "Requisições HTTP", "HTTPS / JSON")
    Rel(api, redis, "Valida Rate-limit / Tracking", "RESP / TCP")
    Rel(api, broker, "Publica evento 'nfe.received'", "AMQP")
    Rel(worker, broker, "Consome tarefas", "AMQP")
    Rel(worker, redis, "Adquire Lock Distribuído", "RESP / TCP")
    Rel(worker, postgres, "Escrita relacional e atualização", "SQLAlchemy Async")