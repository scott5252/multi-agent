# QA042 UI: Spec 042 - Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## Goal

This UI walkthrough verifies the browser experience for Spec 042.

The reviewer should confirm that skill registry and diagnostics work happens in the React admin workspace, that old skill links redirect there, and that deleted Jinja templates are not needed for package, installation, readiness, binding, diagnostics, or audit review.

Use this document even if you are not a developer.

Expected: by the end of the walkthrough, the reviewer has screenshots and notes proving React parity, redirect compatibility, role behavior, tenant isolation, stale-state recovery, diagnostics safety, and redaction.

## How To Use This Guide

Follow the sections in order.

Keep browser screenshots under `output/playwright/qa042_ui`.

Keep manual reviewer notes under `/tmp/qa042-ui-notes.md`.

Use local-principal login only.

Do not enter real provider credentials, real Telegram tokens, real Auth0 values, real connector credentials, private messages, or raw external payloads.

Expected: all UI checks are deterministic and safe to share.

What is happening: the React UI reads backend-owned skill lifecycle contracts and displays safe summaries.

Why this matters: the UI must prove parity without recreating sensitive lifecycle logic in the browser.

## Environment Setup

Copy the QA environment.

```bash
cp specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/.env.qa042 .env
```

Expected: `.env` points at `multi_agent_platform_qa042`, `.data/qa042-artifacts`, and `AUTH_MODE=local_principal`.

Install dependencies and build React assets.

```bash
uv sync
cd frontend/admin && npm run build
cd ../..
```

Expected: dependencies are ready and the React manifest references the latest admin bundle.

Start PostgreSQL and reset the QA database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa042 && createdb -U postgres multi_agent_platform_qa042'
uv run alembic upgrade head
```

Expected: the database is reset and migrations complete.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa042 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist for role and tenant-scope checks.

Start the API and worker.

```bash
mkdir -p output/playwright/qa042_ui /tmp/qa042-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa042-ui/api.log 2>&1
```

Expected: the API serves `http://127.0.0.1:8000/health/live`.

In another terminal, start the worker.

```bash
uv run python -m multi_agent_platform.workers.main > /tmp/qa042-ui/worker.log 2>&1
```

Expected: the worker runs without live provider, Telegram, credential, or connector calls.

Open the browser login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Expected: the local login page lists `platform-admin`, `tenant-admin-acme`, and other QA principals.

## Browser Walkthrough

1. Sign in as `platform-admin`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills`

Action: choose `platform-admin`.

Expected: the browser lands on `/admin/app/skills`.

What is happening: the local-principal login writes a safe local auth cookie for the platform admin.

Why this matters: package publication and tenant grant controls require platform admin authority.

2. Review the skill lifecycle landing page.

Page URL: `http://127.0.0.1:8000/admin/app/skills`

Action: capture `output/playwright/qa042_ui/manual-skills-home.png`.

Expected: the page heading is `Skill lifecycle`, and package publication, tenant discovery, installation readiness, connector diagnostics, binding preview, audit, and legacy redirect content are visible.

What is happening: the React page loads `bootstrap.json` and renders backend-owned summaries.

Why this matters: the first screen replaces the old package, installation, and diagnostics Jinja pages.

3. Review the legacy route redirects panel.

Page URL: `/admin/app/skills`

Action: inspect the `Legacy route redirects` section.

Expected: the panel lists `/admin/skill-registry/ui/packages` and `/admin/skill-execution/ui/diagnostics` with React destinations.

What is happening: the backend exposes deletion-grade compatibility evidence.

Why this matters: bookmarked old links must remain safe after template deletion.

4. Open the old package list URL.

Page URL: `http://127.0.0.1:8000/admin/skill-registry/ui/packages`

Action: paste the URL into the address bar.

Expected: the browser redirects to `/admin/app/skills/packages` or the React app route for package management.

What is happening: the old route authenticates, preserves safe query parameters, and redirects.

Why this matters: legacy direct links no longer render Jinja.

5. Review package publication controls.

Page URL: `/admin/app/skills/packages`

Action: inspect candidate source, manifest digest, safe manifest summary, validation findings, publish readiness, grant preview, and package lifecycle actions.

Expected: package data is summarized; raw manifest text is not visible.

What is happening: the UI renders `PackagePublicationWorkspace`.

