# QA065 User Guide: Spec 065 - Agent Communication Graph Contracts And Projections

## Detailed Overview

Spec 065 adds Agent Communication Graph contracts to the workflow Admin API.
The feature gives tenant admins a safe graph-shaped view of workflow topology.
It supports workflow drafts.
It supports published workflow version bundles.
It identifies coordinator agents.
It identifies sub-agents.
It identifies tool nodes derived from skill bindings.
It identifies join nodes.
It identifies approval nodes.
It identifies handoff nodes.
It identifies terminal nodes.
It identifies communication edges.
It identifies join edges.
It identifies handoff edges.
It includes provenance for the source durable record.
It includes validation badges.
It includes reference summaries.
It includes deterministic layout hints.
It includes keyboard-readable node summaries.
It includes keyboard-readable edge summaries.
It includes honest empty states.
It includes honest partial states.
It reuses existing workflow registry authorization.
It does not add a database migration.
It does not add production sample graph records.
It does not add a React graph canvas.
It prepares the contract that Spec 066 will render.
It must not expose raw prompts.
It must not expose raw completions.
It must not expose provider request payloads.
It must not expose provider response payloads.
It must not expose secrets.
It must not expose authorization headers.
It must not expose private channel messages.
It must not expose memory contents.
It must not expose raw external tool payloads.
Only safe labels, safe summaries, status values, route names, IDs, and artifact references belong in QA evidence.

## Who Should Use This Guide

Use this guide when manually validating qa065.
Use this guide when reviewing backend graph contracts.
Use this guide when checking that generated React contracts are fresh.
Use this guide when confirming workflow authorization behavior.
Use this guide when confirming tenant isolation.
Use this guide when confirming safe text validation.
Use this guide when preparing for Spec 066.
Use this guide when proving that graph data is derived from durable workflow records.
You need the local repository.
You need Docker.
You need PostgreSQL through Docker Compose.
You need Python dependencies installed with `uv`.
You need a browser for OpenAPI and local login checks.
You do not need Auth0.
You do not need live provider credentials.
You do not need Telegram credentials.
You do not need external connector access.

## Manual QA Prerequisites

Confirm the repository root is the current working directory.
Confirm `.env.qa065` exists.
Confirm `DATABASE_URL` targets `multi_agent_platform_qa065`.
Confirm `RUNTIME_CHECKPOINTER_DATABASE_URL` targets `multi_agent_platform_qa065`.
Confirm static secret references use the `qa065/` prefix.
Confirm `FILESYSTEM_STORAGE_ROOT` is `.data/qa065-artifacts`.
Confirm live provider probes are disabled.
Confirm live Telegram delivery is disabled.
Confirm external connector calls are disabled.
Confirm the local principal catalog includes Acme.
Confirm the local principal catalog includes Globex.
Confirm Acme has a tenant admin principal.
Confirm Acme has a tenant user principal.
Confirm Globex has a tenant admin principal.
Confirm screenshots can be saved under `output/playwright/qa065_ui`.
Confirm command output can be saved under `/tmp/qa065-*`.

## Step-by-Step Manual QA

1. Copy the qa065 environment file.

```bash
cp specs/065-agent-communication-graph-contracts-and-projections/.env.qa065 .env
```

Expected result: the active environment targets `multi_agent_platform_qa065`.

2. Create evidence directories.

```bash
mkdir -p .data/qa065-artifacts/evidence output/playwright/qa065_ui /tmp/qa065-evidence
```

Expected result: local QA evidence paths exist.

3. Install dependencies.

```bash
uv sync
```

Expected result: Python dependencies are ready.

4. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running.

