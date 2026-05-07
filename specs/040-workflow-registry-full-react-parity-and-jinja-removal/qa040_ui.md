# QA040 UI Walkthrough: Spec 040 - Workflow Registry Full React Parity And Jinja Removal

## Goal

This walkthrough proves that a browser reviewer can sign in locally, open the React workflow registry, inspect workflow create and draft panels, confirm graph and validation alternatives, inspect publish and version state, and verify old workflow links recover through React.

The walkthrough also proves that the deleted workflow templates are not required for normal browser navigation.

## How To Use This Guide

Follow these steps after the automated backend tests pass.

Capture screenshots for each major screen.

Save reviewer notes under `/tmp/qa040-ui-notes.md`.

Save screenshots under `output/playwright/qa040_ui`.

Use `platform-admin` first, then switch to `tenant-admin-acme`.

Do not enter real secrets, real prompt content, real provider credentials, or private external payloads.

What is happening: the browser loads a non-Jinja React host and fetches workflow JSON contracts from the backend.

Why this matters: Spec 040 deletes workflow templates, so the browser journey must prove React parity.

## Environment Setup

Copy the QA environment file.

```bash
cp specs/040-workflow-registry-full-react-parity-and-jinja-removal/.env.qa040 .env
```

Expected: local-principal auth is active for `qa040`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are available for backend and frontend validation.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: PostgreSQL is running locally.

Reset only the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa040 && createdb -U postgres multi_agent_platform_qa040'
```

Expected: only the `multi_agent_platform_qa040` database is recreated.

Apply migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete without external calls.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa040 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex are available for local principal checks.

Build React assets.

```bash
cd frontend/admin && npm run build
```

Expected: the React manifest and asset bundle are current.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns success.

Run the Playwright validation command when ready.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/040-workflow-registry-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: `output/playwright/qa040_ui/qa040-react-ui2-smoke.png` is created.

## Browser Walkthrough

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.

Expected: the page title is `Local Login` and it lists local principals.

What is happening: the auth router returns non-Jinja login HTML.

Why this matters: the workflow route must be reachable without a server-rendered login template.

2. Click the `platform-admin` sign-in button.

Expected: the browser redirects to `/admin/app/workflows`.

What is happening: the backend sets the local-principal cookie.

Why this matters: Playwright and manual QA use the same deterministic browser login path.

3. Wait for the React admin shell to load.

Expected: the page contains `Workflow` and shows the React admin shell.

What is happening: the host serves non-Jinja HTML and React fetches bootstrap plus workflow builder JSON.

Why this matters: workflow browser state is hydrated from backend contracts.

4. Inspect the workflow registry panel.

Expected: the panel shows workflow list text, filter or status state, and at least one workflow action link.

What is happening: React reads `registry` from the workflow builder envelope.

Why this matters: the old `workflows/index.html` page is no longer required.

5. Inspect the create workflow panel.

Expected: template choices and create action state are visible.

What is happening: React reads `create_state` from the workflow builder envelope.

Why this matters: the old `workflows/create.html` page is no longer required.

6. Inspect the draft details form.

Expected: the draft title, description, profile reference, prompt reference, save button, and stale-save affordance are visible.

What is happening: React reads draft, sections, lookups, and mutation links from backend JSON.

Why this matters: draft editing remains backend-owned after template removal.

7. Inspect the reference picker.

Expected: prompt and profile choices are selectable without exposing raw prompt text.

What is happening: React uses the safe reference catalog.

Why this matters: reference picking replaces the old workflow component template.

8. Inspect the graph preview.

Expected: visual nodes and a keyboard-readable list of nodes and edges are available.

What is happening: React renders the graph panel from server-owned graph data.

Why this matters: graph parity includes accessibility, not just pixels.

9. Run validation from the validation panel.

Expected: validation status, findings, and summary update without a page refresh.

What is happening: React posts to the backend validation endpoint and displays the mutation result.

Why this matters: the old validation panel template is no longer required.

10. Inspect the publish readiness panel.

Expected: publish readiness, blockers, required evidence, and confirmation state are visible.

What is happening: React renders backend publish gate data.

Why this matters: publish decisions remain server-owned.

11. Inspect the sharing panel.

Expected: sharing status and action state are visible without cross-tenant labels.

What is happening: React reads the sharing summary field from the backend envelope.

Why this matters: visibility remains fail-closed and not browser-only.

12. Inspect revision history.

Expected: revisions are listed with safe summaries.

What is happening: React renders revision data from the workflow envelope.

Why this matters: the old revision template is deleted.

13. Inspect published version detail.

Expected: published version title, version label, and digest label are visible.

What is happening: React renders `version_detail`.

Why this matters: the old version detail template is deleted.

14. Navigate directly to `http://127.0.0.1:8000/admin/app/workflows/new`.

Expected: the React host loads and the create panel remains available.

What is happening: the SPA fallback accepts the workflow child route.

Why this matters: direct create links survive page refresh.

15. Navigate directly to `http://127.0.0.1:8000/admin/app/workflows/drafts/00000000-0000-0000-0000-000000000030`.

Expected: the React host loads with workflow content or a safe unavailable state.

What is happening: React child routes use the same host and backend JSON guardrails.

Why this matters: draft bookmarks recover without Jinja.

16. Navigate to `http://127.0.0.1:8000/admin/workflows/ui?tenant_id=11111111-1111-1111-1111-111111111111&q=briefing`.

Expected: the browser redirects to `/admin/app/workflows` and preserves safe query intent.

What is happening: the legacy workflow route returns a redirect.

Why this matters: old workflow list bookmarks do not break.

