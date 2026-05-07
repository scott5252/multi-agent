# QA042 User Guide: Spec 042 - Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## Detailed Overview

Spec 042 moves the skill registry and SkillExecutionGateway diagnostics browser experience into the React admin workspace.

The primary route is `/admin/app/skills`.

Platform administrators use this workspace to review package candidates, validation evidence, immutable versions, tenant grants, lifecycle actions, legacy redirects, and audit evidence.

Tenant administrators use this workspace to review available package versions, installed skills, credential references, smoke-test readiness, connector readiness, binding eligibility, and audit evidence.

Operators use the diagnostics area to review SkillExecutionGateway behavior for read-only Daily Briefing connector tools.

Old `/admin/skill-registry/ui/*` browser links are still accepted.

Old skill registry browser links redirect to React routes or return safe non-Jinja problems.

Old `/admin/skill-execution/ui/diagnostics` redirects to `/admin/app/skills/diagnostics`.

The old skill registry templates are deleted.

The old diagnostics template is deleted.

The React workspace is backed by backend-owned contracts.

The browser does not decide tenant access.

The browser does not decide package publication gates.

The browser does not decide credential readiness.

The browser does not execute connectors implicitly.

All mutation actions route through FastAPI handlers.

All old compatibility form posts still use backend behavior before redirecting to React.

Raw manifests must not be rendered after submission.

Raw credential values must not be rendered.

Raw connector requests must not be rendered.

Raw connector responses must not be rendered.

Authorization headers must not be rendered.

Local filesystem paths must not be rendered.

Unauthorized tenant labels must not be rendered.

The local QA environment uses deterministic local-principal authentication.

The local QA environment uses fake secret references.

The local QA environment uses mocked connector diagnostics.

The local QA environment blocks live provider probes.

The local QA environment blocks live Telegram delivery.

The local QA environment blocks external connector calls.

Use `platform-admin` for platform package checks.

Use `tenant-admin-acme` for tenant-scoped installation checks.

Use `tenant-admin-globex` only for cross-tenant isolation checks.

Use `tenant-user-acme` to confirm protected mutation controls are not available to low-privilege users.

Use `/admin/app/skills/bootstrap.json` when you need to inspect the full React skill contract.

Use `/admin/app/skills/discovery.json` when you need tenant discovery evidence.

Use `/admin/app/skills/installations.json` when you need tenant installation evidence.

Use `/admin/app/skills/diagnostics.json` when you need diagnostics evidence.

Use `/admin/app/skills/legacy-routes.json` when you need redirect evidence.

Use `/admin/skill-execution/api/diagnostics` for the retained diagnostics JSON API.

Use `/admin/skill-execution/api/diagnostics/run` for explicit diagnostics refresh API checks.

Do not rely on old Jinja pages as the source of truth.

Do not recreate the deleted templates.

Do not enter real credentials.

Do not enter production package manifests.

Do not run live connector probes.

Do not use production tenants.

Do not save evidence that contains secrets.

## Step-by-Step Manual QA

1. Copy the QA environment file.

Command:

```bash
cp specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/.env.qa042 .env
```

Expected: `.env` uses `AUTH_MODE=local_principal` and `multi_agent_platform_qa042`.

2. Install dependencies and build React assets.

Command:

```bash
uv sync
cd frontend/admin && npm run build
cd ../..
```

Expected: Vite writes the React manifest under `src/multi_agent_platform/web_admin/static/react`.

3. Start PostgreSQL.

Command:

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL container is healthy.

4. Reset only the QA database.

Command:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa042 && createdb -U postgres multi_agent_platform_qa042'
```

Expected: no non-QA database is changed.

5. Apply migrations.

Command:

```bash
uv run alembic upgrade head
```

Expected: migrations finish successfully.

6. Seed Acme and Globex tenants.

Command:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa042 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: both tenants exist.

7. Start the API.

Command:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns successfully.

8. Open the local login page.

URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Expected: the login page lists QA principals.

9. Sign in as `platform-admin`.

Expected: the browser lands on `/admin/app/skills`.

10. Review the top-level skill lifecycle page.

Expected: the page heading is `Skill lifecycle`.

Expected: package publication evidence is visible.

Expected: tenant discovery evidence is visible.

Expected: connector diagnostics evidence is visible.

Expected: audit evidence is visible.

Expected: `Legacy route redirects` is visible.

11. Review package publication.

Expected: candidate source, manifest digest, validation status, publish readiness, tenant grant preview, and audit reference are visible.

Expected: raw manifest text is not visible.

12. Click `Save candidate` if the action is enabled.

Expected: the mutation result shows accepted status and an audit reference.

Expected: no raw submitted manifest appears.

13. Review package lifecycle actions.

Expected: quarantine, withdrawal, and grant controls are represented through safe backend-owned state.

Expected: platform-only controls are not shown to tenant-only users.

14. Paste the old package list route.

URL:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages
```

Expected: the browser redirects to a React skills route.

Expected: no old package list template renders.

15. Paste an old package candidate route.

