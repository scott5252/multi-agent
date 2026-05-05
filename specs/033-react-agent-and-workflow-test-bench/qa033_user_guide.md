# QA033 User Guide: Spec 033 - React Agent And Workflow Test Bench

## Detailed Overview

QA033 adds a React test bench workspace to the admin console.

The page is designed for tenant administrators who need release confidence for agent and workflow changes.

The page is also designed for platform reviewers who need safe evidence for workflow publish gates.

The page is a usable workspace at `/admin/app/test-bench`, not a marketing screen.

The workspace groups test bench work into suites, cases, assertions, target binding, safe execution modes, runs, diagnostics, artifacts, publish gates, and audit evidence.

Administrators can review the current test suite list.

Administrators can save a suite with a current revision token.

Administrators can save a case with structured assertions.

Administrators can bind a suite to an authorized workflow draft revision.

Administrators can choose mock model and tool execution.

Administrators can choose side-effect-disabled gateway execution.

Administrators can see that live dependency probes are denied in local QA.

Administrators can launch deterministic QA runs.

Administrators can review queued, running, passed, failed, stale, denied, and unavailable states from the backend.

Administrators can inspect assertion diagnostics.

Administrators can inspect safe trace step summaries.

Administrators can inspect artifact metadata references.

Administrators can refresh required publish gate evidence.

Administrators can review audit timeline records.

The expected suite is `Daily briefing release gate`.

The expected suite ID is `suite-qa033-daily-briefing`.

The expected suite revision is `suite-rev-qa033-current`.

The expected target revision is `workflow-draft-rev-qa033-current`.

The expected default safe mode is `mock_model_tools`.

The expected failed run is `run-qa033-failing`.

The expected passing run is `run-qa033-passing`.

The expected artifact reference is `artifact-qa033-summary`.

The expected gate audit reference after refresh is `audit-gate-qa033-passed`.

The page renders safe summaries, status badges, evidence references, revision tokens, artifact metadata, and audit references.

The page must not render raw prompts.

The page must not render raw completions.

The page must not render raw transcripts.

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

The page must not render artifact storage paths.

The page must not render `qa033-secret-value`.

An Acme tenant screenshot must not show Globex test bench data.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA033 in a browser.

Use this guide if you are validating suite authoring.

Use this guide if you are validating deterministic run launch.

Use this guide if you are validating publish gate evidence.

Use this guide if you are validating artifact metadata.

Use this guide if you are validating governance audit evidence.

Use this guide if you need a plain-language checklist for non-developer reviewers.

Use this guide if you need to compare tenant and platform behavior.

Use this guide if you need to confirm redaction and tenant isolation.

Developers should also run `qa033.md`.

UI reviewers should also run `qa033_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes the QA environment file is `.env.qa033`.

This guide assumes Acme uses tenant ID `11111111-1111-1111-1111-111111111111`.

This guide assumes Globex uses tenant ID `22222222-2222-2222-2222-222222222222`.

## Manual QA Prerequisites

Start from the repository root.

Copy the QA033 environment file.

```bash
cp specs/033-react-agent-and-workflow-test-bench/.env.qa033 .env
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

