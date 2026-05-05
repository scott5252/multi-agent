# QA032 User Guide: Spec 032 - React Skill Registry And Tool Execution Lifecycle

## Detailed Overview

QA032 adds a React skill lifecycle workspace to the admin console.

The page is designed for platform administrators who publish skill packages.

The page is also designed for tenant administrators who install and configure granted skills.

The page is a usable workspace at `/admin/app/skills`, not a marketing screen.

The workspace groups skill lifecycle work into publication, discovery, installation, credentials, readiness, diagnostics, binding, and audit evidence.

Platform administrators can save package candidates.

Platform administrators can validate package candidates.

Platform administrators can publish immutable package versions.

Platform administrators can update tenant grants.

Platform administrators can quarantine packages.

Platform administrators can withdraw packages from new installations.

Tenant administrators can discover granted packages.

Tenant administrators can install or refresh granted skills.

Tenant administrators can configure authorized credential references.

Tenant administrators can refresh smoke-test readiness.

Tenant administrators can run connector diagnostics.

Tenant administrators can preview read-only binding eligibility.

Tenant administrators can review safe audit timeline records.

The expected package slug is `daily-briefing-connectors`.

The expected package version is `1.4.0`.

The expected candidate revision is `candidate-rev-qa032-current`.

The expected installation revision is `installation-rev-qa032-current`.

The expected credential fingerprint is `fp_qa032_acme_briefing`.

The expected binding audit reference is `audit-binding-preview-qa032`.

The expected gateway diagnostic audit reference is `audit-gateway-diagnostic-qa032-calendar`.

The page renders safe summaries, digests, fingerprints, status badges, evidence references, revision tokens, and audit references.

The page must not render raw manifests.

The page must not render resolved credential values.

The page must not render authorization headers.

The page must not render provider tokens.

The page must not render private channel messages.

The page must not render memory contents.

The page must not render connector request bodies.

The page must not render connector response bodies.

The page must not render raw tool outputs.

The page must not render stack traces.

The page must not render local filesystem paths.

The page must not render `qa032-secret-value`.

An Acme tenant screenshot must not show Globex lifecycle data.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA032 in a browser.

Use this guide if you are validating platform package publication.

Use this guide if you are validating tenant skill installation.

Use this guide if you need a plain-language checklist for non-developer reviewers.

Use this guide if you need to compare platform and tenant behavior.

Use this guide if you need to confirm redaction and tenant isolation.

Developers should also run `qa032.md`.

UI reviewers should also run `qa032_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes the QA environment file is `.env.qa032`.

This guide assumes Acme uses tenant ID `11111111-1111-1111-1111-111111111111`.

This guide assumes Globex uses tenant ID `22222222-2222-2222-2222-222222222222`.

## Manual QA Prerequisites

Start from the repository root.

Copy the QA032 environment file.

```bash
cp specs/032-react-skill-registry-and-tool-execution-lifecycle/.env.qa032 .env
```

Install Python dependencies.

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

Reset the QA032 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa032 && createdb -U postgres multi_agent_platform_qa032'
```

Run migrations.

```bash
uv run alembic upgrade head
```

Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa032 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence directories.

```bash
mkdir -p .data/qa032-artifacts output/playwright/qa032_ui
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
http://127.0.0.1:8000/admin/app/skills
```

Expected result: the route is not accessible before login.

Expected result: no package, credential, connector, binding, or audit data appears.

