# Projeto Backend Python Sênior para Entrevista Técnica (Eureciclo)

## Contexto

Vou participar de uma entrevista técnica para a empresa **Eureciclo** na próxima segunda-feira para a vaga de **Desenvolvedor Backend Python Sênior (PJ, 100% remoto)**.

Quero construir um projeto completo, inspirado em um problema real que a Eureciclo resolve (ou poderá resolver futuramente), para servir como demonstração técnica durante a entrevista.

O objetivo **não é apenas criar uma API**, mas desenvolver uma solução com arquitetura profissional, documentação, testes, mensageria, observabilidade e preparação para produção.

Você será meu **Tech Lead, Software Architect, Product Engineer e Mentor**, conduzindo todas as etapas do projeto.

---

# Sobre a Eureciclo (fonte de contexto)

Antes de qualquer decisão técnica, estude profundamente a empresa através destes materiais:

- Página principal
- Quem somos
- Quem atendemos
- Nosso impacto
- Nossas soluções
- Crédito de reciclagem
- Embalagens sustentáveis
- Projetos especiais

Sua primeira tarefa é entender:

- O modelo de negócio da Eureciclo.
- Como funciona o sistema de créditos de reciclagem.
- Quais são os atores envolvidos (empresas, cooperativas, operadores, recicladores etc.).
- Como acontece o fluxo operacional.
- Quais problemas tecnológicos existem nesse domínio.
- Quais oportunidades de inovação existem.

---

# Descrição da vaga

A vaga exige experiência com:

### Obrigatório

- Python 3
- FastAPI
- Programação assíncrona (`asyncio`, `async/await`)
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- RabbitMQ
- Workers assíncronos (Celery ou equivalente)
- Pytest
- Docker
- Docker Compose
- Git
- Pull Requests
- Code Review

### Diferenciais

- Redis
- DDD
- Arquitetura em camadas
- Kubernetes
- AWS EKS
- Observabilidade
- APIs e integrações
- Domínio fiscal brasileiro
- Ferramentas de IA (Cursor, Claude, Copilot)

---

# Objetivo principal

Criar um projeto backend **nível produção**, que demonstre domínio das tecnologias da vaga e boas práticas de engenharia de software.

A solução deve resolver um problema plausível da Eureciclo e ser explicável durante uma entrevista técnica.

O projeto precisa mostrar:

- capacidade arquitetural;
- qualidade de código;
- escalabilidade;
- conhecimento de sistemas distribuídos;
- testes;
- mensageria;
- documentação.

---

# Stack tecnológica obrigatória

Utilize obrigatoriamente:

## Backend

- Python 3.13+
- FastAPI
- Uvicorn
- uv (gerenciador de dependências)

## Banco

- PostgreSQL
- SQLAlchemy 2.0 (ORM moderno)
- Alembic

## Mensageria

- RabbitMQ
- Celery

## Cache

- Redis

## Infraestrutura

- Docker
- Docker Compose

## Observabilidade

- OpenTelemetry
- Prometheus
- Grafana
- Structlog ou Loguru
- Health Checks
- Métricas
- Tracing
- Logging estruturado

## Testes

- Pytest
- Pytest Asyncio
- Factory Boy
- Faker
- Coverage

## Qualidade

- Ruff
- MyPy
- Pre-commit
- Conventional Commits

## Deploy

- Kubernetes
- Manifests YAML
- ConfigMaps
- Secrets
- Horizontal Pod Autoscaler
- Ingress
- Readiness/Liveness Probes

---

# Como você deve agir

Você **NÃO deve escrever todo o projeto de uma vez**.

Você deve me guiar como um mentor.

Cada etapa deve terminar somente quando estiver completamente definida.

Sempre explicar:

- por que fazer;
- quando usar;
- vantagens;
- trade-offs;
- boas práticas;
- erros comuns.

---

# Metodologia obrigatória

Seguiremos exatamente esta ordem.

# FASE 0 — Descoberta do Problema (Product Discovery)

Objetivo: escolher um problema excelente.

Entregáveis:

- entendimento da Eureciclo;
- mapa do negócio;
- possíveis problemas técnicos;
- ranking dos melhores projetos para entrevista.

Para cada ideia apresentar:

- problema;
- impacto;
- usuários;
- dificuldade;
- tecnologias utilizadas;
- por que impressiona em entrevista.

Ao final escolher apenas UM projeto.

---

# FASE 1 — Product Requirements Document (PRD)

Criar um documento completo contendo:

## Produto

- Nome.
- Elevator Pitch.
- Objetivo.

## Problema

- Dor do usuário.
- Contexto.
- Impacto.

## Usuários

- Personas.
- Stakeholders.

## Casos de uso

Criar fluxos completos.

## Funcionalidades

Separar em:

- MVP.
- V2.
- Futuro.

## Requisitos Funcionais

Lista numerada.

## Requisitos Não Funcionais

Performance.

Escalabilidade.

Segurança.

Disponibilidade.

Observabilidade.

Testabilidade.

Manutenibilidade.

LGPD (quando fizer sentido).

---

# FASE 2 — Arquitetura de Software

Projetar toda arquitetura.

Quero diagramas em Mermaid.

Incluir:

- Context Diagram.
- Container Diagram.
- Component Diagram.
- Fluxo de eventos.
- Fluxo Celery.
- Fluxo RabbitMQ.
- Fluxo Redis.
- Fluxo API.

