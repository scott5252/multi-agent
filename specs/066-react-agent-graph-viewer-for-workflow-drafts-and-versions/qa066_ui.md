# QA066 UI Walkthrough: React Agent Graph Viewer For Workflow Drafts And Versions

## Goal

This walkthrough validates the browser-facing qa066 graph viewer.
The Admin UI must show draft communication as a graph.
The Admin UI must show published version communication as a graph.
The graph must come from backend Agent Communication Graph JSON.
The graph must include a keyboard-readable node list.
The graph must include a keyboard-readable edge list.
The graph must show safe selected node and edge details.
The graph must stay readable on desktop and mobile widths.
The graph must not show protected raw payloads.
Expected: browser evidence proves the graph viewer is useful without relying on fake production records.

## How To Use This Guide

Run commands from the repository root.
Use `.env.qa066`.
Use Acme tenant admin for successful graph viewing.
Use Globex tenant admin for isolation checks.
Capture screenshots under `output/playwright/qa066_ui`.
Capture notes under `/tmp/qa066-ui-notes.txt`.
Keep notes limited to visible labels, statuses, safe IDs, and screenshot paths.
Do not paste raw prompts, completions, secrets, provider payloads, memory contents, private messages, or raw tool outputs.
Expected: a reviewer can repeat the walkthrough from a clean local database.

## Environment Setup

Copy the environment.

```bash
cp specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/.env.qa066 .env
```

Expected: `.env.qa066` is active.

Prepare the database.

```bash
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa066 && createdb -U postgres multi_agent_platform_qa066'
uv run alembic upgrade head
```

Expected: the qa066 database is migrated.

Seed graph viewer data.

```bash
uv run python scripts/qa/seed_agent_graph_viewer_qa066.py | tee /tmp/qa066-ui-seed.txt
```

Expected: output includes `workflow_draft_id=66666666-1111-4666-8666-000000000066`.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 | tee /tmp/qa066-ui-api.log
```

Expected: the API is available at `http://127.0.0.1:8000`.

## Browser Walkthrough

1. Open local login for the draft graph.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows/drafts/66666666-1111-4666-8666-000000000066
```

Expected: the local login page lists local principals.
What is happening: the browser is preparing deterministic local-principal auth.
Why this matters: graph visibility must use existing Admin authorization.

2. Select Acme tenant admin.

Expected: the browser opens the seeded workflow draft page.
What is happening: the Admin shell loads in Acme tenant scope.
Why this matters: draft graph data must be tenant-scoped.

3. Inspect the draft graph panel title.

Expected: the page shows `Draft communication`.
What is happening: the UI fetched the draft Agent Communication Graph.
Why this matters: the visible graph is backend-owned, not a local sample.

4. Inspect the graph canvas.

Expected: the canvas shows Coordinator, Specialist, Join, Approval, Handoff, and Done nodes.
What is happening: node categories are rendered from the graph contract.
Why this matters: users can inspect intended agent and sub-agent routing.

5. Inspect edge labels.

Expected: visible edge labels include Delegates, Joins, Hands off, and Transitions.
What is happening: directional communication labels come from backend graph edges.
Why this matters: reviewers can understand work movement between agents.

6. Inspect graph badges.

Expected: the panel shows a safe projected graph badge.
What is happening: graph status badges render as concise safe labels.
Why this matters: reviewers see status without raw validation payloads.

7. Select the Specialist node from the node list.

Expected: the detail panel shows `Specialist` and `Sub-agent`.
What is happening: keyboard-readable list selection updates the same detail region as canvas selection.
Why this matters: the list alternative is equivalent, not decorative.

8. Select the Handoff edge from the edge list.

Expected: the detail panel shows `Hands off`.
What is happening: edge detail renders safe summary and category data.
Why this matters: communication paths are inspectable.

9. Capture desktop screenshot.

Expected: save `output/playwright/qa066_ui/qa066-agent-graph-desktop.png`.
What is happening: desktop visual evidence records graph, list, and detail layout.
Why this matters: reviewers can confirm no overlapping text.

10. Open the published version page.

```text
http://127.0.0.1:8000/admin/app/workflows/versions/66666666-4444-4666-8666-000000000066
```

Expected: the page shows `Published version communication`.
What is happening: the UI fetched the published version graph endpoint.
Why this matters: immutable version topology is visible.

11. Capture mobile screenshot.

Expected: save `output/playwright/qa066_ui/qa066-agent-graph-mobile.png`.
What is happening: the graph panel uses narrow viewport layout.
Why this matters: mobile graph evidence catches overlap and hidden list regressions.

12. Open Globex local login and attempt the draft route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows/drafts/66666666-1111-4666-8666-000000000066
```

