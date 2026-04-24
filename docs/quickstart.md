# Platform Quickstart

## Prerequisites

- Python `3.12`
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2

## Local Setup

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Set `AUTH_MODE=local_principal` for local development.
4. Start PostgreSQL with `docker compose up -d postgres`.
5. Apply migrations with `uv run alembic upgrade head`.
6. Seed the local tenant rows before using `tenant-admin-acme`.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform <<'SQL'
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    'acme',
    'Acme',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'globex',
    'Globex',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  )
ON CONFLICT (slug) DO NOTHING;
SQL
```

### Local Principal Example

```bash
export AUTH_MODE=local_principal
export LOCAL_PRINCIPAL_HEADER=X-Local-Principal
export LOCAL_PRINCIPAL_CATALOG_JSON='{"tenant-admin-acme":{"catalog_key":"tenant-admin-acme","display_name":"Tenant Admin","tenant_id":"11111111-1111-1111-1111-111111111111","org_id":"org-acme","role_codes":["tenant_user","tenant_admin"],"permission_codes":["tenant:read","tenant:admin"]},"platform-admin":{"catalog_key":"platform-admin","display_name":"Platform Admin","role_codes":["platform_admin"],"permission_codes":["tenant:admin"]}}'
```

## Run The API And Worker

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

```bash
uv run python -m multi_agent_platform.workers.main
```

## Durable Runtime Quickstart

Start a published workflow run with a local-principal tenant context:

```bash
curl -sS -X POST http://127.0.0.1:8000/runtime/runs \
  -H "Content-Type: application/json" \
  -H "X-Local-Principal: tenant-admin-acme" \
  -d '{
    "published_workflow_version_id": "00000000-0000-0000-0000-000000000004",
    "idempotency_key": "demo-durable-run-001",
    "input": {"prompt": "Run the durable orchestration demo"}
  }'
```

Inspect runtime status and timeline evidence:

```bash
curl -sS http://127.0.0.1:8000/runtime/runs/{workflow_run_id} \
  -H "X-Local-Principal: tenant-admin-acme"

curl -sS http://127.0.0.1:8000/runtime/runs/{workflow_run_id}/timeline \
  -H "X-Local-Principal: tenant-admin-acme"
```

Use the worker command above to validate claim, resume, and lease behavior.
Approval, handoff, side-effect, and lineage endpoints are documented in the
feature quickstart and runbook.

## Workflow Studio Quickstart

1. Open [http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui).
2. Sign in as `platform-admin` to validate publish and sharing flows.
3. Create a draft through `POST /admin/workflows`.
4. Validate with `POST /admin/workflows/drafts/{workflow_draft_id}/validate`.
5. Publish with `POST /admin/workflows/drafts/{workflow_draft_id}/publish`.
6. Inspect the immutable version in `/admin/workflows/versions/{id}/detail`.
7. Create a sharing grant with
   `POST /admin/workflows/versions/{id}/sharing-grants`.

Detailed workflow-registry instructions:

- [Admin Workflow Studio](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-studio.md)
- [Spec 003 Quickstart](/Users/scottcornell/src/my-projects/multi-agent/specs/003-workflow-studio-registry/quickstart.md)
- [Spec 003 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/003-workflow-studio-registry/qa003.md)

## Validation

Run the full local quality workflow:

```bash
./scripts/check.sh
```

Target the workflow-registry feature explicitly:

```bash
uv run pytest \
  tests/unit/admin/test_admin_service.py \
  tests/unit/admin/test_validation.py \
  tests/unit/admin/test_workflow_registry_service.py \
  tests/unit/api/test_admin_workflow_routes.py \
  tests/unit/api/test_admin_workflow_ui_routes.py \
  tests/integration/admin/test_publish_compilation.py \
  tests/integration/api/test_admin_workflows_api.py \
  tests/integration/api/test_admin_workflow_ui.py \
  tests/contract/test_workflow_registry_contract.py
```

Target the durable orchestration runtime explicitly:

```bash
uv run pytest \
  tests/unit/runtime/orchestration \
  tests/unit/api/test_runtime_run_schemas.py \
  tests/unit/db/test_runtime_orchestration_models.py \
  tests/contract/test_runtime_orchestration_contract.py \
  tests/integration/runtime/test_langgraph_checkpoint_resume.py \
  tests/integration/runtime/test_orchestration_crash_resume.py \
  tests/integration/runtime/test_runtime_api_flows.py \
  tests/integration/runtime/test_runtime_repository.py \
  tests/integration/workers/test_orchestration_worker.py \
  tests/performance/runtime/test_runtime_latency.py
```

## Troubleshooting

- `401 missing local principal header or cookie`: sign in through
  `/auth/local-login` first.
- `insert or update on table "access_decision_records" violates foreign key constraint "fk_access_decision_records_tenant_id_tenants"`:
  seed the `acme` tenant row before using `tenant-admin-acme`.
- `409 validation result is stale or failed publish readiness`: save or validate
  again before publishing.
- `503 compiled bundle artifact persistence failed`: check
  `FILESYSTEM_STORAGE_ROOT` and retry.
- platform asset not visible to a tenant: confirm a sharing grant exists for
  that exact published version and tenant.
- browser UI route denied: confirm whether the current principal is
  `tenant-admin-acme` or `platform-admin`.

## Related Docs

- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Durable Orchestration Runtime](/Users/scottcornell/src/my-projects/multi-agent/docs/durable-orchestration-runtime.md)