URL:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages/calendar-assistant/candidate
```

Expected: the browser redirects to `/admin/app/skills/packages/calendar-assistant/candidate`.

16. Switch to `tenant-admin-acme`.

URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the browser lands on the Acme-scoped skills workspace.

17. Review tenant discovery.

Expected: available-version cards or a safe empty state are visible.

Expected: Globex-only details are not visible.

18. Review installed skills.

Expected: exact package slug, installed version, installation revision, credential readiness, smoke readiness, connector readiness, findings, and audit reference are visible.

Expected: raw credential values are not visible.

19. Review credential references.

Expected: options show safe labels, source type, readiness, fingerprint, policy reason, and remediation.

Expected: no raw secret-entry field appears.

20. Review smoke-test readiness.

Expected: refresh is an explicit action.

Expected: safe status and evidence summary are visible.

21. Review binding eligibility.

Expected: eligible tools, blocked tools, policy reasons, missing requirements, remediation, and audit reference are visible.

Expected: no tool executes while previewing eligibility.

22. Open diagnostics.

URL:

```text
http://127.0.0.1:8000/admin/app/skills/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: Calendar, Gmail, News, Weather, and Commute diagnostics are visible.

Expected: gateway decisions and side-effect posture are visible.

Expected: connector payloads are not visible.

23. Click diagnostics refresh.

Expected: the refresh result is safe and mocked.

Expected: no live external connector call is shown.

24. Paste the old diagnostics URL.

URL:

```text
http://127.0.0.1:8000/admin/skill-execution/ui/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the browser redirects to `/admin/app/skills/diagnostics`.

25. Check cross-tenant denial.

URL:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/available-versions?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: while signed in as `tenant-admin-acme`, the response is denied safely.

Expected: the page or response does not reveal Globex records.

26. Capture screenshots.

Expected: save skill home, package review, tenant installation, diagnostics, and redirect evidence screenshots under `output/playwright/qa042_ui`.

27. Run the focused backend tests.

Command:

```bash
uv run pytest --no-cov tests/integration/api/test_admin_skill_registry_legacy_redirects.py tests/integration/api/test_admin_skill_registry_browser_flows.py tests/integration/api/test_admin_skill_execution_legacy_redirects.py tests/integration/api/test_admin_skill_execution_ui.py tests/unit/admin/test_skill_jinja_retirement.py
```

Expected: all tests pass.

28. Run the focused frontend tests.

Command:

```bash
cd frontend/admin && npm test -- --run src/components/skills src/App.test.tsx
```

Expected: all tests pass.

29. Run the Spec 042 validators.

Command:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: both validators pass.

## Expected Results

The React skill workspace loads for platform administrators.

The React skill workspace loads for tenant administrators.

The old package list URL redirects to React.

The old package detail URL redirects to React.

The old candidate URL redirects to React.

The old version URL redirects to React.

The old grant URL redirects to React.

The old available-version URL redirects to React after tenant authorization.

The old installation list URL redirects to React after tenant authorization.

The old installation detail URL redirects to React.

The old credential URL redirects to React.

The old smoke-test action redirects to React.

The old eligibility-preview action redirects to React.

The old diagnostics URL redirects to React.

Invalid old form submissions return safe JSON problems.

Valid old form submissions execute backend behavior.

Valid old form submissions redirect to React destinations.

Stale candidate revision actions redirect with a stale conflict marker.

Stale credential revision actions redirect with a stale conflict marker.

Stale smoke-test actions redirect with a stale conflict marker.

Stale eligibility preview actions redirect with a stale conflict marker.

Cross-tenant tenant discovery is denied.

Cross-tenant credential changes are denied.

React payloads contain safe summaries.

React payloads contain fingerprints when appropriate.

React payloads contain audit references.

React payloads contain artifact references.

React payloads do not contain raw manifests.

React payloads do not contain raw credentials.

React payloads do not contain authorization headers.

React payloads do not contain connector requests.

React payloads do not contain connector responses.

React payloads do not contain raw tool outputs.

React payloads do not contain local filesystem paths.

Deleted skill registry templates remain absent.

Deleted diagnostics template remains absent.

Router scanners find no skill `TemplateResponse` calls.

Playwright captures `output/playwright/qa042_ui/qa042-react-ui2-smoke.png`.

## Troubleshooting

If the login page does not show QA principals, confirm `.env` was copied from `.env.qa042`.

If login does not persist, confirm `LOCAL_PRINCIPAL_COOKIE_NAME=map_local_principal`.

If `/admin/app/skills` returns `401`, sign in through local login again.

If a tenant URL returns `403`, confirm the `tenant_id` matches the selected principal.

If React assets are missing, run `cd frontend/admin && npm run build`.

If a legacy route renders old HTML, stop and inspect the matching router.

If old package form posts fail unexpectedly, run `tests/integration/api/test_admin_skill_registry_browser_flows.py`.

If diagnostics are empty, confirm `SKILL_EXECUTION_CONNECTOR_MODE=mock`.

If diagnostics mention live calls, confirm `ALLOW_EXTERNAL_CONNECTORS=false`.

If raw manifest text appears, preserve the screenshot and treat it as a blocking redaction issue.

If raw credential values appear, preserve the screenshot and treat it as a blocking security issue.

If Globex data appears while signed in as Acme, preserve the evidence and treat it as a tenant isolation blocker.

If Playwright cannot authenticate, confirm the validation manifest uses `/auth/local-login` and `platform-admin`.

If QA database reset fails, confirm Docker PostgreSQL is running.

If full coverage takes too long during a manual review, run focused tests first and record the full coverage gate owner.

If Vite reports a large chunk warning, record it as a non-blocking warning unless the build fails.

If generated types are stale, run `uv run python scripts/frontend/generate_admin_react_types.py`.

If generated assets are stale, run `cd frontend/admin && npm run build`.

If the QA guide validator fails, update `qa042.md`, `qa042_ui.md`, and `.env.qa042` before proceeding.

If Spec QA fails after a code change, fix only Spec 042 scope before rerunning.