Expected: Globex does not see Acme graph data.
What is happening: backend graph and workflow routes enforce tenant scope.
Why this matters: cross-tenant graph leakage would block release.

## Required Automated Evidence

Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/validation.yml --start-processes
```

Expected: desktop and mobile screenshots are captured.

Run focused frontend tests.

```bash
npm --prefix frontend/admin test -- AgentGraphPanel WorkflowBuilderPage
```

Expected: graph component and workflow page tests pass.

Run frontend typecheck.

```bash
npm --prefix frontend/admin run typecheck
```

Expected: strict TypeScript passes.

Run frontend build.

```bash
npm --prefix frontend/admin run build
```

Expected: Vite emits build assets.

Run backend quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all backend quality gates pass.

## UI Evidence Checklist

- Screenshot shows `Draft communication`.
- Screenshot shows `Published version communication`.
- Screenshot shows a graph canvas.
- Screenshot shows a node list.
- Screenshot shows an edge list.
- Screenshot shows a selected detail panel.
- Screenshot shows Coordinator.
- Screenshot shows Specialist.
- Screenshot shows Handoff.
- Screenshot shows `Sub-agent`.
- Screenshot shows `Hands off`.
- Screenshot shows no raw prompt text.
- Screenshot shows no raw completion text.
- Screenshot shows no provider payload.
- Screenshot shows no secret-like value.
- Screenshot shows no private channel payload.
- Screenshot shows no memory content.
- Screenshot shows no raw external tool payload.
- Reviewer notes include `http://127.0.0.1:8000/auth/local-login`.
- Reviewer notes include `.env.qa066`.
- Reviewer notes include `/tmp/qa066-ui-seed.txt`.
- Expected: UI evidence proves safe, live-data graph rendering.

## Acceptance Notes Template

Record QA id qa066.
Record local login URL `http://127.0.0.1:8000/auth/local-login`.
Record draft route `/admin/app/workflows/drafts/66666666-1111-4666-8666-000000000066`.
Record version route `/admin/app/workflows/versions/66666666-4444-4666-8666-000000000066`.
Record desktop screenshot `output/playwright/qa066_ui/qa066-agent-graph-desktop.png`.
Record mobile screenshot `output/playwright/qa066_ui/qa066-agent-graph-mobile.png`.
Record seed output `/tmp/qa066-ui-seed.txt`.
Record frontend test output `/tmp/qa066-focused-frontend.txt`.
Expected: acceptance notes contain only safe labels, IDs, statuses, and file paths.

## Troubleshooting

- If login fails, confirm local-principal auth is active in `.env.qa066`.
- If the graph panel is missing, rerun the qa066 seed script.
- If the draft route is not found, verify the fixed draft ID in seed output.
- If the version route is not found, verify the fixed version ID in seed output.
- If graph fetches are denied for Acme, inspect local-principal tenant ID.
- If graph fetches succeed for Globex, stop and fix tenant isolation.
- If text overlaps on desktop, inspect `.agent-graph-layout`.
- If text overlaps on mobile, inspect responsive graph CSS.
- If screenshots contain unsafe text, stop and fix graph rendering before continuing.
- If Playwright cannot click login, inspect `/tmp/qa066-ui-api.log`.

## Related Files

- `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- `frontend/admin/src/styles/admin.css`
- `frontend/admin/src/test/workflowBuilderTestData.ts`
- `scripts/qa/seed_agent_graph_viewer_qa066.py`
- `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/.env.qa066`
- `output/playwright/qa066_ui`
