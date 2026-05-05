# QA031 UI Walkthrough

## Goal

QA031 UI validation proves the React governance page renders safe provider setup, credential diagnostics, prompt governance, profile resolution, routing preview, policy history, and run provenance.

The route under review is `/admin/app/governance`.

The browser should show the governance page as the first usable screen.

The browser should show sections for Setup, Providers, Prompts, Profiles, Routing, and Provenance.

The browser should show safe credential references and fingerprints.

The browser should show explicit provider probe controls only for platform administrators.

The browser should show prompt preview controls that summarize unsafe fixture output.

The browser should show runtime profile save and resolve controls.

The browser should show read-only routing preview evidence.

The browser should show policy history and provenance summaries.

The browser should not show raw credentials, provider tokens, authorization headers, raw prompts, raw completions, provider request bodies, provider response bodies, private messages, memory contents, connector payloads, stack traces, local paths, or unauthorized tenant labels.

Expected: screenshots show only safe summaries, audit references, and artifact references.

Expected: no screenshot contains `qa031-secret-value`.

Expected: no screenshot contains `Globex` when signed in as an Acme tenant admin.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa031`.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, or confusing tenant scope.

Do not paste real secrets into the browser.

Do not paste raw prompts, completions, memory contents, private messages, provider responses, connector outputs, stack traces, local paths, or cross-tenant labels into reviewer notes.

Expected: QA evidence can be shared with reviewers without cleanup.

What is happening: the browser is exercising the same React route administrators use for governance review.

Why this matters: UI validation catches layout, focus, and unsafe presentation issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/031-model-prompt-profile-and-provider-governance/.env.qa031 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa031 && createdb -U postgres multi_agent_platform_qa031'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa031 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa031-artifacts output/playwright/qa031_ui
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

Open the local browser login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Expected: local login offers `platform-admin` and `tenant-admin-acme`.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/031-model-prompt-profile-and-provider-governance
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

Run full QA031 validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml --start-processes
```

Expected: all automated commands pass before screenshots are accepted.

What is happening: the QA031 manifest resets the database, builds assets, starts app processes, and captures screenshots.

Why this matters: manual observations should match automated evidence.

## Browser Walkthrough

### Step 1: Denied Governance Route

Open:

```text
http://127.0.0.1:8000/admin/app/governance
```

Expected: a 401 response appears when not logged in.

Expected: no provider, prompt, profile, routing, history, or provenance data appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: governance metadata cannot leak anonymously.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-denied.png`.

### Step 2: Platform Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Choose `platform-admin`.

Expected: the browser redirects to `/admin/app/governance`.

Expected: the shell shows `React Admin`.

Expected: the page heading says `Governance`.

Expected: the page shows `Setup and health`.

Expected: the page shows `OpenAI primary`.

Expected: the page shows a `Run probe` button.

What is happening: the platform principal can see provider mutation actions.

Why this matters: provider configuration and probes are platform-only.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-platform.png`.

### Step 3: Run Provider Probe

Click `Run probe`.

Expected: the page shows `Probe result`.

Expected: the page shows `audit-governance-probe-qa031-openai-primary`.

Expected: the page shows safe credential diagnostics only.

What is happening: the button posts to the backend provider probe action.

Why this matters: React does not call a provider directly.

### Step 4: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Choose `tenant-admin-acme`.

Expected: the page shows `Governance`.

Expected: the page shows `OpenAI primary`.

Expected: the page shows `Provider mutation is platform-admin only`.

Expected: the page shows `Daily briefing prompt`.

Expected: the page shows `Runtime configuration`.

Expected: the page shows `Read-only policy preview`.

What is happening: the tenant principal receives read-only provider readiness and authorized prompt/profile/routing data.

Why this matters: tenant admins can review readiness without changing platform provider settings.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-tenant.png`.

### Step 5: Prompt Preview

Find `Versions and safe previews`.

Click `Preview unsafe fixture`.

Expected: the preview status changes to `summarized`.

Expected: the page shows `Preview was summarized`.

Expected: the page does not show raw prompt text.

Expected: the page does not show raw completion text.

What is happening: the backend summarizes or blocks unsafe fixture text before React renders it.

Why this matters: prompt preview is useful without leaking unsafe prompt or completion contents.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-prompt-preview.png`.

### Step 6: Profile Resolution

Find `Runtime configuration`.

Click `Resolve`.

Expected: the page shows `openai-primary through ModelGateway`.

Expected: the page shows `audit-profile-resolution-qa031-briefing-runtime`.

Click `Save profile`.

Expected: the page shows `Runtime profile draft saved`.

What is happening: the profile controls call backend save and resolution actions.

Why this matters: the browser displays resolver evidence without performing runtime routing itself.

### Step 7: Routing Preview

Find `Read-only policy preview`.

Click `Preview routing`.

Expected: the page shows `ModelGateway-only execution preserved`.

Expected: the page shows `audit-routing-preview-qa031`.

What is happening: routing preview is a read-only policy evaluation.

Why this matters: admins can understand routing choices without invoking a live provider or tool.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-profile-routing.png`.

### Step 8: Policy History And Provenance

Find `Safe changes`.

Find `Run evidence`.

Expected: the page shows `Credential reference metadata was reviewed`.

Expected: the page shows `Credential reference fingerprint was ready`.

Expected: the page shows `audit-run-provenance-qa031`.

What is happening: governance history and run provenance are safe summaries.

Why this matters: reviewer evidence is useful without exposing runtime payloads.

### Step 9: Cross-Tenant Denial

While signed in as `tenant-admin-acme`, open:

```text
http://127.0.0.1:8000/admin/app/governance?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: the page shows `cross_tenant_scope`.

Expected: the page does not show `Globex`.

Expected: the page does not show governance details.

What is happening: the active principal cannot switch to another tenant scope.

Why this matters: React route protection is only acceptable if cross-tenant failures happen before data renders.

Screenshot evidence: `output/playwright/qa031_ui/qa031-react-governance-cross-tenant.png`.

## UI Evidence Checklist

- Denied route screenshot exists.
- Platform governance screenshot exists.
- Tenant governance screenshot exists.
- Prompt preview screenshot exists.
- Profile and routing screenshot exists.
- Cross-tenant denial screenshot exists.
- Provider probe evidence is visible only for platform admin.
- Tenant provider card says provider mutation is platform-admin only.
- Prompt unsafe fixture says summarized.
- Profile resolution shows ModelGateway route evidence.
- Routing preview says no browser-side provider execution.
- Provenance uses safe evidence strings.
- No screenshot contains `qa031-secret-value`.
- No Acme screenshot contains `Globex`.
- No screenshot contains raw prompt or completion text.
- No screenshot contains local filesystem paths.

## Acceptance Notes Template

```text
QA031 UI reviewer:
Browser:
Viewport:
Denied route screenshot:
Platform screenshot:
Tenant screenshot:
Prompt preview screenshot:
Profile routing screenshot:
Cross-tenant screenshot:
Unsafe text found:
Layout concerns:
Keyboard or focus concerns:
Accepted:
```

Expected: accepted notes include screenshots and any observed UI limitations.

## Troubleshooting

If the page keeps showing `Loading governance`, confirm the API process is running.

If local login does not show `tenant-admin-acme`, check `.env.qa031`.

If platform probe is missing, sign in as `platform-admin`.

If tenant probe controls are visible, stop and treat the run as failed.

If the unsafe fixture does not summarize, rebuild assets and rerun the prompt preview.

If React assets are blank, rerun `cd frontend/admin && npm install && npm run build`.

If cross-tenant access shows governance data, stop and treat the run as failed.

Expected: troubleshooting does not require real provider, Telegram, credential, or connector calls.

## Related Files

- `specs/031-model-prompt-profile-and-provider-governance/qa031.md`
- `specs/031-model-prompt-profile-and-provider-governance/qa031_user_guide.md`
- `specs/031-model-prompt-profile-and-provider-governance/.env.qa031`
- `specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml`
- `frontend/admin/src/components/governance/GovernancePage.tsx`
- `frontend/admin/src/components/governance/ProviderGovernancePanel.tsx`
- `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`
- `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx`
- `frontend/admin/src/components/governance/RoutingPreviewPanel.tsx`
