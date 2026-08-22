# AGENTS.md — EcoTrace Engine (Ingestão & Antifraude)

## Project context

This project is the **EcoTrace Engine**, a distributed, asynchronous backend engine for ingestion, fiscal validation, SHA-256 anti-fraud auditing, and Recycling Credit generation for the Eureciclo ecosystem.

All technical documentation, architectural decisions, DDD models, database schemas, and engineering roadmaps are consolidated under the `docs/` folder:

```text
docs/
├── FASE_00_PRODUCT_DISCOVERY.md
├── FASE_01_PRD.md
├── FASE_02_ARQUITETURA.md
├── FASE_03_MODELAGEM_DDD.md
├── FASE_04_BANCO_DE_DADOS.md
├── FASE_05_ESTRUTURA_PROJETO.md
└── FASE_06_PLANEJAMENTO_DESENVOLVIMENTO.md
```

> MANDATORY ANTI-HALLUCINATION RULE:
> You MUST NOT invent external libraries, folder structures, database models,
> or API contracts that diverge from the specifications in docs/. 
> Always verify technical details against the reference files before writing code.

## Mandatory Technology Stack & Version Locks

### You MUST strictly use the following technology stack:

- Dependency Manager: uv (NEVER use pip, poetry, or pipenv)
- Runtime: Python 3.13+
- Web Framework: FastAPI (Pydantic v2, Async Lifespan)
- Database & ORM: PostgreSQL 16 + SQLAlchemy 2.0 (AsyncSession only) + Alembic (Async)
- Messaging & Async Workers: RabbitMQ 3.x + Celery
- Cache & Distributed Locks: Redis 7.x (Redlock pattern for idempotency)
- Observability: Structlog (JSON structured logging) + OpenTelemetry + Prometheus + Grafana
- Testing & Quality: Pytest (Pytest-Asyncio, Factory-Boy, Faker), Ruff (linter/formatter), MyPy (Strict Mode)

## Architectural Directives (Clean Architecture / DDD)

### Domain Layer (app/domain/):

- MUST be pure Python. NEVER import SQLAlchemy, FastAPI, Pydantic, Celery, or infrastructure modules inside app/domain/.
- Use standard Python dataclasses or native types.

### Application Layer (app/application/):

- Contains Use Cases and Application DTOs (Pydantic v2).
- Communicates with infrastructure only through Abstract Base Classes (Interfaces/Ports).

### Infrastructure Layer (app/infrastructure/):

- Houses SQLAlchemy ORM models, repository implementations, Redis/RabbitMQ connections, and external HTTP clients.
- Requires explicit Mappers to translate between DB models and Domain Entities.

## Session workflow

### Beans modeling rules (MANDATORY)

- Every Bean MUST be self-contained
- Each Bean must include:
    - What needs to be done
    - Why it needs to be done
    - Where to implement (files/modules)
    - How to approach it (architecture/constraints)
    - Beans must be written in English

- Use a hierarchical structure:
    - `Epic` → represents a feature or high-level goal (e.g., Milestones M1 to M6)
    - `Tasks` → implementation steps under an epic
    - Each Epic MUST have child tasks
    - `Bug` → issues/defects found during development or review

> Each Epic MUST have child tasks (and/or bugs when applicable)

- Dependencies must be explicitly defined:
    - Tasks can depend on other tasks
    - Execution order is driven by dependencies, not type

- Write Beans assuming:
> Another agent with zero context will execute it

______________________________________________________________________

## 1. Start of session

```bash
# Check whether `beans` is already initialized before running `beans init`
beans init  # initialize beans in the project (run once)
```

```bash
beans --json ready  # list available tasks
```

> `beans` — task management CLI: https://github.com/henriquebastos/beans/

> Use `beans --help` for more information about available commands

## 2. Before starting any task

```bash
beans claim <id> --actor opencode
```

## 3. Red-green-refactor (TDD — always write the test first)

```
RED    → write a failing test
GREEN  → make it pass with the minimal implementation
COMMIT → feat: <description>

REFACTOR → improve the code without changing behavior
COMMIT   → refactor: <description>
```

## 4. After completing a task

```bash
beans close <id> --reason "commit <hash>"
```

## 5. At 80% context — run handoff

Summarize what was done, what is pending, and the current state of the codebase so the next session can resume without losing context.

______________________________________________________________________

## Imports

**Imports always at the top of the file — never inside a function or class.**

______________________________________________________________________

## Commits

Each commit does **one thing**. Use conventional commit messages:

| Prefix | When to use |
|---|---|
| `feat:` | new functionality |
| `fix:` | bug fix |
| `refactor:` | code improvement, no behavior change |
| `chore:` | tooling, config, dependencies |
| `docs:` | documentation only |
| `ci:` | CI/CD changes |

When a commit resolves a bean, append `#closes <bean-id>` to the message:

```bash
git commit -m "feat: add --body flag to create command #closes bean-69b4e720"
```

______________________________________________________________________

## Before every commit

**Step 1 — tests and lint**

```bash
uv run pytest
uv run ruff check tests/
```

**Step 2 — review uncommitted changes**

Run `git diff HEAD` and review the output in 5 focused passes:

It runs a 5-pass review of uncommitted changes covering: security, correctness, design, testing, and conventions.

1. **Security** — secrets exposure, unsafe inputs, injection risks, auth issues
1. **Correctness** — logic errors, wrong assumptions, edge cases, off-by-one
1. **Design** — coupling, cohesion, SRP violations, unnecessary abstractions
1. **Testing** — missing coverage, brittle assertions, untested edge cases
1. **Conventions** — naming, import order, code style, project-specific patterns

For each pass, list issues found. Fix any issues → re-run tests → then commit.
