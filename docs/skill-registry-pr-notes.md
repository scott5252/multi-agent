# Skill Registry PR Notes

## Scope

Spec 014 adds an additive governed skill registry lifecycle. The submitted
slice includes manifest validation, content-addressed artifact storage,
redacted audit helpers, durable in-memory lifecycle job primitives, readiness
evaluation, smoke-test evidence summaries, binding eligibility, runtime
eligibility, quarantine decisions, SQLAlchemy models, Alembic migration,
repository methods, JSON schemas, API routes, admin UI view models, templates,
navigation, docs, and focused tests.

## Security And Tenant Isolation

- Raw secrets, tokens, credential values, raw payloads, unsafe docs, and
  cross-tenant data are redacted at lifecycle audit boundaries.
- Tenant availability grants gate installation.
- Readiness and binding eligibility carry tenant id, installation id,
  installation version, package slug/version, manifest digest, and artifact
  digest.
- Quarantine blocks readiness, new bindings, workflow publish validation, and
  runtime use without deleting immutable history.

## Test Evidence

- `uv run pytest --no-cov ...skill registry focused suite...`: 33 passed.
- `uv run ruff check ...skill registry focused paths...`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed.
- `uv run mypy src`: passed.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`:
  724 passed, total coverage 90.11%.

## Remaining Reviewer Commands

Run before merge:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual QA Evidence

Use `specs/014-skill-registry-lifecycle/qa014.md` and
`specs/014-skill-registry-lifecycle/qa014_ui.md` for the copy/paste and
browser reviewer pass.
