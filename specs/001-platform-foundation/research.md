# Research: Platform Foundation

## Decision 1: Use FastAPI lifespan plus router-level dependency injection

- **Decision**: Use FastAPI's `lifespan` hook for API startup and shutdown,
  organize HTTP routes with `APIRouter`, and expose request-scoped providers
  through FastAPI dependencies.
- **Rationale**: FastAPI recommends `lifespan` for startup/shutdown resource
  management, which maps directly to shared resources like database engines,
  secret providers, and storage adapters. Router-level dependencies also keep
  operational routes thin and testable.
- **Alternatives considered**:
  - `@app.on_event("startup")` and `@app.on_event("shutdown")`: rejected
    because FastAPI treats `lifespan` as the preferred path and it gives a
    cleaner single context boundary.
  - Inline resource construction inside handlers: rejected because it breaks
    shared lifecycle control and makes readiness, cleanup, and tests harder.
- **Sources**:
  - [FastAPI lifespan events](https://fastapi.tiangolo.com/advanced/events/)
  - [FastAPI bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

## Decision 2: Use SQLAlchemy 2.x async ORM with psycopg 3

- **Decision**: Use `create_async_engine()` with the `postgresql+psycopg://`
  dialect, pair it with `async_sessionmaker`, and keep one `AsyncSession` per
  request or worker task.
- **Rationale**: SQLAlchemy 2.x documents `async_sessionmaker` as the reusable
  factory for async sessions, and it explicitly warns that an `AsyncSession`
  must not be shared across concurrent tasks. Psycopg 3 gives one dialect name
  for both sync and async engine creation, which keeps migrations and runtime
  configuration aligned.
- **Alternatives considered**:
  - Synchronous SQLAlchemy sessions in the API: rejected because API and worker
    code will spend significant time in I/O-bound paths and the async runtime is
    a better fit for later LangGraph orchestration.
  - `asyncpg` as the application driver: rejected for the foundation because
    `psycopg` provides a unified sync/async dialect path that simplifies Alembic
    and runtime configuration.
- **Sources**:
  - [SQLAlchemy asyncio support](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
  - [SQLAlchemy session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
  - [SQLAlchemy PostgreSQL psycopg dialect](https://docs.sqlalchemy.org/20/dialects/postgresql.html)

## Decision 3: Use Alembic with the async template, but constrain rollback promises

- **Decision**: Bootstrap Alembic with an async-capable environment so it can
  operate alongside the async SQLAlchemy stack, while explicitly validating
  rollback only in local and test workflows and documenting shared/production
  recovery as operator-controlled.
- **Rationale**: Alembic documents async-capable migration environments even
  though it does not expose a separate async API. This supports the async stack
  without forcing unsafe universal rollback promises in shared or production
  environments.
- **Alternatives considered**:
  - Upgrade-only migrations: rejected because the spec explicitly requires
    rollback validation in local/test.
  - Automatic rollback guarantees in every environment: rejected because shared
    and production recovery often requires forward-fix or restore procedures.
- **Sources**:
  - [Alembic cookbook: async migrations](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

## Decision 4: Keep the repository as a single Python project managed with uv

- **Decision**: Use one root `pyproject.toml` and `uv.lock`, with a single
  `src/multi_agent_platform/` package and thin entrypoint modules for API and
  worker startup.
- **Rationale**: The foundation needs clear module separation, but not
  multi-package release management yet. `uv` provides reproducible locking,
  exact sync, and fast task execution without adding a second layer of build
  tooling.
- **Alternatives considered**:
  - Multiple Python packages or a workspace layout now: rejected because the
    platform does not yet have independently releasable services.
  - Raw `venv` plus `pip`: rejected because it weakens lockfile guarantees and
    makes developer/CI parity harder.
- **Sources**:
  - [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
  - [uv project layout](https://docs.astral.sh/uv/concepts/projects/layout/)

## Decision 5: Use Docker Compose for infrastructure dependencies, not as the only dev runtime

- **Decision**: Use a root `compose.yaml` to start core infrastructure
  dependencies like PostgreSQL by default, with optional profiles for local
  S3-compatible storage and observability helpers. Run API and worker processes
  on the host during day-to-day development via `uv run`.
- **Rationale**: This keeps reload/debug loops fast while still giving every
  contributor a reproducible infrastructure baseline. Docker Compose profiles
  also let optional services stay out of the default local path.
- **Alternatives considered**:
  - Running every local process in Compose all the time: rejected because it
    slows the feedback loop for a code-heavy foundation spec.
  - No Compose support: rejected because the spec explicitly requires local
    Docker Compose support.
- **Sources**:
  - [Docker Compose profiles reference](https://docs.docker.com/reference/compose-file/profiles/)
  - [docker compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/)
  - [Docker Compose install guidance](https://docs.docker.com/compose/install/)

## Decision 6: Use pytest fixtures and FastAPI dependency overrides for the test harness

- **Decision**: Build the test harness around pytest fixtures, FastAPI
  `app.dependency_overrides`, and async-friendly HTTP/database test helpers.
- **Rationale**: FastAPI explicitly supports overriding dependencies during
  tests, which makes it a clean fit for secret providers, tenant context, and
  storage adapters. pytest fixtures provide scoped lifecycle control for database
  setup, test apps, and stand-in providers.
- **Alternatives considered**:
  - End-to-end only tests through live dependencies: rejected because the
    foundation needs fast, targeted feedback and strong unit coverage.
  - Hand-rolled test setup without fixture scopes: rejected because it becomes
    brittle once the project has multiple providers and entrypoints.
- **Sources**:
  - [FastAPI dependency overrides in tests](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
  - [pytest fixtures documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)

## Decision 7: Use a PostgreSQL-backed queue and lease abstraction as the worker spine

- **Decision**: Define queue, lease, and outbox abstractions in `runtime/` and
  back the first implementation with PostgreSQL tables and leasing semantics.
- **Rationale**: The repository architecture already centers PostgreSQL as the
  durable source of truth, and foundation scope needs a reliable worker shell
  more than a separate queue product. This also keeps audit, idempotency, and
  migration control in one transaction boundary.
- **Alternatives considered**:
  - Redis/Celery in the foundation: rejected because it adds another operational
    dependency before queue semantics are fully proven.
  - In-memory background tasks only: rejected because they are not durable and
    break the platform’s crash-survival goals.
- **Sources**:
  - [Repo architecture guidance](../../docs/architecture.md)
  - [Transactional outbox example](../../docs/example/transactional_outbox.py)

## Decision 8: Reserve LangGraph durable execution boundaries now

- **Decision**: Even though this feature does not implement workflow execution,
  it will reserve runtime module boundaries and correlation fields for
  checkpointers, run IDs, parent-child lineage, and future execution bundles.
- **Rationale**: LangGraph durable execution depends on persistence,
  deterministic replay, thread identifiers, and idempotent side effects. The
  foundation must leave space for those capabilities instead of treating them as
  later bolt-ons.
- **Alternatives considered**:
  - Deferring all runtime boundaries until workflow implementation: rejected
    because it would force later restructuring across API, worker, audit, and
    persistence modules.
- **Sources**:
  - [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
  - [Repo architecture guidance](../../docs/architecture.md)

## Decision 9: Standardize quality gates on Ruff, mypy, pytest-cov, and CI enforcement

- **Decision**: Use Ruff for linting and formatting, mypy for type checking,
  pytest plus pytest-cov for testing and coverage enforcement, and a GitHub
  Actions workflow that blocks merge readiness when any required gate fails.
- **Rationale**: The foundation spec needs fast local feedback and strict CI
  parity. Ruff is fast enough to run continuously, mypy enforces contract and
  provider typing, and coverage enforcement is a constitutional requirement.
- **Alternatives considered**:
  - Separate linter and formatter stack with slower tools: rejected because the
    foundation benefits from fewer moving parts and faster developer feedback.
  - Manual coverage review without enforcement: rejected because the
    constitution requires an explicit threshold.
- **Sources**:
  - [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
  - [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
  - [mypy docs](https://mypy.readthedocs.io/)
