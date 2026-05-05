# QA030 UI Walkthrough

## Goal

QA030 UI validation proves the React workflow builder renders safe guided workflow authoring, graph review, validation, publish evidence, revisions, and redacted JSON preview.

The route under review is `/admin/app/workflows`.

The browser should show the workflow draft, backend-owned reference choices, a graph canvas, keyboard-readable node and edge lists, validation findings, publish evidence, revision history, and a read-only JSON preview.

The browser should not show raw prompts, completions, memory contents, private channel messages, provider responses, Telegram updates, connector outputs, stack traces, local paths, raw credentials, or unauthorized tenant labels.

The builder uses deterministic QA030 data.

The builder does not call live providers.

The builder does not call Telegram.

The builder does not call external tools.

Expected: screenshots show only safe summaries and artifact references.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa030`.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, or confusing tenant scope.

Do not paste real secrets into the browser.

Do not paste raw prompts, completions, memory, private messages, provider responses, Telegram updates, connector outputs, stack traces, or local paths into reviewer notes.

Expected: QA evidence can be shared with reviewers without redaction cleanup.

What is happening: the browser is exercising the same route tenant admins use for workflow drafting.

Why this matters: UI validation catches layout, focus, and copy issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/030-react-workflow-builder/.env.qa030 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa030 && createdb -U postgres multi_agent_platform_qa030'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa030 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa030-artifacts output/playwright/qa030_ui
```

Expected: database, React assets, and evidence folders are ready.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: worker starts without live provider calls.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/030-react-workflow-builder
```

Run backend quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Run full QA030 validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml --start-processes
```

Expected: all automated commands pass before screenshots are accepted.

What is happening: the QA030 manifest resets the database, builds assets, starts app processes, and captures screenshots.

Why this matters: manual observations should match automated evidence.

## Browser Walkthrough

### Step 1: Denied Workflow Builder Route

Open:

```text
http://127.0.0.1:8000/admin/app/workflows
```

Expected: a 401 response appears when not logged in.

Expected: no workflow draft appears.

Expected: no graph or evidence appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: workflow drafts cannot leak anonymously.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-denied.png`.

### Step 2: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Choose `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app/workflows`.

Expected: the shell shows `React Admin`.

Expected: the page heading says `Workflow builder`.

Expected: the active scope is Acme.

What is happening: the local-principal cookie authorizes the tenant builder envelope.

Why this matters: the builder must preserve tenant scope through the React shell.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-tenant.png`.

### Step 3: Review Guided Draft Authoring

Find `Metadata`.

Find `References`.

Find `Graph`.

Find `Publish`.

Expected: section statuses are visible.

Expected: the draft name is `Daily briefing workflow`.

Expected: the revision is `draft-rev-qa030-current`.

Expected: the `Save draft` button is visible.

Expected: the `Simulate stale save` button is visible.

What is happening: the backend owns the current draft revision and action hrefs.

Why this matters: authoring state remains auditable and revision-aware.

### Step 4: Save Draft

Click `Save draft`.

Expected: the page shows `accepted`.

Expected: the page shows `audit-workflow-save-qa030`.

Expected: no unsafe payload appears.

What is happening: the save button posts to the backend draft action.

Why this matters: the browser does not create workflow revisions on its own.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-save.png`.

### Step 5: Review References

Find `Pinned runtime inputs`.

Find `Daily briefing prompt`.

Find `Briefing runtime profile`.

Find `Weather connector skill`.

Find `Daily briefing required suite`.

Expected: each reference has a safe readiness status.

Expected: no raw prompt text is visible.

What is happening: references are safe options produced by the lookup contract.

Why this matters: prompt and provider details stay governed by backend policy.

### Step 6: Review Graph

Find `Runtime structure`.

Find `Start briefing`.

Find `Calendar branch`.

Find `Weather branch`.

Find `Join briefing branches`.

Find `Edges and joins`.

Expected: the graph canvas appears.

Expected: node and edge details are available as lists for keyboard review.

Expected: no raw tool result is visible.

What is happening: the graph has both visual and list representations.

Why this matters: graph semantics remain reviewable by keyboard users.

### Step 7: Run Validation

Find `Backend-owned findings`.

Click `Run validation`.

Expected: the page shows `Required Daily briefing test evidence is stale`.

Click `Mark evidence current`.

Expected: the page shows publish readiness with a confirmation requirement.

What is happening: validation findings and readiness are returned by backend actions.

Why this matters: publish blockers cannot be bypassed by local React state.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-validation.png`.

