# QA066 User Guide: Spec 066 - React Agent Graph Viewer For Workflow Drafts And Versions

## Detailed Overview

The Agent Graph Viewer helps Admin users inspect workflow communication.
It appears on workflow draft pages.
It appears for published workflow version pages.
It is read-only.
It does not edit graph topology.
It uses backend Agent Communication Graph JSON.
It shows coordinator agent nodes.
It shows sub-agent nodes.
It shows tool nodes.
It shows join nodes.
It shows approval nodes.
It shows handoff nodes.
It shows terminal nodes.
It shows directional communication edges.
It shows edge labels such as Delegates.
It shows edge labels such as Sends context.
It shows edge labels such as Returns result.
It shows edge labels such as Joins.
It shows edge labels such as Hands off.
It shows safe graph badges.
It shows safe node badges.
It shows safe edge badges.
It shows safe reference summaries.
It shows related links when the backend provides them.
It includes a keyboard-readable node list.
It includes a keyboard-readable edge list.
It includes a selected-item detail panel.
It shows truthful loading state.
It shows truthful empty state.
It shows truthful denied state.
It shows truthful not-found state.
It shows truthful partial state.
It shows truthful error state.
It does not create fake graph records.
It does not show raw prompts.
It does not show raw completions.
It does not show credentials.
It does not show provider payloads.
It does not show private channel messages.
It does not show memory contents.
It does not show raw external tool outputs.

## Who Should Use This Guide

Use this guide if you are manually validating qa066.
Use this guide if you review Admin workflow UI changes.
Use this guide if you need to confirm accessible list behavior.
Use this guide if you need to confirm selected detail behavior.
Use this guide if you need to confirm tenant isolation.
Use this guide if you need to confirm redaction.
Use this guide if you need desktop and mobile screenshot evidence.
You need the local repository.
You need Docker.
You need PostgreSQL through Docker Compose.
You need Python dependencies through `uv`.
You need npm dependencies under `frontend/admin`.
You need a browser.
You do not need Auth0.
You do not need live provider credentials.
You do not need Telegram access.
You do not need external connector access.

## Manual QA Prerequisites

Confirm `.env.qa066` exists.
Confirm `DATABASE_URL` uses `multi_agent_platform_qa066`.
Confirm `RUNTIME_CHECKPOINTER_DATABASE_URL` uses `multi_agent_platform_qa066`.
Confirm static secret references use the `qa066/` prefix.
Confirm storage root is `.data/qa066-artifacts`.
Confirm local-principal auth is active.
Confirm Acme tenant admin is available.
Confirm Globex tenant admin is available.
Confirm live provider probes are disabled.
Confirm live Telegram delivery is disabled.
Confirm external connector calls are disabled.
Confirm screenshot output can be written to `output/playwright/qa066_ui`.
Confirm evidence notes can be written to `/tmp/qa066-ui-notes.txt`.
Confirm fixed draft ID is `66666666-1111-4666-8666-000000000066`.
Confirm fixed version ID is `66666666-4444-4666-8666-000000000066`.

## Step-by-Step Manual QA

1. Copy the qa066 environment file.

```bash
cp specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/.env.qa066 .env
```

Expected result: the active environment targets qa066.

2. Install dependencies.

```bash
uv sync
```

Expected result: Python dependencies are ready.

3. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running.

4. Recreate the qa066 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa066 && createdb -U postgres multi_agent_platform_qa066'
```

Expected result: the qa066 database is empty.

5. Apply migrations.

```bash
uv run alembic upgrade head
```

Expected result: database schema is current.

6. Seed the qa066 workflow.

```bash
uv run python scripts/qa/seed_agent_graph_viewer_qa066.py
```

Expected result: the command prints the fixed draft and version IDs.

7. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the API starts on port 8000.

8. Open local login for the draft.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows/drafts/66666666-1111-4666-8666-000000000066
```

Expected result: local login options are visible.

9. Choose Acme tenant admin.

Expected result: the seeded draft workflow page opens.

10. Inspect the draft graph title.

Expected result: the page shows `Draft communication`.

11. Inspect draft node categories.

Expected result: coordinator, specialist, tool, join, approval, handoff, and terminal graph content is visible.

