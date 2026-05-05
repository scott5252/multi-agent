# Quickstart: React Skill Registry And Tool Execution Lifecycle

## Scope

QA032 validates the additive React skill lifecycle workspace for package publication, tenant discovery and installation, credential reference configuration, smoke-test/readiness evidence, connector diagnostics, binding eligibility preview, quarantine/withdrawal state, and audit timeline review.

The primary route is `/admin/app/skills`.

Existing Jinja/admin routes remain available during migration:

- `/admin/skill-registry/ui/packages`
- `/admin/skill-registry/ui/installations`
- `/admin/skill-execution/ui/diagnostics`

## Local Environment

Use the generated QA environment once implementation creates it:

```bash
cp specs/032-react-skill-registry-and-tool-execution-lifecycle/.env.qa032 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa032 && createdb -U postgres multi_agent_platform_qa032'
uv run alembic upgrade head
```

Seed local tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa032 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Start the application:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

## Browser-First Validation

Open platform publication:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Sign in as `platform-admin`.

Expected results:

- The React shell renders `Skill lifecycle`.
- The platform publication wizard shows package candidate, manifest, validation, publish readiness, grants, quarantine, withdrawal, and audit sections.
- Manifest submission returns safe summary, digest, validation findings, and no raw manifest echo.
- Publish returns immutable version evidence and audit reference.
- Quarantine or withdrawal state is visible as safe lifecycle evidence.

Open tenant lifecycle:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Sign in as `tenant-admin-acme`.

Expected results:

- Discovery shows granted packages only.
- Installation actions return safe mutation feedback and revision tokens.
- Credential reference configuration uses authorized options only.
- Smoke-test/readiness refresh returns queued or ready evidence.
- Calendar, Gmail, news, weather, and commute connector diagnostics show safe readiness summaries.
- Binding eligibility preview is read-only and shows policy reasons.
- Audit timeline shows safe bounded records.

Cross-tenant check:

```text
http://127.0.0.1:8000/admin/app/skills?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: an Acme principal sees a safe cross-tenant denial without Globex package, installation, credential, smoke-test, diagnostic, or audit details.

## Automated Validation

Run QA docs:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/032-react-skill-registry-and-tool-execution-lifecycle
```

Run focused tests after implementation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_skill_lifecycle_schema.py \
  tests/unit/admin/test_skill_lifecycle_service.py \
  tests/performance/skills/test_skill_lifecycle_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Run frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Run full QA:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml --start-processes
```

## Redaction Expectations

Screenshots, JSON responses, logs, and QA artifacts must not contain:

- raw manifests
- raw credential values
- authorization headers
- provider tokens
- private messages
- memory contents
- connector request or response payloads
- raw tool outputs
- stack traces
- local filesystem paths
- unauthorized tenant labels