Reset the QA033 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa033 && createdb -U postgres multi_agent_platform_qa033'
```

Run migrations.

```bash
uv run alembic upgrade head
```

Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa033 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence directories.

```bash
mkdir -p .data/qa033-artifacts output/playwright/qa033_ui
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
http://127.0.0.1:8000/admin/app/test-bench
```

Expected result: the route is not accessible before login.

Expected result: no suite, run, trace, artifact, gate, or audit data appears.

Step 2: open local login as the Acme tenant administrator.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Choose `tenant-admin-acme`.

Expected result: the browser redirects to `/admin/app/test-bench`.

Expected result: the shell says `React Admin`.

Expected result: the page says `Test Bench`.

Expected result: the active scope is Acme.

Step 3: review the dashboard.

Find `Release confidence`.

Find `Daily briefing release gate`.

Find `Reusable suites`.

Find the stale publish gate alert.

Expected result: dashboard cards summarize suite, run, and gate state.

Expected result: no fake secret value appears.

Step 4: review the suite list.

Find `Daily briefing release gate`.

Find `mock_model_tools`.

Find the current target revision.

Expected result: suite status and latest run status are visible.

Expected result: target binding is shown as a backend-provided summary.

Step 5: save the suite.

Click `Save suite`.

Expected result: the page shows `audit-test-suite-save-qa033`.

Expected result: the saved suite remains tied to the current target revision.

Step 6: save a case.

Click `Save case`.

Expected result: the page shows `audit-test-case-save-qa033`.

Expected result: the page shows structured assertion descriptors.

Expected result: raw fixture bodies do not appear.

Step 7: review assertion and target metadata.

Find `Target binding`.

Find `workflow-draft-rev-qa033-current`.

Find assertion threshold information.

Expected result: threshold values are bounded and readable.

Expected result: React does not evaluate assertions locally.

Step 8: review safe execution modes.

Find `Mock model and tools`.

Find `Side-effect-disabled gateway`.

Find the local denial for live dependency probes.

Expected result: mock mode is the default local validation mode.

Expected result: side-effect-disabled gateway mode remains explicit.

Step 9: launch a run.

Click `Launch run`.

Expected result: the page shows `audit-test-run-launch-qa033`.

Expected result: the page shows run progress from the backend.

Expected result: no real provider, Telegram, credential, or connector call occurs.

Step 10: review recent runs.

Find `run-qa033-failing`.

Find `run-qa033-passing`.

Expected result: recent runs show safe mode, actor, pass rate, and audit reference.

Expected result: run status comes from the backend contract.

Step 11: review run detail.

Find `Blocked side-effect assertion failed`.

Find usage and latency summaries.

Find evaluator and gateway decision summaries.

Expected result: failures are actionable without raw prompts or completions.

Step 12: review trace and artifact evidence.

Find safe trace step summaries.

Find `artifact-qa033-summary`.

Find checksum and retention metadata.

Expected result: artifact evidence is metadata only.

Expected result: no local path or artifact storage path appears.

Step 13: refresh publish gate evidence.

Click `Refresh evidence`.

Expected result: the page shows `Publish-gate evidence is current for the selected target revision`.

Expected result: stale evidence remediation remains visible.

Step 14: review the audit timeline.

Find `Audit timeline`.

Find actor summaries.

Find safe diff summaries.

Find denied access evidence.

Expected result: audit records are bounded and safe.

Expected result: denied access summaries do not reveal resource details.

Step 15: review cross-tenant behavior.

Open local login again.

Choose `tenant-admin-globex`.

Expected result: Globex does not see Acme-only run or artifact evidence.

Expected result: an Acme screenshot does not contain Globex data.

## Expected Results

The test bench page loads through the React admin shell.

The page uses `/admin/app/test-bench/bootstrap.json`.

The page shows suite authoring controls.

The page shows case authoring controls.

The page shows target revision binding.

The page shows safe mode choices.

The page shows run launch results.

The page shows run progress.

The page shows diagnostic findings.

The page shows trace summaries.

The page shows artifact references.

The page shows publish gate evidence.

The page shows audit records.

The page shows stale evidence remediation.

The page never exposes raw prompts.

The page never exposes raw completions.

The page never exposes credential values.

The page never exposes connector payloads.

The page never exposes local paths.

The page never exposes cross-tenant labels in the wrong tenant view.

## Evidence To Capture

Capture a denied-route screenshot.

Capture an Acme tenant dashboard screenshot.

Capture a suite save result screenshot.

Capture a case save result screenshot.

Capture a run launch result screenshot.

Capture a run detail screenshot.

Capture a trace and artifact screenshot.

Capture a publish gate screenshot.

Capture an audit timeline screenshot.

Capture a cross-tenant screenshot.

Save API dashboard JSON to `/tmp/qa033-tenant-test-bench.json`.

Save run detail JSON to `/tmp/qa033-run-detail.json`.

Save gate evidence JSON to `/tmp/qa033-gates.json`.

Run the redaction scan.

Record every screenshot path.

Record every failed observation.

Record whether every automated command passed.

## Security And Redaction Checks

Search screenshots for `qa033-secret-value`.

Search screenshots for raw prompt text.

Search screenshots for raw completion text.

Search screenshots for raw transcript text.

Search screenshots for credential values.

Search screenshots for authorization headers.

Search screenshots for provider tokens.

Search screenshots for connector request bodies.

Search screenshots for connector response bodies.

Search screenshots for raw tool outputs.

Search screenshots for stack traces.

Search screenshots for local filesystem paths.

Search screenshots for artifact storage paths.

Search Acme screenshots for Globex data.

Expected result: every search is clean.

Expected result: all sensitive evidence is summarized or referenced.

## Tenant Isolation Checks

Use `tenant-admin-acme` for the main walkthrough.

Confirm the active scope says Acme.

Confirm Acme can see the Daily briefing release gate fixture.

Confirm Acme sees Acme-scoped audit summaries.

Use `tenant-admin-globex` for the cross-tenant review.

Confirm the active scope changes.

Confirm Globex does not see Acme-only run details.

Confirm Globex does not see Acme-only artifact references.

Confirm unauthorized resource detail is summarized safely.

Expected result: every contract fails closed for the wrong tenant.

Expected result: tenant labels are safe and scoped.

## Troubleshooting

If local login is missing, confirm `.env.qa033` was copied before starting the API.

If the page cannot load assets, run `cd frontend/admin && npm run build`.

If the route returns 401, sign in again through local login.

If the route returns 403, use `tenant-admin-acme` or `platform-admin`.

If the dashboard request fails, confirm the API is running on port 8000.

If the worker logs show live provider attempts, stop and treat it as a regression.

If run launch is denied for live dependency probe mode, that is expected.

If run launch is denied for mock mode, verify the payload uses `mock_model_tools`.

If publish gate refresh is stale, reload the page and use the current target revision.

If QA document validation fails, confirm `qa033.md`, `qa033_ui.md`, and `.env.qa033` exist.

If Playwright screenshots are blank, confirm the React build completed.

If redaction scan finds unsafe output, stop and file a defect before approving QA033.
