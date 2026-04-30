# Skill Registry Testing

Use this document for reviewer and developer evidence for Spec 014.

## Setup

```bash
uv sync
cp specs/014-skill-registry-lifecycle/.env.qa014 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa014 && createdb -U postgres multi_agent_platform_qa014'
uv run alembic upgrade head
```

## Targeted Tests

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_skill_manifest.py \
  tests/unit/admin/test_skill_package_validation.py \
  tests/unit/admin/test_skill_artifact_store.py \
  tests/unit/admin/test_skill_audit_redaction.py \
  tests/unit/admin/test_skill_readiness.py \
  tests/unit/admin/test_skill_eligibility.py \
  tests/unit/admin/test_skill_registry_jobs.py \
  tests/unit/admin/test_skill_registry_fairness.py \
  tests/unit/admin/test_skill_quarantine.py \
  tests/unit/admin/test_skill_registry_observability.py \
  tests/unit/admin/test_skill_runtime_eligibility.py \
  tests/unit/api/test_skill_registry_ui_models.py \
  tests/unit/api/test_skill_registry_schemas.py \
  tests/unit/auth/test_skill_policy.py \
  tests/integration/skill_registry/test_skill_smoke_runner.py \
  tests/integration/skill_registry/test_skill_installation_lifecycle.py \
  tests/integration/skill_registry/test_skill_workflow_publish_validation.py \
  tests/integration/skill_registry/test_skill_policy_integration.py
```

Expected: all tests pass. This proves the implemented slice validates
manifests, blocks unsafe entries, writes content-addressed artifacts, redacts
audit summaries, evaluates readiness, enforces eligibility, handles durable
job idempotency, and preserves tenant installation evidence.

## Quality Commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Record command output in `docs/skill-registry-pr-notes.md`.

## Manual Checks

- Platform package creation and version publication use platform-admin local
  principal permissions.
- Tenant installation requires a tenant grant.
- Missing credentials keep readiness blocked.
- Configured credential references move readiness to ready only when smoke
  tests and policy checks are satisfied.
- Quarantined versions and installations are denied for binding and runtime.
- Rendered pages display digests, summaries, findings, and redaction notices,
  never raw payloads or credential values.