### Step 8: Review Publish Gate

Find `Evidence and decision`.

Find `Daily briefing required suite`.

Find `artifact-ref-qa030-stale-evidence`.

Click `Check publish gate`.

Expected: the page shows `validation_error`.

Click `Prepare publish`.

Expected: the page shows `confirmation_required`.

Click `Confirm publish`.

Expected: the page shows `Workflow published as an immutable bundle`.

What is happening: publish is split into gate review, confirmation, and accepted result.

Why this matters: irreversible publishing remains explicit and auditable.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-publish.png`.

### Step 9: Review Revisions And JSON Preview

Find `Immutable draft history`.

Find `audit-workflow-revision-current-qa030`.

Find `Read-only preview`.

Find `artifact-ref-qa030-json-preview`.

Expected: the JSON preview contains safe summary fields only.

Expected: no raw prompts, completions, memory contents, provider responses, channel messages, connector outputs, local paths, or credential values appear.

What is happening: advanced JSON is summarized before it reaches the browser.

Why this matters: reviewers can inspect structure without seeing sensitive payloads.

### Step 10: Cross-Tenant Check

Open:

```text
http://127.0.0.1:8000/admin/app/workflows?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: the tenant-admin-acme principal is denied.

Expected: `Globex` does not appear.

Expected: workflow builder data does not appear.

What is happening: the Acme principal is denied before a Globex builder envelope is created.

Why this matters: tenant isolation fails closed.

Screenshot evidence: `output/playwright/qa030_ui/qa030-react-workflows-cross-tenant.png`.

## UI Evidence Checklist

- No overlapping text.
- No clipped buttons.
- No layout jump when mutation results appear.
- Graph canvas is visible and nonblank.
- Node and edge lists are visible without mouse interaction.
- Publish buttons fit on desktop and mobile widths.
- Artifact references wrap instead of overflowing.
- No unsafe raw payloads or local paths are visible.

## Acceptance Notes Template

Use this template for UI review notes:

```text
QA030 UI reviewer:
Browser:
Viewport:
Denied screenshot:
Tenant screenshot:
Save screenshot:
Publish screenshot:
Cross-tenant screenshot:
Graph visible and nonblank:
Keyboard-readable graph lists visible:
Unsafe text absent:
Tenant isolation result:
Decision:
```

Expected: screenshots are saved under `output/playwright/qa030_ui`.

What is happening: the template records both visual and safety outcomes.

Why this matters: later reviewers can understand what was accepted without rerunning the browser.

## Troubleshooting

If the page stays on local login, clear the local-principal cookie and repeat the login step.

If the graph canvas is blank, rerun `cd frontend/admin && npm run build` and reload the browser.

If publish buttons do not update, wait for network idle after each click and retry from a fresh login.

If tenant labels look wrong, verify the `tenant_id` query and seeded QA030 tenant rows.

Expected: troubleshooting preserves auth, tenant, and redaction requirements.

What is happening: each fix restores deterministic local QA state.

Why this matters: UI issues should not be solved by bypassing protected routes.

## Related Files

- `specs/030-react-workflow-builder/qa030.md`.
- `specs/030-react-workflow-builder/qa030_user_guide.md`.
- `specs/030-react-workflow-builder/.env.qa030`.
- `specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml`.
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`.
- `frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx`.
- `frontend/admin/src/styles/admin.css`.