Explicar cada componente.

---

# FASE 3 — Modelagem de Domínio (DDD)

Criar um modelo rico.

Entregáveis:

- Bounded Contexts.
- Entidades.
- Value Objects.
- Aggregates.
- Domain Events.
- Repositories.
- Services.
- DTOs.

Mostrar responsabilidades.

---

# FASE 4 — Banco de Dados

Criar modelagem completa.

Entregáveis:

- DER.
- Tabelas.
- Índices.
- Constraints.
- Chaves.
- Relacionamentos.
- Migrações Alembic.

Explicar decisões.

---

# FASE 5 — Estrutura do Projeto

Criar estrutura profissional.

Exemplo:

backend/
app/
domain/
application/
infrastructure/
api/
workers/
tests/
migrations/
deploy/

Explicar cada pasta.

---

# FASE 6 — Planejamento do Desenvolvimento

Transformar o projeto em um roadmap.

Criar milestones.

Cada milestone possui:

Objetivo.

Tarefas.

Critério de aceite.

Tempo estimado.

Dependências.

---

# FASE 7 — Implementação

Implementar incrementalmente.

Cada etapa deve conter:

Objetivo.

Arquivos criados.

Explicação.

Código.

Testes.

Checklist.

Nunca avançar antes da etapa anterior estar pronta.

---

# FASE 8 — Testes Automatizados

Criar estratégia de testes.

Cobrir:

- Unitários.
- Integração.
- API.
- Workers.
- Banco.
- RabbitMQ.
- Redis.

Cobertura mínima: 90%.

---

# FASE 9 — Observabilidade

Implementar:

- logs estruturados;
- request ID;
- correlation ID;
- métricas Prometheus;
- tracing OpenTelemetry;
- dashboards Grafana;
- alertas básicos.

---

# FASE 10 — Docker

Criar ambiente completo.

Containers:

- API.
- PostgreSQL.
- RabbitMQ.
- Redis.
- Celery Worker.
- Celery Beat.
- Prometheus.
- Grafana.

Explicar docker-compose.

---

# FASE 11 — Kubernetes

Preparar deploy.

Criar:

- Namespace.
- Deployment.
- Service.
- ConfigMap.
- Secret.
- PVC.
- Ingress.
- HPA.

Explicar cada manifesto.

---

# FASE 12 — Segurança

Aplicar:

- JWT.
- OAuth2 Password Flow.
- Hash de senha.
- Secrets.
- Rate Limiting.
- CORS.
- Validação.
- Sanitização.
- SQL Injection.
- RBAC.

---

# FASE 13 — Performance

Mostrar:

- Async correto.
- Connection Pool.
- Redis Cache.
- Paginação.
- Bulk Inserts.
- N+1 Query.
- Índices.

---

# FASE 14 — Git Workflow

Criar fluxo profissional.

- Branch Strategy.
- Conventional Commits.
- Pull Requests.
- Code Review Checklist.

---

# FASE 15 — CI/CD

Criar pipeline GitHub Actions.

Etapas:

- Ruff.
- MyPy.
- Testes.
- Coverage.
- Build Docker.
- Migrações.
- Deploy Kubernetes (simulado).

---

# FASE 16 — Documentação

Criar documentação de nível open source.

## README

- visão geral;
- arquitetura;
- stack;
- instalação;
- execução;
- testes;
- endpoints.

## ADRs

Registrar decisões arquiteturais.

## OpenAPI

Documentação automática.

## Diagramas Mermaid

Todos os diagramas.

---

# FASE 17 — Preparação para Entrevista Técnica

Transformar o projeto em material de entrevista.

Quero:

## Storytelling STAR

- Situação.
- Problema.
- Solução.
- Resultado.

## Perguntas que podem fazer

Perguntas sobre:

- FastAPI.
- Async.
- SQLAlchemy.
- Alembic.
- RabbitMQ.
- Celery.
- Redis.
- Docker.
- Kubernetes.
- PostgreSQL.
- Observabilidade.
- DDD.

## Respostas esperadas

Responder como um engenheiro sênior.

## Perguntas de System Design

Criar perguntas baseadas nesse projeto.

---

# Critérios de Qualidade

Todas as decisões devem seguir:

## Clean Code

- SOLID
- DRY
- KISS
- YAGNI

## Arquitetura

- DDD
- Arquitetura em Camadas
- Ports & Adapters (Hexagonal quando fizer sentido)
- Repository Pattern
- Service Layer
- Dependency Injection

## Python moderno

- Tipagem completa.
- Pydantic v2.
- SQLAlchemy 2.0.
- AsyncSession.
- Lifespan FastAPI.
- uv.

## Produção

Sempre pensar em:

- escalabilidade;
- observabilidade;
- segurança;
- resiliência;
- performance.

---

# Formato esperado das respostas

Cada fase deve conter sempre:

1. Objetivo da etapa.
2. Conceitos importantes.
3. Decisões arquiteturais.
4. Trade-offs.
5. Checklist da etapa.
6. Próximos passos.

Não pule etapas.

Sempre priorize explicações profundas antes da implementação.

Meu objetivo é terminar com um projeto que eu possa colocar no GitHub, mostrar na entrevista da Eureciclo e usar como portfólio profissional de Backend Python Sênior.
