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

## User Interaction Channels Quickstart

Start a run through the shared Web API channel:

```bash
curl -sS -X POST http://127.0.0.1:8000/runs \
  -H "Content-Type: application/json" \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "X-Idempotency-Key: quickstart-channel-001" \
  -d '{
    "workflow_id": "published-demo-workflow",
    "inputs": {"topic": "quickstart"},
    "channel": "web_api"
  }'
```

Use the returned `run_id` with `/runs/{run_id}/status`,
`/runs/{run_id}/timeline`, `/runs/{run_id}/result`, approval/cancel endpoints,
and artifact URL grant endpoints. Open `/runs` for the Web UI channel. For
Telegram, create a link token with `POST /channels/telegram/link-token`, send
`/link TOKEN` to `/channels/telegram/webhook/{secret}`, then use protected
commands such as `/run`, `/status`, `/result`, and `/artifacts`.

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

Target workflow graph execution explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/runtime/orchestration/test_graph_execution.py \
  tests/unit/runtime/orchestration/test_graph_roles.py \
  tests/unit/runtime/orchestration/test_graph_redaction.py \
  tests/contract/test_workflow_graph_execution_contract.py \
  tests/docs/test_workflow_graph_execution_docs.py \
  tests/integration/runtime/test_workflow_graph_execution.py \
  tests/integration/workers/test_orchestration_worker.py \
  tests/performance/runtime/test_workflow_graph_execution_performance.py
```

Manual workflow graph execution QA:

- [Spec 020 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md)
- [Spec 020 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_ui.md)
- [Spec 020 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_user_guide.md)
- [Spec 020 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/testing-instructions.md)

Target skill tool execution explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/skill_execution \
  tests/unit/runtime/test_runtime_skill_tools.py \
  tests/contract/test_skill_execution_gateway_contract.py \
  tests/integration/api/test_admin_skill_execution_ui.py
```

Manual skill tool execution QA:

- [Spec 021 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/021-real-skill-tool-execution-connectors/qa021.md)
- [Spec 021 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/021-real-skill-tool-execution-connectors/qa021_ui.md)
- [Spec 021 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/021-real-skill-tool-execution-connectors/qa021_user_guide.md)
- Admin diagnostics route: `/admin/skill-execution/ui/diagnostics`

Target immutable memory explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/memory \
  tests/unit/db/test_memory_models.py \
  tests/contract/test_memory_contract.py \
  tests/integration/db/test_memory_migration.py \
  tests/integration/runtime/test_runtime_memory_flows.py \
  tests/integration/api/test_memory_api.py \
  tests/performance/memory/test_memory_latency.py
```

Manual immutable-memory QA:

- [Spec 005 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005.md)
- [Spec 005 Postman Collection](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005_collection.json)
- [Immutable Memory Operations](/Users/scottcornell/src/my-projects/multi-agent/docs/immutable-memory.md)

Target user interaction channels explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/channels \
  tests/unit/api/test_channel_run_schemas.py \
  tests/unit/db/test_channel_models.py \
  tests/contract/test_channel_layer_contract.py \
  tests/integration/api/test_channel_run_api.py \
  tests/integration/api/test_web_run_ui.py \
  tests/integration/api/test_telegram_webhook.py \
  tests/integration/channels \
  tests/performance/channels/test_channel_latency.py
```

Manual channel QA:

- [Spec 006 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/006-user-interaction-channels/qa006.md)
- [User Interaction Channels](/Users/scottcornell/src/my-projects/multi-agent/docs/user-interaction-channels.md)

Target model-skill routing explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/model_skill_config \
  tests/unit/db/test_model_skill_config_models.py \
  tests/contract/test_model_skill_config_contract.py \
  tests/docs/test_model_skill_routing_docs.py
