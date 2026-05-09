# QA065 UI Walkthrough: Agent Communication Graph Contracts And Projections

## Goal

This walkthrough validates the browser-facing qa065 evidence path.
Spec 065 is a backend contract feature.
The browser proof is therefore the OpenAPI contract and safe Admin shell access.
The draft graph route must appear in OpenAPI.
The published version graph route must appear in OpenAPI.
The response schema must be named for Agent Communication Graphs.
The local login path must work without external identity services.
The evidence must remain safe for reviewers.
The evidence must not include raw prompts.
The evidence must not include raw completions.
The evidence must not include provider payloads.
The evidence must not include secrets.
The evidence must not include authorization headers.
The evidence must not include private channel payloads.
The evidence must not include memory contents.
The evidence must not include raw external tool payloads.
Expected: a reviewer can prove the contract exists in the browser before Spec 066 adds the React graph viewer.

## How To Use This Guide

Run commands from the repository root.
Use `.env.qa065`.
Use the local-principal login page.
Use Acme as the success tenant.
Use Globex only for isolation checks.
Capture screenshots under `output/playwright/qa065_ui`.
Capture notes under `/tmp/qa065-ui-notes.txt`.
Keep notes limited to route names, schema names, response status codes, and safe IDs.
Do not paste raw workflow documents into notes.
Do not paste raw request headers into notes.
Do not paste provider diagnostics into notes.
Expected: the walkthrough produces deterministic reviewer evidence for qa065.

## Environment Setup

Copy the QA environment file.

```bash
cp specs/065-agent-communication-graph-contracts-and-projections/.env.qa065 .env
```

Expected: `.env.qa065` is the active local configuration.

Prepare local evidence directories.

```bash
mkdir -p .data/qa065-artifacts/evidence output/playwright/qa065_ui /tmp/qa065-evidence
```

Expected: screenshot and command output directories exist.

Install dependencies.

```bash
uv sync
```

Expected: Python dependencies are available for API and QA commands.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL container is healthy.

Reset the qa065 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa065 && createdb -U postgres multi_agent_platform_qa065'
```

Expected: only `multi_agent_platform_qa065` is recreated.

Apply migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete without live provider, Telegram, Auth0, or connector calls.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 | tee /tmp/qa065-ui-api.log
```

Expected: the API is available at `http://127.0.0.1:8000`.

## Browser Walkthrough

1. Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected: the page lists local-principal login choices.
What is happening: the browser is using deterministic local-principal authentication.
Why this matters: reviewers can validate Admin authorization without Auth0.

2. Select the Acme tenant admin principal.

Expected: the browser creates a local-principal session for Acme.
What is happening: the Admin backend receives a safe principal from the configured local catalog.
Why this matters: graph routes must inherit the same tenant-admin visibility rules as workflow registry routes.

3. Open the OpenAPI document.

```text
http://127.0.0.1:8000/openapi.json
```

Expected: the browser displays the FastAPI OpenAPI JSON.
What is happening: the backend exposes generated route metadata.
Why this matters: Spec 066 will consume these contracts through generated TypeScript types.

4. Search the page for the draft graph route.

```text
/admin/workflows/drafts/{workflow_draft_id}/agent-graph
```

Expected: the draft graph route appears exactly once in the OpenAPI paths.
What is happening: the route is registered on the workflow Admin router.
Why this matters: draft graph viewers can fetch topology without relying on mock data.

5. Search the page for the published graph route.

```text
/admin/workflows/versions/{workflow_version_bundle_id}/agent-graph
```

Expected: the published graph route appears exactly once in the OpenAPI paths.
What is happening: published bundle graph projection is exposed as a separate safe endpoint.
Why this matters: viewers can compare draft and immutable published graph provenance.

6. Search the page for the response schema name.

```text
AgentCommunicationGraph
```

Expected: the schema name appears in the OpenAPI components.
What is happening: FastAPI published the Pydantic response model.
Why this matters: generated React API contracts must stay stable and typed.

7. Search the page for safe response fields.

```text
accessibility
```

Expected: `accessibility` appears in the schema.
What is happening: the contract includes keyboard-readable node and edge summaries.
Why this matters: Spec 066 can provide a list equivalent for graph visualization.

8. Search the page for provenance fields.

```text
provenance
```

Expected: `provenance` appears in the schema.
What is happening: graph responses identify draft or version origins.
Why this matters: reviewers can tell which durable workflow record produced the graph.

9. Search the page for partial graph state.

```text
partial
```

Expected: `partial` appears in the schema.
What is happening: the backend can truthfully represent incomplete published bundle evidence.
Why this matters: the UI must never silently render a complete graph when evidence is missing.

10. Capture the OpenAPI screenshot.

Expected: save `output/playwright/qa065_ui/qa065-graphical-ui-smoke.png`.
What is happening: the screenshot records the route and schema contract in a browser.
Why this matters: release evidence includes reviewer-readable visual proof.