5. Reset the qa065 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa065 && createdb -U postgres multi_agent_platform_qa065'
```

Expected result: the qa065 database is empty.

6. Apply database migrations.

```bash
uv run alembic upgrade head
```

Expected result: all schema objects exist.

7. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the API starts successfully on `127.0.0.1:8000`.

8. Open local login.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected result: local-principal login options are visible.

9. Choose Acme tenant admin.

Expected result: the browser stores an Acme tenant admin local-principal session.

10. Open the OpenAPI document.

```text
http://127.0.0.1:8000/openapi.json
```

Expected result: OpenAPI JSON appears in the browser.

11. Search for the draft graph route.

```text
/admin/workflows/drafts/{workflow_draft_id}/agent-graph
```

Expected result: the draft graph route is present.

12. Search for the published graph route.

```text
/admin/workflows/versions/{workflow_version_bundle_id}/agent-graph
```

Expected result: the published version graph route is present.

13. Search for the graph schema name.

```text
AgentCommunicationGraph
```

Expected result: the response schema is present.

14. Search for accessibility fields.

```text
accessibility
```

Expected result: the schema includes keyboard-readable summaries.

15. Search for provenance fields.

```text
provenance
```

Expected result: the schema identifies the source workflow record.

16. Search for partial state fields.

```text
partial
```

Expected result: the schema supports incomplete published graph evidence.

17. Capture a screenshot.

Expected result: the screenshot is saved as `output/playwright/qa065_ui/qa065-graphical-ui-smoke.png`.

18. Create a draft using the API QA guide.

Expected result: `/tmp/qa065-create-draft.json` contains a non-null draft ID.

19. Fetch the draft agent graph.

Expected result: `/tmp/qa065-draft-agent-graph.json` has `source` set to `draft` and `partial` set to false.

20. Validate draft node categories.

Expected result: coordinator, sub-agent, tool, join, approval, handoff, and terminal categories are present.

21. Validate draft edge categories.

Expected result: delegation, join, and handoff communication categories are present.

22. Validate the draft graph accessibility summaries.

Expected result: node and edge summaries are populated.

23. Publish the workflow draft using the API QA guide.

Expected result: `/tmp/qa065-publish.json` contains a workflow version bundle ID.

24. Fetch the published graph.

Expected result: `/tmp/qa065-version-agent-graph.json` has `source` set to `published_version`.

25. Check missing-auth behavior.

Expected result: an unauthenticated graph request returns `401`.

26. Check tenant-user behavior.

Expected result: an Acme tenant user graph request returns `403`.

27. Check cross-tenant behavior.

Expected result: a Globex tenant admin graph request for the Acme draft returns `403`.

28. Check not-found behavior.

Expected result: a missing draft graph request returns `404`.

29. Run safe text grep checks.

Expected result: graph JSON files do not contain unsafe raw prompt, raw completion, provider, secret, private channel, memory, or raw tool payload markers.

30. Run focused tests.

```bash
uv run pytest tests/unit/api/test_admin_agent_graph_schemas.py tests/unit/admin/test_agent_graph.py tests/integration/api/test_admin_agent_graph_api.py tests/contract/test_workflow_registry_contract.py --no-cov
```

Expected result: focused qa065 tests pass.

31. Run generated type freshness.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected result: generated React Admin API types are fresh.

32. Run QA document validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/065-agent-communication-graph-contracts-and-projections
```

Expected result: qa065 documentation passes validation.

33. Run Spec Kit QA.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml
```

Expected result: qa065 manifest validation passes.

34. Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml --start-processes
```

Expected result: browser smoke validation passes and captures the qa065 screenshot.

35. Run repository quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected result: lint, formatting, typing, and coverage gates pass.

## Expected Results

The draft graph route exists in OpenAPI.
The published graph route exists in OpenAPI.
The `AgentCommunicationGraph` schema exists in OpenAPI.
Graph responses are derived from workflow draft and bundle records.
Graph responses include source provenance.
Graph responses include deterministic layout hints.
Graph responses include validation badges.
Graph responses include reference summaries.
Graph responses include keyboard-readable accessibility summaries.
Empty draft graphs are truthful.
Published graphs can report partial state when compiled bundle evidence is unavailable.
Acme tenant admins can read Acme graph projections.
Acme tenant users cannot read graph projections.
Globex tenant admins cannot read Acme graph projections.
Unauthenticated callers cannot read graph projections.
Missing graph sources return not found.
Generated React contracts include the new graph response shape.
No production sample graph records are created.
No migration is required for qa065.
No React canvas is added in qa065.
No raw prompt content appears in graph JSON.
No raw completion content appears in graph JSON.
No provider payload appears in graph JSON.
No secret or authorization header appears in graph JSON.
No private channel message appears in graph JSON.
No memory contents appear in graph JSON.
No raw external tool payload appears in graph JSON.