12. Inspect draft edge labels.

Expected result: Delegates, Joins, Hands off, and Transitions labels are visible.

13. Select the Specialist node from the node list.

Expected result: detail panel shows Specialist and Sub-agent.

14. Select the Handoff edge from the edge list.

Expected result: detail panel shows Hands off.

15. Confirm existing workflow panels remain visible.

Expected result: workflow graph preview, validation, publish, revision, and JSON inspector surfaces still appear.

16. Open the published version route.

```text
http://127.0.0.1:8000/admin/app/workflows/versions/66666666-4444-4666-8666-000000000066
```

Expected result: the page shows `Published version communication`.

17. Capture desktop screenshot.

Expected result: screenshot shows graph, lists, and detail panel without overlap.

18. Capture mobile screenshot.

Expected result: screenshot shows graph, lists, and detail panel stacked without overlap.

19. Try Globex tenant admin against the Acme draft route.

Expected result: Globex does not see Acme graph content.

20. Run focused frontend tests.

```bash
npm --prefix frontend/admin test -- AgentGraphPanel WorkflowBuilderPage
```

Expected result: focused frontend tests pass.

21. Run generated contract check.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected result: generated graph types are fresh.

22. Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/validation.yml --start-processes
```

Expected result: desktop and mobile screenshots are captured.

## Expected Results

Acme tenant admin can view the draft graph.
Acme tenant admin can view the published version graph.
The graph is read-only.
The graph uses backend graph JSON.
The graph shows representative node categories.
The graph shows directional edge labels.
The node list is visible.
The edge list is visible.
The selected detail panel is visible.
Node selection updates details.
Edge selection updates details.
Existing workflow builder panels remain visible.
Published version route shows published graph content.
Desktop screenshot has no overlapping text.
Mobile screenshot has no overlapping text.
Globex does not see Acme graph content.
Generated graph types are fresh.
Focused frontend tests pass.
Playwright validation passes.
No fake production graph records are created.

## Evidence To Capture

Capture `/tmp/qa066-ui-seed.txt`.
Capture `/tmp/qa066-focused-frontend.txt`.
Capture `/tmp/qa066-types-check.txt`.
Capture `output/playwright/qa066_ui/qa066-agent-graph-desktop.png`.
Capture `output/playwright/qa066_ui/qa066-agent-graph-mobile.png`.
Capture `/tmp/qa066-ui-notes.txt`.
Capture `.data/qa066-artifacts/evidence/qa066-agent-graph-seed.json`.
Capture `.data/curl_test_runs/qa066-after-spec`.
Expected result: evidence files contain safe IDs, labels, statuses, and screenshot paths only.

## Security And Redaction Checks

Search visible copy for raw prompt markers.
Search visible copy for raw completion markers.
Search visible copy for credential markers.
Search visible copy for provider payload markers.
Search visible copy for private channel markers.
Search visible copy for memory content markers.
Search visible copy for raw tool output markers.
Search screenshots manually for unsafe content.
Search reviewer notes for unsafe content.
Expected result: no unsafe marker appears in visible UI or evidence notes.

## Tenant Isolation Checks

Use Acme tenant admin for success.
Use Globex tenant admin for denial.
Attempt to open the Acme draft as Globex.
Attempt to open the Acme version as Globex.
Confirm no Acme graph node appears to Globex.
Confirm no Acme graph edge appears to Globex.
Confirm no Acme graph ID appears to Globex.
Expected result: cross-tenant graph content is not visible.

## Troubleshooting

If the graph is missing, rerun the seed script.
If the page is empty, confirm the fixed draft ID.
If published graph is missing, confirm the fixed version ID.
If local login fails, confirm `AUTH_MODE=local_principal`.
If Acme is denied, inspect the local principal catalog.
If Globex sees graph content, stop and fix tenant isolation.
If typecheck fails, inspect generated graph types.
If focused tests fail, inspect AgentGraphPanel selection behavior.
If desktop screenshot overlaps, inspect panel CSS.
If mobile screenshot overlaps, inspect responsive CSS.
If Playwright fails before login, inspect `/tmp/qa066-api.log`.
If curl regression fails, inspect `.data/curl_test_runs/qa066-after-spec`.
