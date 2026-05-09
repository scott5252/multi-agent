# Quickstart: Agent Communication Graph Contracts And Projections

## Setup

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Use local-principal auth in another terminal:

```bash
export BASE_URL="http://127.0.0.1:8000"
export ACME_HEADER="X-Local-Principal: tenant-admin-acme"
export PLATFORM_HEADER="X-Local-Principal: platform-admin"
export JSON_HEADER="Content-Type: application/json"
```

## Create A Draft With Agent Graph Topology

Create a workflow draft through the existing workflow registry API, then call:

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/agent-graph" | jq .
```

Expected result:

- `source` is `draft`
- `state` is `ready` or `empty`
- node IDs use `node:<node_key>`
- edge IDs use `edge:<edge_key>`
- `accessibility.node_summaries` and `accessibility.edge_summaries` are present
- no raw prompts, completions, secrets, credentials, private messages, memory
  contents, provider payloads, local file paths, or raw tool payloads appear

## Publish And Inspect A Version Graph

Validate and publish the draft through existing workflow publish APIs, then call:

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/agent-graph" | jq .
```

Expected result:

- `source` is `published_version`
- provenance includes `workflow_version_bundle_id`
- graph topology is derived from the published bundle document when available
- partial published metadata is marked with `partial: true`

## Focused Validation

```bash
uv run pytest tests/unit/admin/test_agent_graph.py \
  tests/unit/api/test_admin_agent_graph_schemas.py \
  tests/integration/api/test_admin_agent_graph_api.py
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run ruff check src/multi_agent_platform/api/schemas/admin_agent_graph.py \
  src/multi_agent_platform/admin/workflow_registry/agent_graph.py \
  src/multi_agent_platform/api/routers/admin_workflows.py \
  tests/unit/admin/test_agent_graph.py \
  tests/unit/api/test_admin_agent_graph_schemas.py \
  tests/integration/api/test_admin_agent_graph_api.py
uv run mypy src/multi_agent_platform/api/schemas/admin_agent_graph.py \
  src/multi_agent_platform/admin/workflow_registry/agent_graph.py
```

## Full Spec Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/065-agent-communication-graph-contracts-and-projections
uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml
uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml \
  --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/qa065-after-spec
```