17. Navigate to `http://127.0.0.1:8000/admin/workflows/new`.

Expected: the browser redirects to `/admin/app/workflows/new`.

What is happening: the old create route no longer renders a template.

Why this matters: `workflows/create.html` remains deleted.

18. Navigate to an old draft editor URL.

Expected: the browser redirects to `/admin/app/workflows/drafts/{id}` or shows a safe React unavailable state.

What is happening: route parameters are carried into the React path.

Why this matters: support links keep their recovery value.

19. Navigate to an old publish gate URL.

Expected: the browser redirects to `/admin/app/workflows/drafts/{id}/publish-gate`.

What is happening: publish gate context moves to React.

Why this matters: gate review no longer depends on `publish_gate.html`.

20. Navigate to an old version detail URL.

Expected: the browser redirects to `/admin/app/workflows/versions/{id}`.

What is happening: published version context moves to React.

Why this matters: version review no longer depends on `version_detail.html`.

21. Sign out through `http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login`.

Expected: the browser returns to local login.

What is happening: the local-principal cookie is cleared.

Why this matters: QA can switch principals without manual browser cleanup.

22. Sign in as `tenant-admin-acme`.

Expected: `/admin/app/workflows` loads with tenant scope.

What is happening: the active principal changes to a tenant-scoped admin.

Why this matters: tenant-scoped workflow authors must have the same React route.

23. Try a Globex tenant URL as the Acme principal.

Expected: the page denies access or shows unavailable state without Globex workflow details.

What is happening: backend authorization rejects cross-tenant scope.

Why this matters: React parity cannot weaken tenant isolation.

24. Inspect the page source for Jinja markers.

Expected: no `{%`, `{{`, `templates/workflows`, or workflow template names appear.

What is happening: browser HTML is generated by the non-Jinja host renderer.

Why this matters: deleted workflow templates are not silently still required.

## Required Automated Evidence

Run lint.

```bash
uv run ruff check .
```

Expected: pass.

Run format check.

```bash
uv run ruff format --check .
```

Expected: pass.

Run mypy.

```bash
uv run mypy src
```

Expected: pass.

Run full coverage.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: pass.

Run focused backend workflow tests.

```bash
uv run pytest --no-cov tests/integration/api/test_admin_workflow_ui.py tests/unit/api/test_admin_workflow_ui_routes.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py -q
```

Expected: pass.

Run frontend workflow tests.

```bash
cd frontend/admin && npm test -- --run src/App.test.tsx src/components/workflows
```

Expected: pass.

Run Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/040-workflow-registry-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: screenshot exists at `output/playwright/qa040_ui/qa040-react-ui2-smoke.png`.

## UI Evidence Checklist

- Expected: screenshot of local login before sign-in.
- Expected: screenshot of `/admin/app/workflows` after platform-admin sign-in.
- Expected: screenshot of workflow registry panel.
- Expected: screenshot of create workflow panel.
- Expected: screenshot of draft edit form.
- Expected: screenshot of reference picker.
- Expected: screenshot of graph visual and list alternative.
- Expected: screenshot of validation panel after running validation.
- Expected: screenshot of publish readiness panel.
- Expected: screenshot of sharing summary.
- Expected: screenshot of revision history.
- Expected: screenshot of published version detail.
- Expected: reviewer note that old workflow list redirects to React.
- Expected: reviewer note that old create redirects to React.
- Expected: reviewer note that old draft, publish gate, revision, and version links redirect to React.
- Expected: reviewer note that cross-tenant denial is redaction-safe.
- Expected: reviewer note that no workflow Jinja marker appears in browser HTML.
- Expected: reviewer note that no raw secrets, raw prompts, raw completions, raw tool payloads, stack traces, or local paths appear.

## Acceptance Notes Template

- Step: Local login.
- Expected: local login lists deterministic principals.
- Actual:
- Evidence:

- Step: React workflow registry.
- Expected: workflow panels render through React.
- Actual:
- Evidence:

- Step: Old route redirect.
- Expected: old route lands on React route.
- Actual:
- Evidence:

- Step: Graph accessibility.
- Expected: visual graph and list alternative are both available.
- Actual:
- Evidence:

- Step: Publish readiness.
- Expected: server-owned readiness and evidence are visible.
- Actual:
- Evidence:

- Step: Tenant isolation.
- Expected: cross-tenant scope is denied or unavailable.
- Actual:
- Evidence:

- Step: Redaction.
- Expected: no sensitive payloads leak.
- Actual:
- Evidence:

## Troubleshooting

- If the page shows a blank screen, rebuild React assets and reload `/admin/app/workflows`.
- If local login does not show principals, confirm `.env.qa040` is copied to `.env`.
- If old workflow routes return 200 instead of 303, inspect legacy route handlers for restored template rendering.
- If graph content is missing, check the builder JSON response and frontend console.
- If validation does not update, inspect network requests to `/admin/app/workflows/drafts/{workflow_draft_id}/validate`.
- If publish readiness looks browser-owned, verify the backend envelope contains `publish_readiness`.
- If cross-tenant labels appear, stop and treat it as a security blocker.
- If screenshots contain local paths or stack traces, discard them, fix the response, and recapture evidence.

## Related Files

- `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040.md`
- `specs/040-workflow-registry-full-react-parity-and-jinja-removal/.env.qa040`
- `specs/040-workflow-registry-full-react-parity-and-jinja-removal/pr_notes.md`
- `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- `frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx`
- `frontend/admin/src/components/workflows/WorkflowRegistryPage.tsx`
- `frontend/admin/src/components/workflows/WorkflowCreatePage.tsx`
