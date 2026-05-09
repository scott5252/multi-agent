# QA068 UI Walkthrough: Durable Agent Interaction Evidence And Replay Graph

## Goal
Confirm that the operations workbench renders durable replay evidence through the existing runtime graph panel on desktop and mobile.

## How To Use This Guide
Use local-principal login only. Save screenshots and reviewer notes under `/tmp/qa068-ui-*` or the Playwright output directory. Do not capture raw payloads.

## Environment Setup
```bash
cp specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_runtime_interaction_evidence_qa068.py
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```
Expected: the local app is available at `http://127.0.0.1:8000`.
What is happening: the QA database is seeded with a run containing replay evidence.
Why this matters: the browser checks should use live backend-owned data, not fixture-only UI state.

## Browser Walkthrough
```bash
open http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations%3Frun_id%3D68686868-6666-4868-8868-000000000068%26tenant_id%3D11111111-1111-1111-1111-111111111111
```
Expected: the local login page shows `tenant-admin-acme`.
What is happening: the reviewer is entering through deterministic local-principal auth.
Why this matters: Auth0 and production auth are not needed for QA068.

### Browser Step 1
Click the `tenant-admin-acme` login button and wait for Operations to load.
Expected: the page title includes Operations and the runtime run communication panel appears.
What is happening: step 1 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 1 helps prove replay evidence is usable without exposing protected data.

### Browser Step 2
Find the runtime graph edge list and select `Coordinator to Specialist`.
Expected: the detail panel shows `Replay 1: handoff` and `Coordinator sent safe context to Specialist.`
What is happening: step 2 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 2 helps prove replay evidence is usable without exposing protected data.

### Browser Step 3
Select the Specialist node from the node list.
Expected: the detail panel shows retry-scheduled safe evidence without raw stack traces.
What is happening: step 3 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 3 helps prove replay evidence is usable without exposing protected data.

### Browser Step 4
Resize the viewport to 390 by 900 or run the mobile Playwright flow.
Expected: replay references remain readable and no graph text overlaps incoherently.
What is happening: step 4 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 4 helps prove replay evidence is usable without exposing protected data.

### Browser Step 5
Review visible graph, list, badge, and detail content for safe-summary behavior 5.
Expected: browser step 5 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 5 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 5 helps prove replay evidence is usable without exposing protected data.

### Browser Step 6
Review visible graph, list, badge, and detail content for safe-summary behavior 6.
Expected: browser step 6 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 6 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 6 helps prove replay evidence is usable without exposing protected data.

### Browser Step 7
Review visible graph, list, badge, and detail content for safe-summary behavior 7.
Expected: browser step 7 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 7 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 7 helps prove replay evidence is usable without exposing protected data.

### Browser Step 8
Review visible graph, list, badge, and detail content for safe-summary behavior 8.
Expected: browser step 8 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 8 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 8 helps prove replay evidence is usable without exposing protected data.

### Browser Step 9
Review visible graph, list, badge, and detail content for safe-summary behavior 9.
Expected: browser step 9 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 9 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 9 helps prove replay evidence is usable without exposing protected data.

### Browser Step 10
Review visible graph, list, badge, and detail content for safe-summary behavior 10.
Expected: browser step 10 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 10 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 10 helps prove replay evidence is usable without exposing protected data.

### Browser Step 11
Review visible graph, list, badge, and detail content for safe-summary behavior 11.
Expected: browser step 11 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 11 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 11 helps prove replay evidence is usable without exposing protected data.

### Browser Step 12
Review visible graph, list, badge, and detail content for safe-summary behavior 12.
Expected: browser step 12 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 12 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 12 helps prove replay evidence is usable without exposing protected data.

### Browser Step 13
Review visible graph, list, badge, and detail content for safe-summary behavior 13.
Expected: browser step 13 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 13 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 13 helps prove replay evidence is usable without exposing protected data.

### Browser Step 14
Review visible graph, list, badge, and detail content for safe-summary behavior 14.
Expected: browser step 14 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 14 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 14 helps prove replay evidence is usable without exposing protected data.

### Browser Step 15
Review visible graph, list, badge, and detail content for safe-summary behavior 15.
Expected: browser step 15 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 15 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 15 helps prove replay evidence is usable without exposing protected data.

