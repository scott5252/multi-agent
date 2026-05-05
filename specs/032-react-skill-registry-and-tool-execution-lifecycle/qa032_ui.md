# QA032 UI Walkthrough

## Goal

QA032 UI validation proves the React skill lifecycle page renders safe package publication, tenant installation, credential readiness, connector diagnostics, binding preview, and audit evidence.

The route under review is `/admin/app/skills`.

The browser should show the skill lifecycle page as the first usable screen.

The browser should show sections for Publish, Discover, Installations, Diagnostics, Binding, and Audit.

The browser should show platform publication controls only for platform administrators.

The browser should show tenant discovery and installation details only for authorized tenant administrators.

The browser should show credential references as labels and fingerprints only.

The browser should show calendar, Gmail, news, weather, and commute connector readiness.

The browser should show explicit smoke-test/readiness and diagnostic actions.

The browser should show SkillExecutionGateway diagnostic summaries.

The browser should show read-only binding preview policy reasons.

The browser should show bounded lifecycle audit records.

The browser should not show raw manifests, credential values, provider tokens, authorization headers, private messages, memory contents, connector request bodies, connector response bodies, raw tool outputs, stack traces, local paths, or unauthorized tenant labels.

Expected: screenshots show only safe summaries, fingerprints, audit references, and evidence references.

Expected: no screenshot contains `qa032-secret-value`.

Expected: no screenshot contains `Globex` when signed in as an Acme tenant admin.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa032`.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, or confusing tenant scope.

Do not paste real secrets into the browser.

Do not paste raw manifests, credential values, connector request bodies, connector response bodies, tool outputs, private messages, stack traces, local paths, or cross-tenant labels into reviewer notes.

Expected: QA evidence can be shared with reviewers without cleanup.

Expected: every action is explicit and user initiated.

What is happening: the browser is exercising the same React route administrators use for skill lifecycle review.

Why this matters: UI validation catches layout, focus, and unsafe presentation issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/032-react-skill-registry-and-tool-execution-lifecycle/.env.qa032 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa032 && createdb -U postgres multi_agent_platform_qa032'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa032 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa032-artifacts output/playwright/qa032_ui
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

Expected: worker starts without live provider, Telegram, credential, or connector calls.

Open the local browser login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Expected: local login offers `platform-admin` and `tenant-admin-acme`.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/032-react-skill-registry-and-tool-execution-lifecycle
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

Run full QA032 validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml --start-processes
```

Expected: all automated commands pass before screenshots are accepted.

What is happening: the QA032 manifest resets the database, builds assets, starts app processes, and captures screenshots.

Why this matters: manual observations should match automated evidence.

## Browser Walkthrough

### Step 1: Denied Skill Lifecycle Route

Open:

```text
http://127.0.0.1:8000/admin/app/skills
```

Expected: a 401 response appears when not logged in.

Expected: no package, credential, connector, binding, or audit data appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: skill lifecycle metadata cannot leak anonymously.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-denied.png`.

### Step 2: Platform Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Choose `platform-admin`.

Expected: the browser redirects to `/admin/app/skills`.

Expected: the shell shows `React Admin`.

Expected: the page heading says `Skill lifecycle`.

Expected: the page shows `Package publication`.

Expected: the page shows `Save candidate`, `Validate`, and `Publish`.

Expected: the page shows `Immutable package versions`.

Expected: the page shows grant, quarantine, and withdrawal evidence.

What is happening: the platform principal can see package publication and lifecycle actions.

Why this matters: package creation, tenant grants, quarantine, and withdrawal are platform-only.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-platform.png`.

### Step 3: Candidate And Publication Actions

Click `Save candidate`.

Expected: the page shows `Candidate result`.

Expected: the page shows `Package candidate saved with safe manifest summary`.

Click `Validate`.

Expected: the page shows validation feedback.

Click `Publish`.

Expected: the page shows `Publish result`.

Expected: the page shows immutable publication evidence and an audit reference.

What is happening: buttons post to protected backend skill lifecycle actions.

Why this matters: React does not parse raw manifests or apply publication rules in the browser.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-publication.png`.

### Step 4: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Choose `tenant-admin-acme`.

Expected: the page shows `Skill lifecycle`.

Expected: the page does not show package publication controls.

Expected: the page shows `Granted tenant skills`.

Expected: the page shows `daily-briefing-connectors`.

Expected: the page shows `Reference readiness`.

Expected: the page shows `Connector readiness`.

What is happening: the tenant principal receives only granted package and tenant-scoped readiness data.

Why this matters: tenant administrators can operate granted skills without seeing platform package mutation controls.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-tenant.png`.