```

Manual model-skill QA:

- Set a tenant default model, add workflow, agent, and step overrides, then
  verify model precedence through `/admin/config/preview/model`.
- Add prompt references and confirm prompt precedence is step, agent, workflow
  with no tenant-global fallback.
- Bind a skill, allow a tool, add outbound policy, then verify an unapproved
  domain denies before side effects.
- Configure credential requirements using secret-reference metadata only.
- Review history, rollback, run provenance, resume stability, elapsed time,
  assisted status, and aggregate pass/fail evidence.
- [Model Skill Routing](/Users/scottcornell/src/my-projects/multi-agent/docs/model-skill-routing.md)

## Prompt Runtime Profiles Quickstart

Open the shared admin shell:

- [Prompt Library](http://127.0.0.1:8000/admin/prompt-runtime/prompts)
- [Agent Profiles](http://127.0.0.1:8000/admin/prompt-runtime/profiles)
- [Profile Resolution](http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve)

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/prompts \
  tests/unit/agents \
  tests/contract/test_prompt_runtime_profiles_contract.py \
  tests/integration/api/test_prompt_runtime_admin_navigation.py
```

Manual QA:

- [Prompt Runtime Profiles](/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md)
- [Spec 012 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/qa012.md)

## Agent And Workflow Test Bench Quickstart

Use the QA015 environment when validating the admin test bench:

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/015-agent-workflow-test-bench/.env.qa015 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa015 && createdb -U postgres multi_agent_platform_qa015'
uv run alembic upgrade head
```

Seed Acme and Globex tenants with the SQL block in
`specs/015-agent-workflow-test-bench/qa015.md`, then start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open the browser UI:

- [Agent Tests](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=11111111-1111-1111-1111-111111111111)

Manual QA:

- Create `QA015 Draft Workflow Guard` for target `qa015-draft-triage` and
  target version `draft-rev-1`.
- Add a case with a fixture containing `qa015-fake-value` and confirm the raw
  value is not rendered.
- Run once with `mock_model` and once with
  `real_model_side_effects_disabled`.
- Confirm result diagnostics include pass/fail status, trace steps, provider
  metadata, token usage, latency, contract validation, assertion outcomes,
  blocked side effects, redaction summary, and artifact summary.
- Confirm `approved_real_probe` rejects without approval metadata.
- Confirm the publish gate is ready for `draft-rev-1` and blocked for a stale
  target version.
- Sign in as `tenant-admin-globex` and confirm Acme suite and run details are
  denied.

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/testing/agent_bench \
  tests/unit/db/test_agent_tests_models.py \
  tests/unit/db/test_agent_tests_repository.py \
  tests/unit/api/test_agent_test_schemas.py \
  tests/unit/auth/test_agent_test_policy.py \
  tests/unit/admin/test_publish_gate.py \
  tests/contract/test_agent_test_bench_contract.py \
  tests/integration/runtime/test_agent_workflow_test_bench_gateway.py \
  tests/integration/api/test_admin_agent_tests_api.py \
  tests/docs/test_agent_test_bench_docs.py
```

Additional evidence:

- [Spec 015 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/015-agent-workflow-test-bench/qa015.md)
- [Spec 015 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/015-agent-workflow-test-bench/qa015_ui.md)
- [Spec 015 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/015-agent-workflow-test-bench/qa015_user_guide.md)
- [Spec 015 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/015-agent-workflow-test-bench/testing-instructions.md)

## Token Usage And Cost Analytics Quickstart

Use the QA016 environment when validating usage analytics:

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/016-token-usage-cost-analytics/.env.qa016 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa016 && createdb -U postgres multi_agent_platform_qa016'
uv run alembic upgrade head
```

Open the browser UI:

- [Usage Analytics](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/usage)

Manual QA:

- Sign in as `platform-admin` and confirm `/admin/usage` renders summary
  cards, filters, rollups, event drilldown rows or a safe empty state, and CSV
  export controls.
- Sign in as `tenant-admin-acme` and confirm Acme tenant scope is accepted.
- Sign in as `tenant-admin-globex` and confirm Acme tenant usage is denied.
- Confirm exports include safe normalized usage columns only.
- Confirm raw prompts, completions, secrets, memory content, provider
  credentials, and unauthorized run content are excluded.

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/model_providers/test_usage.py \
  tests/unit/usage \
  tests/unit/db/test_usage_models.py \
  tests/unit/db/test_usage_repository.py \
  tests/unit/auth/test_usage_policy.py \
  tests/unit/api/test_usage_schemas.py \
  tests/unit/api/test_usage_ui_models.py \
  tests/contract/test_usage_analytics_contract.py \
  tests/integration/db/test_usage_migration.py \
  tests/integration/model_providers/test_gateway_usage_capture.py \
  tests/integration/api/test_admin_usage_api.py \
  tests/integration/api/test_admin_usage_ui.py \
  tests/docs/test_usage_analytics_docs.py
```