## Evidence To Capture

Capture `/tmp/qa065-create-draft.json`.
Capture `/tmp/qa065-draft-agent-graph.json`.
Capture `/tmp/qa065-validation.json`.
Capture `/tmp/qa065-publish.json`.
Capture `/tmp/qa065-version-agent-graph.json`.
Capture `/tmp/qa065-missing-auth.txt`.
Capture `/tmp/qa065-denied-role.txt`.
Capture `/tmp/qa065-cross-tenant.txt`.
Capture `/tmp/qa065-not-found.txt`.
Capture `/tmp/qa065-focused-tests.txt`.
Capture `/tmp/qa065-types-check.txt`.
Capture `output/playwright/qa065_ui/qa065-graphical-ui-smoke.png`.
Capture `.data/curl_test_runs/qa065-after-spec`.
Expected result: evidence files contain only safe contract, status, and artifact references.

## Troubleshooting

If the API does not start, confirm `.env.qa065` is active.
If the database migration fails, confirm PostgreSQL is running.
If local login does not list principals, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.
If the draft graph route is missing, inspect `src/multi_agent_platform/api/routers/admin_workflows.py`.
If the published graph route is missing, inspect `src/multi_agent_platform/api/routers/admin_workflows.py`.
If schema validation fails, inspect `src/multi_agent_platform/api/schemas/admin_agent_graph.py`.
If graph topology is empty when it should be populated, inspect the workflow draft document.
If published graph state is partial unexpectedly, inspect filesystem storage under `.data/qa065-artifacts`.
If cross-tenant requests succeed, stop and fix workflow registry visibility checks.
If tenant-user requests succeed, stop and fix Admin authorization checks.
If unsafe strings appear, fix safe text validators before continuing.
If generated types are stale, run the type generation command without `--check` and review the diff.
If Playwright fails, inspect the generated screenshot and process logs.
If curl regression fails, inspect the first failing command in the curl-test output directory.
Expected result: each troubleshooting path points to a deterministic local fix.

## Related Files

Use `specs/065-agent-communication-graph-contracts-and-projections/spec.md` for requirements.
Use `specs/065-agent-communication-graph-contracts-and-projections/plan.md` for implementation strategy.
Use `specs/065-agent-communication-graph-contracts-and-projections/tasks.md` for task completion status.
Use `specs/065-agent-communication-graph-contracts-and-projections/qa065.md` for API validation commands.
Use `specs/065-agent-communication-graph-contracts-and-projections/qa065_ui.md` for browser validation.
Use `specs/065-agent-communication-graph-contracts-and-projections/.env.qa065` for local QA configuration.
Use `src/multi_agent_platform/api/schemas/admin_agent_graph.py` for graph response schemas.
Use `src/multi_agent_platform/admin/workflow_registry/agent_graph.py` for graph projection logic.
Use `src/multi_agent_platform/admin/workflow_registry/service.py` for workflow service entry points.
Use `src/multi_agent_platform/api/routers/admin_workflows.py` for API routes.
Use `tests/unit/api/test_admin_agent_graph_schemas.py` for safe schema tests.
Use `tests/unit/admin/test_agent_graph.py` for projection tests.
Use `tests/integration/api/test_admin_agent_graph_api.py` for route tests.
Use `tests/contract/test_workflow_registry_contract.py` for OpenAPI contract tests.
Use `frontend/admin/src/api/generated/reactAdminApi.ts` for generated React contracts.