Why this matters: platform admins need parity without exposing raw package payloads.

6. Trigger the candidate save action if enabled.

Page URL: `/admin/app/skills/packages`

Action: click `Save candidate` and wait for the mutation result.

Expected: the result shows an accepted status, a safe summary, and an audit reference.

What is happening: the browser posts to a React admin mutation endpoint.

Why this matters: candidate workflow stays backend-owned and idempotent.

7. Review validation and publish actions.

Page URL: `/admin/app/skills/packages`

Action: inspect validation status, publish blockers, publish confirmation, and package version details.

Expected: status labels are clear and no blocking-finding raw payload appears.

What is happening: React displays backend validation evidence.

Why this matters: immutable package publication must remain gated by backend validation.

8. Review tenant grants.

Page URL: `/admin/app/skills/packages`

Action: inspect tenant grant summary and grant action state.

Expected: Acme grant data is summarized safely and cross-tenant private data is absent.

What is happening: the UI renders `TenantSkillGrantSummary`.

Why this matters: grant review touches tenant boundaries and must stay safe.

9. Switch to `tenant-admin-acme`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-admin-acme`.

Expected: the browser lands on the tenant-scoped skill workspace.

What is happening: local login changes the active principal and tenant scope.

Why this matters: tenant install and credential controls must be scoped to Acme.

10. Review tenant discovery.

Page URL: `/admin/app/skills/available-versions?tenant_id=11111111-1111-1111-1111-111111111111`

Action: inspect available versions, install eligibility, restrictions, and empty-state copy.

Expected: discovery is readable and does not reveal Globex-only records.

What is happening: the UI renders `TenantSkillDiscovery`.

Why this matters: tenant discovery is where cross-tenant leakage would be visible.

11. Open the old tenant discovery URL.

Page URL: `/admin/skill-registry/ui/available-versions?tenant_id=11111111-1111-1111-1111-111111111111`

Action: paste the URL into the address bar.

Expected: the browser redirects to `/admin/app/skills/available-versions?tenant_id=11111111-1111-1111-1111-111111111111`.

What is happening: the old tenant route validates tenant access before redirecting.

Why this matters: redirect compatibility must not skip tenant authorization.

12. Review installation readiness.

Page URL: `/admin/app/skills/installations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: inspect installation status, exact installed version, credential readiness, smoke-test readiness, connector readiness, findings, and upgrade path.

Expected: installation data is exact and safe; no credential value is visible.

What is happening: the UI renders `TenantSkillInstallationSummary`.

Why this matters: bindings must rely on exact installed package evidence.

13. Review credential configuration.

Page URL: `/admin/app/skills/installations/install-qa032-daily-briefing/credentials?tenant_id=11111111-1111-1111-1111-111111111111`

Action: inspect credential reference options, fingerprint, readiness, policy reason, and remediation.

Expected: references are summarized; raw secret fields are absent.

What is happening: the UI renders backend-approved credential choices.

Why this matters: users should select references, not paste secrets.

14. Trigger smoke-test refresh if enabled.

Page URL: `/admin/app/skills/installations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: click the smoke-test refresh action.

Expected: the result is accepted or queued and shows safe evidence only.

What is happening: the backend records a mocked-safe readiness refresh.

Why this matters: smoke history must stay deterministic and side-effect safe.

15. Preview binding eligibility.

Page URL: `/admin/app/skills/installations?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose a profile or workflow context and trigger preview.

Expected: eligible tools, blocked tools, policy reasons, and audit reference are shown.

What is happening: the backend computes a read-only eligibility preview.

Why this matters: binding preview must not execute tools.

16. Review connector diagnostics.

Page URL: `/admin/app/skills/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111`

Action: inspect Calendar, Gmail, News, Weather, and Commute diagnostic summaries.

Expected: gateway decisions, side-effect posture, policy status, credential status, redaction summary, and remediation are visible.

What is happening: React renders SkillExecutionGateway diagnostic summaries.

Why this matters: operators need connector readiness without raw adapter payloads.

17. Refresh diagnostics explicitly.

Page URL: `/admin/app/skills/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111`

Action: click diagnostics refresh and capture `output/playwright/qa042_ui/manual-diagnostics-refresh.png`.

Expected: the result shows a safe mutation result and no live external call evidence.

What is happening: the backend runs mocked diagnostics through the gateway.