### Step 5: Credential Reference

Find `Reference readiness`.

Click `Save reference`.

Expected: the page shows `Credential result`.

Expected: the page shows `fp_qa032_acme_briefing`.

Expected: the page does not show any credential value.

What is happening: the backend accepts an authorized credential reference id and returns safe reference metadata.

Why this matters: the browser never receives resolved credentials.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-credential.png`.

### Step 6: Smoke-Test Readiness

Find `Queued readiness`.

Click `Refresh readiness`.

Expected: the page shows `Readiness result`.

Expected: the page shows `queued`.

Expected: surrounding layout does not shift.

What is happening: the backend returns queued readiness evidence.

Why this matters: smoke tests are explicit actions, not unbounded polling.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-readiness.png`.

### Step 7: Connector Diagnostic

Find `Connector readiness`.

Click `Run diagnostic`.

Expected: the page shows `Diagnostic result`.

Expected: the page shows a safe gateway diagnostic audit reference.

Expected: no connector request or response body appears.

What is happening: the backend summarizes SkillExecutionGateway evidence.

Why this matters: diagnostics explain policy without exposing connector outputs.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-diagnostics.png`.

### Step 8: Binding Preview

Find `Eligibility and diagnostics`.

Click `Preview binding`.

Expected: the page shows `Binding result`.

Expected: the page shows policy reasons and blocked tools.

Expected: no live tools, live credentials, Telegram delivery, model calls, or connector side effects occur.

What is happening: the backend evaluates binding eligibility read-only.

Why this matters: workflow builders can inspect skill readiness before runtime binding.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-binding.png`.

### Step 9: Audit Timeline

Find `Lifecycle timeline`.

Expected: the page shows package, installation, and diagnostic records.

Expected: each record has an audit reference.

Expected: safe diff summaries do not include raw manifests or credential values.

What is happening: the React page renders bounded audit records from backend contracts.

Why this matters: lifecycle changes remain reviewable and redaction-safe.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-audit.png`.

### Step 10: Cross-Tenant Check

Open while signed in as `tenant-admin-acme`:

```text
http://127.0.0.1:8000/admin/app/skills?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: access is denied.

Expected: no Globex package, installation, credential, diagnostic, or audit details appear.

What is happening: tenant scope resolution fails closed before React data renders.

Why this matters: cross-tenant leakage is a stop condition.

Screenshot evidence: `output/playwright/qa032_ui/qa032-react-skills-cross-tenant.png`.

## UI Evidence Checklist

- Screenshot for denied unauthenticated route.
- Screenshot for platform publication workspace.
- Screenshot after candidate or publish action.
- Screenshot for tenant discovery and installation.
- Screenshot after credential reference configuration.
- Screenshot after smoke-test readiness refresh.
- Screenshot after connector diagnostic refresh.
- Screenshot after binding preview.
- Screenshot for audit timeline.
- Screenshot for cross-tenant denial.
- Reviewer note that no screenshot contains `qa032-secret-value`.
- Reviewer note that no Acme screenshot contains unauthorized Globex details.

Expected: every screenshot path is recorded in `pr_notes.md`.

## Acceptance Notes Template

Record:

- Reviewer.
- Browser and viewport.
- Platform login result.
- Tenant login result.
- Candidate action result.
- Credential action result.
- Readiness action result.
- Diagnostic action result.
- Binding preview result.
- Audit timeline observation.
- Cross-tenant denial result.
- Redaction scan result.
- Layout or accessibility concerns.

Expected: unresolved layout or safety concerns are fixed before QA032 sign-off.

## Troubleshooting

- If the page stays on login, choose a local principal.
- If the platform view lacks publication controls, confirm the current principal is `platform-admin`.
- If the tenant view lacks install or credential controls, confirm the current principal is `tenant-admin-acme`.
- If a mutation fails, reload `/admin/app/skills` and retry with current revision metadata.
- If screenshots are missing, rerun Playwright with `--start-processes`.
- If unsafe text appears, stop and fix the backend schema or service before continuing.

Expected: troubleshooting does not require live credentials or external connectors.

## Related Files

- `specs/032-react-skill-registry-and-tool-execution-lifecycle/qa032.md`
- `specs/032-react-skill-registry-and-tool-execution-lifecycle/qa032_user_guide.md`
- `specs/032-react-skill-registry-and-tool-execution-lifecycle/.env.qa032`
- `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- `frontend/admin/src/test/skillLifecycleTestData.ts`
- `tests/integration/test_admin_react_routes.py`
- `output/playwright/qa032_ui`