Step 2: open local login as platform admin.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
```

Choose `platform-admin`.

Expected result: the browser redirects to `/admin/app/skills`.

Expected result: the shell says `React Admin`.

Expected result: the page says `Skill lifecycle`.

Expected result: the active scope is platform.

Step 3: review platform publication.

Find `Package publication`.

Find `daily-briefing-connectors`.

Find `sha256:qa032dailybriefing`.

Find `Save candidate`.

Find `Validate`.

Find `Publish`.

Expected result: safe candidate metadata is visible.

Expected result: raw package manifest text is not visible.

Step 4: save a package candidate.

Click `Save candidate`.

Expected result: the page shows `Candidate result`.

Expected result: the result says `Package candidate saved with safe manifest summary`.

Expected result: the page shows `audit-skill-candidate-qa032`.

Step 5: validate the candidate.

Click `Validate`.

Expected result: validation status remains safe summary text.

Expected result: no raw manifest body appears.

Step 6: publish the candidate.

Click `Publish`.

Expected result: the page shows `Publish result`.

Expected result: the page shows `Immutable skill package version published`.

Expected result: the page shows `audit-skill-publish-qa032`.

Step 7: review immutable versions.

Find `Immutable package versions`.

Find `1.4.0`.

Find `validation-evidence-qa032`.

Find `smoke-evidence-qa032`.

Expected result: tenant grant impact is summarized for Acme.

Expected result: quarantine and withdrawal controls are visible for platform admin.

Step 8: update a tenant grant.

Click `Update grant`.

Expected result: the page shows `Lifecycle result`.

Expected result: the result says the tenant grant was updated with a safe availability summary.

Step 9: verify platform lifecycle controls.

Click `Quarantine`.

Expected result: the result shows a quarantined lifecycle state.

Reload the page before testing withdrawal if you need to preserve a clean screenshot.

Expected result: lifecycle controls never expose package manifest bodies.

Step 10: sign in as tenant admin.

Open local login again.

Choose `tenant-admin-acme`.

Expected result: the page says `Skill lifecycle`.

Expected result: the page shows Acme tenant scope.

Expected result: `Package publication` controls are absent.

Expected result: the page shows `Granted tenant skills`.

Step 11: review tenant discovery.

Find `daily-briefing-connectors`.

Find `Read-only briefing connector bundle`.

Find `Version`.

Find `Digest`.

Expected result: only active-tenant grant summaries appear.

Expected result: no Globex package details appear.

Step 12: install the granted skill.

Click `Install`.

Expected result: the page shows `Install result`.

Expected result: the result says the skill package was installed for the active tenant.

Expected result: the result shows `audit-installation-qa032`.

Step 13: review credential readiness.

Find `Reference readiness`.

Find `Acme briefing connector reference`.

Find `fp_qa032_acme_briefing`.

Expected result: credential options show labels, policy reasons, and fingerprints only.

Expected result: no credential value appears.

Step 14: save the credential reference.

Click `Save reference`.

Expected result: the page shows `Credential result`.

Expected result: the credential result includes `fp_qa032_acme_briefing`.

Expected result: the result does not include a resolved credential.

Step 15: refresh smoke-test readiness.

Find `Queued readiness`.

Click `Refresh readiness`.

Expected result: the page shows `Readiness result`.

Expected result: the result says `Smoke-test readiness refresh queued`.

Expected result: the queued state does not shift surrounding layout.

Step 16: review connector readiness.

Find `Connector readiness`.

Find `Calendar`.

Find `Gmail`.

Find `News`.

Find `Weather`.

Find `Commute`.

Expected result: each connector has readiness, credential, policy, smoke, and evidence information.

Expected result: connector request and response bodies are absent.

Step 17: run a connector diagnostic.

Click the `Run diagnostic` button inside the connector readiness section.

Expected result: the page shows `Diagnostic result`.

Expected result: the result references `audit-gateway-diagnostic-qa032-calendar`.

Expected result: the result summarizes SkillExecutionGateway policy evidence.

Step 18: preview binding eligibility.

Find `Eligibility and diagnostics`.

Click `Preview binding`.

Expected result: the page shows `Binding result`.

Expected result: the result says `Read-only binding eligibility preview completed`.

Expected result: eligible tools and blocked tools are explained.

Expected result: no live tools, credentials, Telegram delivery, model calls, or connector side effects occur.

Step 19: review audit timeline.

Find `Lifecycle timeline`.

Find `published_version`.

Find `configured_credentials`.

Find `diagnostic_refreshed`.

Expected result: every record has an audit reference.

Expected result: safe diff summaries do not include raw manifests or credential values.

Step 20: verify cross-tenant denial.

Open while signed in as `tenant-admin-acme`:

```text
http://127.0.0.1:8000/admin/app/skills?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: the Acme admin is denied.

Expected result: no Globex package, installation, credential, diagnostic, binding, or audit details appear.

## Expected Results

Expected result: platform admin can see package publication and lifecycle controls.

Expected result: tenant admin cannot see package publication controls.

Expected result: tenant admin can see granted tenant packages and installation actions.

Expected result: candidate actions return safe mutation summaries.

Expected result: credential actions return fingerprints and policy reasons only.

Expected result: readiness refresh is explicit and queued.

Expected result: connector diagnostics are safe summaries.

Expected result: binding preview is read-only.

Expected result: audit timeline records are bounded and redaction-safe.

Expected result: unauthenticated access fails closed.

Expected result: cross-tenant access fails closed.

Expected result: screenshots do not contain `qa032-secret-value`.

Expected result: Acme screenshots do not contain unauthorized Globex details.

## Evidence To Capture

Capture a screenshot of the denied unauthenticated route.

Capture a screenshot of the platform publication workspace.

Capture a screenshot after candidate save or publish.

Capture a screenshot of immutable package versions.

Capture a screenshot of the tenant discovery workspace.

Capture a screenshot after install.

Capture a screenshot after credential reference save.

Capture a screenshot after readiness refresh.

Capture a screenshot after connector diagnostic refresh.

Capture a screenshot after binding preview.

Capture a screenshot of the audit timeline.

Capture a screenshot of cross-tenant denial.

Record focused backend test output.

Record frontend typecheck output.

Record frontend test output.

Record frontend build output.

Record generated TypeScript drift-check output.

Record QA document validation output.

Record Spec QA output.

Record Playwright output.

Record the redaction scan output.

## Security And Redaction Checks

Reject evidence that contains `qa032-secret-value`.

Reject evidence that contains raw manifest text.

Reject evidence that contains resolved credential values.

Reject evidence that contains authorization headers.

Reject evidence that contains provider tokens.

Reject evidence that contains private messages.

Reject evidence that contains memory contents.

Reject evidence that contains connector request bodies.

Reject evidence that contains connector response bodies.

Reject evidence that contains raw tool outputs.

Reject evidence that contains stack traces.

Reject evidence that contains local filesystem paths.

Reject evidence that contains unauthorized tenant labels.

Credential references should appear as labels and fingerprints only.

Manifest data should appear as summaries and digests only.

Connector diagnostics should appear as gateway decisions and safe attempt summaries only.

Binding previews should describe policy decisions without executing tools.

## Tenant Isolation Checks

Use `platform-admin` only for platform package publication checks.

Use `tenant-admin-acme` for tenant discovery, installation, credentials, readiness, diagnostics, binding, and audit checks.

Use the Acme tenant ID when reviewing tenant-scoped routes.

Attempt the Globex tenant ID while signed in as Acme.

Expected result: the Globex route is denied.

Expected result: the denial response does not include Globex lifecycle details.

Expected result: the Acme tenant view does not include Globex labels.

Expected result: tenant grant mutation remains platform-admin only.

## Troubleshooting

If the page shows `missing local principal header or cookie`, sign in through `/auth/local-login`.

If platform publication controls are missing, confirm the selected local principal is `platform-admin`.

If tenant install controls are missing, confirm the selected local principal is `tenant-admin-acme`.

If a mutation reports `stale_conflict`, reload `/admin/app/skills` and retry with the latest revision token.

If a mutation reports `validation_error`, read the safe field errors and confirm the selected fixture or credential reference is authorized.

If the browser shows a cross-tenant denial, confirm the tenant ID in the URL belongs to the current principal.

If React assets are missing, rerun `cd frontend/admin && npm run build`.

If the API cannot start, confirm `.env.qa032` was copied to `.env`.

If migrations fail, recreate only `multi_agent_platform_qa032`.

If screenshots are missing, rerun Playwright with `--start-processes`.

If unsafe text appears, stop validation and fix the backend schema or service before continuing.

## Final Sign-Off

QA032 is complete when the React route renders for platform and tenant principals.

QA032 is complete when publication actions are platform-admin only.

QA032 is complete when tenant install, credential, readiness, diagnostic, binding, and audit actions are tenant-scoped.

QA032 is complete when generated TypeScript contracts are current.

QA032 is complete when focused backend tests pass.

QA032 is complete when frontend typecheck, tests, and build pass.

QA032 is complete when QA docs pass validation.

QA032 is complete when Spec QA passes.

QA032 is complete when Playwright validation passes.

QA032 is complete when redaction scans find no unreviewed unsafe markers.