Why this matters: React must not introduce implicit connector execution.

18. Open the old diagnostics URL.

Page URL: `/admin/skill-execution/ui/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111`

Action: paste the URL into the address bar.

Expected: the browser redirects to `/admin/app/skills/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111`.

What is happening: the old diagnostics route authenticates and redirects.

Why this matters: the deleted diagnostics template is no longer needed.

19. Check cross-tenant denial.

Page URL: `/admin/skill-registry/ui/available-versions?tenant_id=22222222-2222-2222-2222-222222222222`

Action: while still signed in as `tenant-admin-acme`, paste the URL.

Expected: the browser shows a safe denied state or JSON denial and does not display `Globex`.

What is happening: the old route checks tenant access before redirect.

Why this matters: redirect compatibility must fail closed.

20. Run a visual redaction scan.

Page URL: `/admin/app/skills?tenant_id=11111111-1111-1111-1111-111111111111`

Action: search the page text for `raw manifest`, `resolved credential`, `authorization header`, `connector request`, `connector response`, `raw tool output`, and `/Users/`.

Expected: none of those strings appear.

What is happening: schemas and builders reject unsafe text before React renders it.

Why this matters: Jinja removal must not move unsafe content into React.

## Required Automated Evidence

Run the focused UI tests.

```bash
cd frontend/admin
npm test -- --run src/components/skills src/App.test.tsx
cd ../..
```

Expected: all skill component tests and app route tests pass.

Run the production React build.

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected: `tsc` and Vite complete, and the React manifest points at the built asset.

Run the backend route and retirement checks.

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_skill_registry_legacy_redirects.py \
  tests/integration/api/test_admin_skill_registry_browser_flows.py \
  tests/integration/api/test_admin_skill_execution_legacy_redirects.py \
  tests/integration/api/test_admin_skill_execution_ui.py \
  tests/unit/admin/test_skill_jinja_retirement.py
```

Expected: all focused backend tests pass.

Run the project quality commands.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all gates pass before release.

Run the Spec 042 UI validator.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: Playwright captures `output/playwright/qa042_ui/qa042-react-ui2-smoke.png`.

## UI Evidence Checklist

- `manual-skills-home.png` shows the React skill lifecycle landing page.
- `manual-diagnostics-refresh.png` shows safe diagnostics refresh evidence.
- `qa042-react-ui2-smoke.png` shows the automated React skill smoke route.
- Notes confirm `/admin/skill-registry/ui/packages` redirects to React.
- Notes confirm `/admin/skill-registry/ui/available-versions` preserves `tenant_id`.
- Notes confirm `/admin/skill-execution/ui/diagnostics` redirects to React.
- Notes confirm Acme cannot view Globex tenant labels.
- Notes confirm no raw manifest, raw credential, connector payload, or local path appears.

## Acceptance Notes Template

```text
Reviewer:
Date:
Browser:
Principal sequence: platform-admin -> tenant-admin-acme
Primary route:
Screenshots:
Legacy redirects checked:
Tenant isolation checked:
Diagnostics refresh checked:
Redaction strings checked:
Decision:
Notes:
```

Expected: every note maps to a screenshot, test log, or saved browser observation.

## Troubleshooting

- If login does not persist, confirm `.env` has `LOCAL_PRINCIPAL_COOKIE_NAME=map_local_principal`.
- If the React page is blank, rebuild assets with `cd frontend/admin && npm run build`.
- If `/admin/app/skills` returns `401`, sign in with local login or send `X-Local-Principal`.
- If tenant URLs return `403`, check the `tenant_id` belongs to the selected principal.
- If legacy URLs return old HTML, stop and inspect the relevant router before continuing.
- If diagnostics mention a live connector call, confirm `SKILL_EXECUTION_CONNECTOR_MODE=mock`.
- If redaction markers appear, preserve the screenshot and file a blocking defect.

## Related Files

- `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/qa042.md`
- `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- `src/multi_agent_platform/api/routers/admin_skill_execution.py`
- `src/multi_agent_platform/admin/skill_lifecycle.py`
- `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`
- `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.tsx`
- `tests/integration/api/test_admin_skill_registry_legacy_redirects.py`
- `tests/integration/api/test_admin_skill_execution_legacy_redirects.py`
- `output/playwright/qa042_ui/qa042-react-ui2-smoke.png`