### Browser Step 16
Review visible graph, list, badge, and detail content for safe-summary behavior 16.
Expected: browser step 16 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 16 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 16 helps prove replay evidence is usable without exposing protected data.

### Browser Step 17
Review visible graph, list, badge, and detail content for safe-summary behavior 17.
Expected: browser step 17 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 17 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 17 helps prove replay evidence is usable without exposing protected data.

### Browser Step 18
Review visible graph, list, badge, and detail content for safe-summary behavior 18.
Expected: browser step 18 shows only safe labels, statuses, references, and reviewer-safe summaries.
What is happening: step 18 checks the same backend-owned replay evidence through a user-facing surface.
Why this matters: step 18 helps prove replay evidence is usable without exposing protected data.

## Required Automated Evidence
```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/068-durable-agent-interaction-evidence-and-replay-graph/validation.yml --start-processes
```
Expected: `qa068-interaction-replay-graph-desktop.png` and `qa068-interaction-replay-graph-mobile.png` are produced.
What is happening: Playwright logs in, opens the operations route, selects graph detail, and captures screenshots.
Why this matters: the evidence is repeatable and covers both desktop and mobile layouts.
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/frontend/generate_admin_react_types.py --check
cd frontend/admin && npm run typecheck
cd frontend/admin && npm test
cd frontend/admin && npm run build
```
Expected: the same quality commands used by API QA exit 0.
What is happening: the UI is checked alongside backend typing and coverage.
Why this matters: replay graph UI depends on generated contracts and backend route behavior.

## UI Evidence Checklist
- Expected: screenshot or reviewer note 1 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 1.
- Why this matters: evidence item 1 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 2 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 2.
- Why this matters: evidence item 2 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 3 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 3.
- Why this matters: evidence item 3 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 4 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 4.
- Why this matters: evidence item 4 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 5 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 5.
- Why this matters: evidence item 5 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 6 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 6.
- Why this matters: evidence item 6 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 7 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 7.
- Why this matters: evidence item 7 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 8 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 8.
- Why this matters: evidence item 8 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 9 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 9.
- Why this matters: evidence item 9 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 10 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 10.
- Why this matters: evidence item 10 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 11 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 11.
- Why this matters: evidence item 11 supports audit-friendly QA review.
- Expected: screenshot or reviewer note 12 confirms replay evidence is safe, readable, and tenant-scoped.
- What is happening: reviewer captures UI evidence item 12.
- Why this matters: evidence item 12 supports audit-friendly QA review.
## Acceptance Notes Template
- Expected: note 1 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 2 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 3 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 4 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 5 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 6 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 7 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 8 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 9 includes viewport, selected graph item, visible replay summary, and redaction result.
- Expected: note 10 includes viewport, selected graph item, visible replay summary, and redaction result.
## Troubleshooting
Missing replay text means seed data did not run after migration.
Expected: the reviewer can isolate the issue without using production systems.
What is happening: troubleshooting stays within deterministic local QA.
Why this matters: QA evidence remains safe and reproducible.
A blank graph usually means the run ID or tenant ID is incorrect.
Expected: the reviewer can isolate the issue without using production systems.
What is happening: troubleshooting stays within deterministic local QA.
Why this matters: QA evidence remains safe and reproducible.
Unexpected raw markers should be treated as a release blocker.
Expected: the reviewer can isolate the issue without using production systems.
What is happening: troubleshooting stays within deterministic local QA.
Why this matters: QA evidence remains safe and reproducible.
Mobile clipping should be captured with screenshot evidence.
Expected: the reviewer can isolate the issue without using production systems.
What is happening: troubleshooting stays within deterministic local QA.
Why this matters: QA evidence remains safe and reproducible.
Use `/tmp/qa068-api.log` for server-side diagnostics.
Expected: the reviewer can isolate the issue without using production systems.
What is happening: troubleshooting stays within deterministic local QA.
Why this matters: QA evidence remains safe and reproducible.
## Related Files
- specs/068-durable-agent-interaction-evidence-and-replay-graph/qa068.md
- specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068
- output/playwright/qa068_ui
- frontend/admin/src/components/workflows/AgentGraphPanel.tsx
- frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx
