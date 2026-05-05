# QA031 User Guide: Spec 031 - Model, Prompt, Profile, And Provider Governance

## Detailed Overview

QA031 adds a React governance page to the admin console.

The page is designed for administrators who need to understand model provider readiness.

The page is also designed for administrators who manage prompt and profile governance.

The first screen is the usable governance workspace, not a landing page.

The page groups work into Setup, Providers, Prompts, Profiles, Routing, and Provenance.

The Setup section explains readiness at a glance.

The Providers section shows provider health and credential reference diagnostics.

The Prompts section shows prompt versions, safe summaries, and preview controls.

The Profiles section shows runtime configuration and resolver evidence.

The Routing section shows read-only model and skill policy decisions.

The Provenance section shows policy history and run evidence.

Platform administrators can run explicit provider probes.

Platform administrators can update credential references through protected backend actions.

Tenant administrators can review authorized readiness.

Tenant administrators cannot mutate provider setup.

Prompt previews use deterministic QA fixtures.

Unsafe preview fixtures are summarized before the browser renders them.

Routing previews are read-only policy evaluations.

Routing previews do not invoke live providers.

Routing previews do not invoke connector tools.

Routing previews do not contact Telegram.

Credential diagnostics show references and fingerprints only.

Credential diagnostics do not show resolved values.

The most important safety rule is simple.

No raw sensitive governance data should be visible.

Do not accept a screenshot that shows raw credentials.

Do not accept a screenshot that shows provider tokens.

Do not accept a screenshot that shows authorization headers.

Do not accept a screenshot that shows raw prompts.

Do not accept a screenshot that shows raw completions.

Do not accept a screenshot that shows memory contents.

Do not accept a screenshot that shows private channel messages.

Do not accept a screenshot that shows raw provider payloads.

Do not accept a screenshot that shows connector payloads.

Do not accept a screenshot that shows stack traces.

Do not accept a screenshot that shows local filesystem paths.

Do not accept a screenshot that shows `qa031-secret-value`.

Do not accept an Acme tenant screenshot that shows Globex data.

The expected provider name is `OpenAI primary`.

The expected prompt name is `Daily briefing prompt`.

The expected runtime profile name is `Briefing runtime profile`.

The expected routing audit reference is `audit-routing-preview-qa031`.

The expected run provenance audit reference is `audit-run-provenance-qa031`.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA031 in a browser.

Use this guide if you need a plain-language checklist.

Use this guide if you are not changing code but need to verify the feature.

Use this guide if you need to compare platform and tenant behavior.

Use this guide if you need to confirm redaction and tenant isolation.

Developers should also run `qa031.md`.

UI reviewers should also run `qa031_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes the QA environment file is `.env.qa031`.

This guide assumes Acme uses tenant ID `11111111-1111-1111-1111-111111111111`.

This guide assumes Globex uses tenant ID `22222222-2222-2222-2222-222222222222`.

## Manual QA Prerequisites

Start from the repository root.

Copy the environment file.

```bash
cp specs/031-model-prompt-profile-and-provider-governance/.env.qa031 .env
```

Install dependencies.

```bash
uv sync
```

Build the React admin bundle.

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Reset the QA031 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa031 && createdb -U postgres multi_agent_platform_qa031'
```

Run migrations.

```bash
uv run alembic upgrade head
```

Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa031 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence directories.

```bash
mkdir -p .data/qa031-artifacts output/playwright/qa031_ui
```

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Confirm the API is live.

```text
http://127.0.0.1:8000/health/live
```

Expected result: the health endpoint responds.

Expected result: local login shows `platform-admin`, `tenant-admin-acme`, and `tenant-admin-globex`.

## Step-by-Step Manual QA

Step 1: open the denied route.

```text
http://127.0.0.1:8000/admin/app/governance
```

Expected result: the route is not accessible before login.

Expected result: no governance content appears.

Step 2: open local login as platform admin.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Choose `platform-admin`.

Expected result: the browser redirects to `/admin/app/governance`.

Expected result: the shell says `React Admin`.

Expected result: the page says `Governance`.

Expected result: the active scope is platform.

Step 3: review platform setup and provider cards.

Find `Setup`.

Find `Setup and health`.

Find `OpenAI primary`.

Find `Local compatible provider`.

Expected result: provider health is summarized.

Expected result: credential references are shown as safe references.

Expected result: the `Run probe` button is visible for platform admin.

Step 4: run the platform provider probe.

Click `Run probe`.

Expected result: the page shows `Probe result`.

Expected result: the page shows `audit-governance-probe-qa031-openai-primary`.

Expected result: no provider token appears.

Step 5: review prompt governance.

Find `Versions and safe previews`.

Find `Daily briefing prompt`.

Find `Published v3`.

Find `Draft qa031`.

Expected result: prompt history is safe summary text.

Expected result: no raw prompt text appears.

Step 6: preview unsafe prompt fixture.

Click `Preview unsafe fixture`.

Expected result: the preview status is `summarized`.

Expected result: the page says `Preview was summarized`.

Expected result: no raw completion text appears.

Step 7: save prompt summary.

Click `Save summary`.

Expected result: the page shows `accepted`.

Expected result: the page shows a prompt result.

Step 8: review runtime profile.

Find `Runtime configuration`.

Find `Briefing runtime profile`.

Find `gpt-qa031-safe-route`.

Find `daily-briefing v3`.

Expected result: model, provider, prompt, and skills are shown as safe bindings.

Step 9: resolve runtime profile.

Click `Resolve`.

Expected result: the resolution preview shows `openai-primary through ModelGateway`.

Expected result: the resolution preview shows `audit-profile-resolution-qa031-briefing-runtime`.

Step 10: save runtime profile.

Click `Save profile`.

Expected result: the page shows `Runtime profile draft saved`.

Step 11: run routing preview.

Find `Read-only policy preview`.

Click `Preview routing`.

Expected result: the page shows `ModelGateway-only execution preserved`.

Expected result: the page shows `audit-routing-preview-qa031`.

Step 12: review policy history and provenance.

Find `Safe changes`.

Find `Run evidence`.

Find `Credential reference metadata was reviewed`.

Find `Credential reference fingerprint was ready`.

Expected result: provenance links runtime evidence to provider, prompt, profile, routing, credential, usage, and audit summaries.

Step 13: sign in as tenant admin.

Open local login again.

Choose `tenant-admin-acme`.

Expected result: the page still says `Governance`.

Expected result: the page shows Acme tenant scope.

Expected result: the page shows `Provider mutation is platform-admin only`.

Expected result: the tenant page does not show `Local compatible provider`.

Step 14: verify tenant prompt, profile, and routing views.

Find `Daily briefing prompt`.

Find `Runtime configuration`.

Find `Read-only policy preview`.

Expected result: tenant admin can review authorized governance evidence.

Expected result: tenant admin cannot run provider mutation actions.

Step 15: verify cross-tenant denial.

Open:

```text
http://127.0.0.1:8000/admin/app/governance?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: the Acme admin is denied.

Expected result: `Globex` does not appear.

## Expected Results

Expected result: unauthenticated users cannot see governance data.

Expected result: platform administrators can see platform provider actions.

Expected result: platform administrators can run an explicit provider probe.

Expected result: tenant administrators see authorized provider readiness.

Expected result: tenant administrators cannot mutate provider configuration.

Expected result: prompt unsafe fixture preview is summarized.

Expected result: prompt save returns `accepted`.

Expected result: profile save returns `accepted`.

Expected result: profile resolution shows `openai-primary through ModelGateway`.

Expected result: routing preview shows `ModelGateway-only execution preserved`.

Expected result: policy history shows safe summaries.

Expected result: provenance shows safe evidence references.

Expected result: Acme users cannot see Globex governance data.

Expected result: no screenshot contains `qa031-secret-value`, authorization headers, provider tokens, raw prompts, raw completions, private messages, memory contents, raw provider payloads, connector payloads, stack traces, or local filesystem paths.

## Evidence To Capture

Capture a screenshot of the denied route.

Capture a screenshot of the platform governance page after running a probe.

Capture a screenshot of the tenant governance page.

Capture a screenshot after previewing the unsafe prompt fixture.

Capture a screenshot after resolving the profile and previewing routing.

Capture a screenshot of cross-tenant denial.

Keep `/tmp/qa031-platform-dashboard.json`.

Keep `/tmp/qa031-tenant-dashboard.json`.

Keep `/tmp/qa031-provider-probe.json`.

Keep `/tmp/qa031-prompt-preview.json`.

Keep `/tmp/qa031-routing-preview.json`.

Keep `/tmp/qa031-provenance.json`.

## Security And Redaction Checks

Check every screenshot for secrets.

Check every screenshot for raw prompts.

Check every screenshot for raw completions.

Check every screenshot for provider tokens.

Check every screenshot for authorization headers.

Check every screenshot for stack traces.

Check every screenshot for local filesystem paths.

Check every JSON evidence file for `qa031-secret-value`.

Check every JSON evidence file for raw provider request or response text.

Expected result: all evidence is safe to share with reviewers.

## Tenant Isolation Checks

Use `tenant-admin-acme` for Acme review.

Use the Acme tenant ID for tenant-scoped URLs.

Use the Globex tenant ID only for denial testing.

Expected result: Acme pages show Acme scope.

Expected result: Acme pages do not show Globex labels.

Expected result: cross-tenant requests fail with a safe 403 response.

Expected result: denied responses do not render governance cards.

## Troubleshooting

If local login does not show `tenant-admin-acme`, check `LOCAL_PRINCIPAL_CATALOG_JSON` in `.env.qa031`.

If platform probe controls are missing, confirm you signed in as `platform-admin`.

If the platform probe returns 403, confirm `platform-admin` has `admin:model-providers:write`.

If the route returns 401, sign in through `/auth/local-login?redirect_to=/admin/app/governance`.

If the route returns 403 for Acme, confirm the Acme tenant row exists in `multi_agent_platform_qa031`.

If React assets are missing, rerun `cd frontend/admin && npm install && npm run build`.

If prompt preview does not update, reload the page and repeat the preview action.

If routing preview does not show audit evidence, rerun the action and check the API log.

If unsafe text appears, stop the review and treat the run as failed.

If cross-tenant data appears, stop the review and treat the run as failed.

## Final Manual Acceptance

Accept QA031 only when the page is usable on desktop and mobile widths.

Accept QA031 only when provider mutation controls are platform-only.

Accept QA031 only when tenant users can review authorized governance evidence.

Accept QA031 only when prompt preview unsafe fixtures are summarized.

Accept QA031 only when profile and routing previews stay read-only.

Accept QA031 only when policy history and provenance show safe summaries.

Accept QA031 only when no unsafe raw governance data appears anywhere in the browser.