11. Open local login with an Admin redirect.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Expected: selecting Acme tenant admin reaches the Admin React shell or its safe fallback.
What is happening: the browser confirms Admin auth still works while the backend contract is present.
Why this matters: Spec 065 must not break existing Admin shell navigation.

12. Open local login with Globex tenant admin.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/openapi.json
```

Expected: OpenAPI remains schema-only and does not reveal tenant graph data.
What is happening: route metadata is public contract metadata, not tenant records.
Why this matters: browser evidence must avoid cross-tenant workflow content.

## Required Automated Evidence

Run the focused Playwright smoke for qa065.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml --start-processes
```

Expected: Playwright captures `qa065-graphical-ui-smoke.png`.

Run the QA document validator.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/065-agent-communication-graph-contracts-and-projections
```

Expected: qa065 API guide, UI walkthrough, user guide, and environment file pass validation.

Run the spec QA manifest.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml
```

Expected: qa065 automated checks pass.

Run focused backend tests.

```bash
uv run pytest tests/unit/api/test_admin_agent_graph_schemas.py tests/unit/admin/test_agent_graph.py tests/integration/api/test_admin_agent_graph_api.py tests/contract/test_workflow_registry_contract.py --no-cov
```

Expected: schema, projection, route, and OpenAPI tests pass.

Run generated type freshness.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: generated React Admin API contracts are fresh.

Run repository quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: lint, format, type, and coverage checks pass.

## UI Evidence Checklist

- Screenshot shows `http://127.0.0.1:8000/openapi.json`.
- Screenshot or reviewer notes show the draft agent graph route.
- Screenshot or reviewer notes show the published agent graph route.
- Screenshot or reviewer notes show `AgentCommunicationGraph`.
- Screenshot or reviewer notes show `accessibility`.
- Screenshot or reviewer notes show `provenance`.
- Screenshot or reviewer notes show `partial`.
- Screenshot or reviewer notes show no tenant workflow document body.
- Screenshot or reviewer notes show no raw prompt text.
- Screenshot or reviewer notes show no raw completion text.
- Screenshot or reviewer notes show no provider payload.
- Screenshot or reviewer notes show no secret-like value.
- Screenshot or reviewer notes show no private channel payload.
- Screenshot or reviewer notes show no memory content.
- Screenshot or reviewer notes show no raw external tool payload.
- Screenshot path is recorded as `output/playwright/qa065_ui/qa065-graphical-ui-smoke.png`.
- Reviewer notes path is recorded as `/tmp/qa065-ui-notes.txt`.
- Expected: evidence proves browser-visible contracts without exposing protected content.

## Acceptance Notes Template

Record QA id qa065.
Record local login URL `http://127.0.0.1:8000/auth/local-login`.
Record OpenAPI URL `http://127.0.0.1:8000/openapi.json`.
Record draft route `/admin/workflows/drafts/{workflow_draft_id}/agent-graph`.
Record version route `/admin/workflows/versions/{workflow_version_bundle_id}/agent-graph`.
Record response schema `AgentCommunicationGraph`.
Record screenshot `output/playwright/qa065_ui/qa065-graphical-ui-smoke.png`.
Record Playwright manifest `specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml`.
Record QA guide `specs/065-agent-communication-graph-contracts-and-projections/qa065.md`.
Record environment file `specs/065-agent-communication-graph-contracts-and-projections/.env.qa065`.
Expected: acceptance notes contain only safe route, schema, file, and status references.

## Troubleshooting

- If the login page is unavailable, confirm the API is running on `127.0.0.1:8000`.
- If OpenAPI is unavailable, inspect `/tmp/qa065-ui-api.log`.
- If the draft route is missing, confirm `admin_workflows.py` registered the route.
- If the version route is missing, confirm the published graph route uses the version bundle id path.
- If the schema name is missing, confirm the route response model is `AgentCommunicationGraph`.
- If generated types are stale, run `uv run python scripts/frontend/generate_admin_react_types.py`.
- If Playwright fails to start processes, confirm Docker and PostgreSQL are running.
- If the screenshot contains raw workflow JSON, rerun the browser smoke against `/openapi.json`.
- If unsafe content appears, stop and fix graph text validation before continuing.
- If port `8000` is busy, stop the other local API and rerun validation.

## Related Files

- `specs/065-agent-communication-graph-contracts-and-projections/.env.qa065`
- `specs/065-agent-communication-graph-contracts-and-projections/qa065.md`
- `specs/065-agent-communication-graph-contracts-and-projections/qa065_user_guide.md`
- `specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml`
- `src/multi_agent_platform/api/routers/admin_workflows.py`
- `src/multi_agent_platform/api/schemas/admin_agent_graph.py`
- `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- `frontend/admin/src/api/generated/reactAdminApi.ts`
- `output/playwright/qa065_ui`
