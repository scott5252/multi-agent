# Quickstart: Runtime Agent Communication Graph For Runs

## Goal

Validate that a reviewer can inspect a real workflow run communication graph from safe durable runtime evidence.

## Setup

```bash
uv sync
docker compose up -d postgres
cp specs/067-runtime-agent-communication-graph-for-runs/.env.qa067 .env
uv run alembic upgrade head
uv run python scripts/qa/seed_runtime_agent_graph_qa067.py
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open the local Admin UI and sign in as `tenant-admin-acme`:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations?run_id=77777777-6767-4767-8767-000000000067
```

## API Smoke

```bash
export BASE_URL=http://127.0.0.1:8000
export ACME_HEADER='X-Local-Principal: tenant-admin-acme'
export GLOBEX_HEADER='X-Local-Principal: tenant-admin-globex'
export ACME_TENANT_ID=11111111-1111-1111-1111-111111111111
export QA067_RUN_ID=77777777-6767-4767-8767-000000000067

curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/runs/$QA067_RUN_ID/agent-graph?tenant_id=$ACME_TENANT_ID" \
  | jq '{source, state, partial, nodes: (.nodes | length), edges: (.edges | length)}'

curl -sS -i -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/runs/$QA067_RUN_ID/agent-graph?tenant_id=$ACME_TENANT_ID"
```

## Expected Reviewer Evidence

- Runtime graph source is `runtime_run`.
- The graph shows completed, failed or retrying, paused or waiting, and skipped or unavailable status examples from seeded evidence.
- Selecting a node or edge shows safe evidence references only.
- Cross-tenant access returns a denied response without topology details.
- Desktop and mobile screenshots show the canvas plus accessible node and edge lists.

## Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/067-runtime-agent-communication-graph-for-runs
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/067-runtime-agent-communication-graph-for-runs/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/067-runtime-agent-communication-graph-for-runs/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa067-after-spec
```