Additional evidence:

- [Spec 016 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/016-token-usage-cost-analytics/qa016.md)
- [Spec 016 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/016-token-usage-cost-analytics/qa016_ui.md)
- [Spec 016 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/016-token-usage-cost-analytics/qa016_user_guide.md)
- [Spec 016 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/016-token-usage-cost-analytics/testing-instructions.md)

## Telegram Configuration Console Quickstart

Use the QA017 environment when validating Telegram configuration:

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/017-telegram-configuration-console/.env.qa017 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa017 && createdb -U postgres multi_agent_platform_qa017'
uv run alembic upgrade head
```

Open the browser UI:

- [Telegram Configuration](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram)

Manual QA:

- Sign in as `platform-admin` and confirm `/admin/telegram` renders provider
  readiness, safe secret-reference labels, tenant controls, link-token
  controls, masked identities, and diagnostics.
- Sign in as `tenant-admin-acme` and confirm Acme tenant scope is accepted.
- Sign in as `tenant-admin-globex` and confirm Acme Telegram configuration is
  denied.
- Confirm webhook validation records a local-only diagnostic and does not call
  Telegram.
- Confirm bot tokens, webhook secrets, private Telegram messages, raw prompts,
  run results, and unauthorized tenant data are excluded.

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/admin/telegram_config \
  tests/unit/api/test_telegram_config_schemas.py \
  tests/unit/auth/test_telegram_config_policy.py \
  tests/unit/db/test_telegram_config_repository.py \
  tests/contract/test_telegram_configuration_contract.py \
  tests/integration/db/test_telegram_config_migration.py \
  tests/integration/api/test_admin_telegram_api.py \
  tests/integration/api/test_admin_telegram_ui.py \
  tests/docs/test_telegram_configuration_docs.py
```

Additional evidence:

- [Spec 017 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/017-telegram-configuration-console/qa017.md)
- [Spec 017 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/017-telegram-configuration-console/qa017_ui.md)
- [Spec 017 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/017-telegram-configuration-console/qa017_user_guide.md)
- [Spec 017 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/017-telegram-configuration-console/testing-instructions.md)

## Membership Administration Quickstart

Use the QA018 environment when validating user and tenant membership
administration:

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/018-user-tenant-membership-administration/.env.qa018 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa018 && createdb -U postgres multi_agent_platform_qa018'
uv run alembic upgrade head
```

Open the browser UI:

- [Membership Administration](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships)

Manual QA:

- Sign in as `platform-admin` and confirm `/admin/memberships` renders the
  platform-scope summary, invitation form, principals, role grants, tenant
  memberships, invitations, access history, and membership audit sections.
- Create and replay an Acme invitation and confirm the rendered row uses
  masked email plus hash evidence.
- Link or inspect an Auth0-backed principal identity and confirm passwords are
  never requested or stored.
- Create and revoke tenant role grants, then confirm tenant membership and
  audit rows update safely.
- Sign in as `tenant-admin-acme` and confirm Acme self-service works for
  `tenant_user` and `tenant_admin` roles.
- Confirm Acme tenant admins cannot assign `platform_admin` and cannot inspect
  Globex membership data.
- Confirm access history and membership audit rows show safe action, decision,
  reason, summary, and trace evidence only.

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/admin/memberships \
  tests/unit/api/test_membership_schemas.py \
  tests/unit/api/test_membership_ui_models.py \
  tests/unit/auth/test_membership_policy.py \
  tests/unit/db/test_membership_repository.py \
  tests/integration/api/test_admin_memberships_api.py \
  tests/integration/api/test_admin_memberships_ui.py \
  tests/contract/test_membership_administration_contract.py \
  tests/docs/test_membership_administration_docs.py \
  tests/integration/db/test_membership_administration_migration.py \
  tests/unit/auth/test_service.py
```

