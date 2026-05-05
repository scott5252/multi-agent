# Quickstart: Model, Prompt, Profile, And Provider Governance

## Local Setup

```bash
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
uv run alembic upgrade head
```

Start the application:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Start the worker when validating provenance and gateway-adjacent summaries:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Entry

Open the local-principal login flow:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Use `platform-admin` to validate provider configuration, credential-reference diagnostics, and explicit probe actions.

Use `tenant-admin-acme` to validate tenant-scoped catalog, prompt, profile, routing, history, and provenance visibility.

Use `auditor` only for read/review paths when available.

## API Smoke Checks

Governance shell:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: platform-admin" \
  "http://127.0.0.1:8000/admin/app/governance"
```

Governance bootstrap:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: platform-admin" \
  "http://127.0.0.1:8000/admin/app/governance/bootstrap.json"
```

Tenant-scoped bootstrap:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/governance/bootstrap.json?tenant_id=11111111-1111-1111-1111-111111111111"
```

Explicit provider probe:

```bash
curl --fail --silent --show-error \
  -X POST \
  -H "X-Local-Principal: platform-admin" \
  "http://127.0.0.1:8000/admin/app/governance/providers/openai-primary/probe"
```

Tenant provider mutation denial:

```bash
test "$(curl --silent --output /tmp/qa031-tenant-provider-denied.json --write-out '%{http_code}' \
  -X POST \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/governance/providers/openai-primary/probe")" = "403"
```

Prompt preview:

```bash
curl --fail --silent --show-error \
  -X POST \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -d '{"fixture_id":"qa031-safe-preview"}' \
  "http://127.0.0.1:8000/admin/app/governance/prompts/daily-briefing/preview?tenant_id=11111111-1111-1111-1111-111111111111"
```

Denied route:

```bash
test "$(curl --silent --output /tmp/qa031-denied.json --write-out '%{http_code}' \
  "http://127.0.0.1:8000/admin/app/governance/bootstrap.json")" = "401"
```

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_governance_schema.py \
  tests/unit/admin/test_governance_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/governance/test_governance_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Full QA031 Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/031-model-prompt-profile-and-provider-governance
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml --start-processes
```

## Expected Evidence

- Governance route denies unauthenticated access.
- Platform admin can open governance setup and run an explicit mocked provider probe.
- Tenant admin can view only authorized catalog, prompt, profile, routing, history, and provenance data.
- Tenant admin cannot mutate provider configuration or credential references.
- Prompt preview blocks or summarizes unsafe prompt/completion text before rendering.
- Profile and routing previews are read-only and do not call live providers or tools.
- Policy history and run provenance show bounded safe evidence.
- No raw secrets, resolved credentials, provider tokens, authorization headers, raw prompts, raw completions, private messages, memory, connector payloads, provider payloads, local paths, stack traces, or unauthorized tenant labels appear.
