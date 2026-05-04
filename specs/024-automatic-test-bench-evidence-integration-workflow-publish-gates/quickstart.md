# Quickstart: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Goal

Verify that workflow validation and publish gates use current repository-backed agent test evidence instead of manual `latest_result_status` document fields.

## Local Setup

```bash
uv sync
cp specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/.env.qa024 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa024 && createdb -U postgres multi_agent_platform_qa024'
uv run alembic upgrade head
```

Expected: dependencies are installed, PostgreSQL is running, and the QA024 database has the latest schema.

## Start The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui
```

Choose `tenant-admin-acme` for tenant-scoped workflow and test-bench checks.

## Manual Flow

1. Create a tenant workflow draft from the Workflow Registry UI.
2. Create an Agent Test Suite for the same tenant and set its target to the workflow draft.
3. Add at least one deterministic test case.
4. Save the workflow draft with a required test declaration for that suite.
5. Run the suite against the current workflow draft revision ID.
6. Validate the workflow draft.
7. Open the publish gate.
8. Confirm the required-test summary is ready and publish is enabled.

Expected: the gate is ready only after the same-tenant run passes for the current revision.

## Negative Checks

- Change the draft after a passing run and rerun validation.
- Reference a suite from another tenant.
- Run the suite against an older target version.
- Set `latest_result_status` to `passed` in the workflow document without running the suite.

Expected: validation and publish gates block with safe required-test diagnostics.

## Focused Automated Tests

```bash
uv run pytest tests/unit/admin/test_publish_gate.py tests/unit/admin/test_workflow_builder_references.py tests/unit/admin/test_workflow_registry_service.py tests/integration/api/test_admin_workflow_ui.py
```

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