Additional evidence:

- [Spec 018 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/018-user-tenant-membership-administration/qa018.md)
- [Spec 018 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/018-user-tenant-membership-administration/qa018_ui.md)
- [Spec 018 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/018-user-tenant-membership-administration/qa018_user_guide.md)
- [Spec 018 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/018-user-tenant-membership-administration/testing-instructions.md)

## Operations Console Quickstart

Use the QA019 environment when validating the Operations Console:

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/019-operations-console-logs-performance/.env.qa019 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa019 && createdb -U postgres multi_agent_platform_qa019'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa019 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Open the browser UI:

- [Operations Console](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/operations)

Manual QA:

- Sign in as `platform-admin` and confirm `/admin/operations` renders health,
  dependency readiness, capacity, provider and channel status, reliability
  pressure, latency, throughput, token usage, error rate, operational logs, and
  CSV export controls.
- Sign in as `auditor` and confirm redacted operational logs and dashboard
  data are available with explicit operations permissions.
- Sign in as `tenant-admin-acme` and confirm `/admin/operations` and
  `/admin/operations/api` are denied in v1.
- Confirm filters cover trace id, tenant id, run id, component, severity,
  status, dependency, and time range.
- Confirm UI, JSON APIs, CSV export artifacts, screenshots, and audit-safe
  summaries exclude raw prompts, model responses, channel messages, secrets,
  credentials, memory content, raw payloads, stack traces, and unauthorized
  tenant data.

Focused reviewer command:

```bash
uv run pytest --no-cov \
  tests/unit/operations \
  tests/unit/api/test_operations_schemas.py \
  tests/unit/api/test_operations_ui_models.py \
  tests/unit/auth/test_operations_policy.py \
  tests/contract/test_operations_console_contract.py \
  tests/integration/api/test_admin_operations_api.py \
  tests/integration/api/test_admin_operations_ui.py \
  tests/performance/operations/test_log_filtering.py \
  tests/docs/test_operations_console_docs.py
```

Additional evidence:

- [Spec 019 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/019-operations-console-logs-performance/qa019.md)
- [Spec 019 UI Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/019-operations-console-logs-performance/qa019_ui.md)
- [Spec 019 User Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/019-operations-console-logs-performance/qa019_user_guide.md)
- [Spec 019 Testing Instructions](/Users/scottcornell/src/my-projects/multi-agent/specs/019-operations-console-logs-performance/testing-instructions.md)

Target production audit debugging explicitly:

```bash
uv run pytest --no-cov \
  tests/unit/audit \
  tests/unit/api/test_audit_debugging_schemas.py \
  tests/contract/test_production_audit_debugging_contract.py \
  tests/integration/api/test_admin_run_inspection_api.py
```

Manual production audit debugging QA:

- Run `uv run alembic upgrade head`.
- Create successful and failed workflow runs with trace ids.
- Inspect timelines with
  `/admin/runs/{workflow_run_id}/timeline?tenant_id={tenant_id}`.
- Search failed runs with
  `/admin/runs/debug-search?tenant_id={tenant_id}&status=failed`.
- Review replay, lineage, and bundle responses for linked trace ids and safe
  metadata.
- Create a redacted debug-evidence export through
  `POST /admin/runs/{workflow_run_id}/exports`.
- Confirm denied inspection attempts are audit logged and no timelines, traces,
  exports, logs, metrics, README guidance, or PR notes contain raw secrets,
  credential values, unauthorized prompt text, or unauthorized memory content.
- [Production Audit Debugging](/Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md)

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
- [Immutable Memory](/Users/scottcornell/src/my-projects/multi-agent/docs/immutable-memory.md)
