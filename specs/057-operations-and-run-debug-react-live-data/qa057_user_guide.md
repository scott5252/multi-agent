# QA057 User Guide: Spec 057 - Operations And Run Debug React Live Data

## Detailed Overview

Spec 057 changes the React operations workbench from deterministic QA029-style
sample content to live, repository-backed operational evidence.

The workbench is the screen operators use when they need to understand current
platform health, tenant-visible run activity, delivery retries, model gateway
attempts, tool traces, reliability pressure, and export evidence.

Before this spec, the React route could still rely on fixed rows that looked
like real incidents.

After this spec, those rows must come from the QA database, from live service
queries, or from truthful empty, denied, validation, or unavailable states.

The page under review is `/admin/app/operations`.

The JSON route under review is `/admin/app/operations.json`.

The run-debug JSON route is `/admin/app/operations/runs/{workflow_run_id}.json`.

The export route is `/admin/app/operations/export`.

QA057 seeds Acme with one live workflow run and several operational evidence
rows inside the last 60 minutes.

QA057 leaves Globex empty so reviewers can compare seeded and empty states.

The seeded Acme run id is `57000000-0000-0000-0000-000000000057`.

Expected Acme evidence includes audit timeline rows, tool trace rows, Telegram
delivery retry evidence, one gateway attempt, and one capacity snapshot.

Expected export evidence is a safe `operations-export:` reference.

The UI must never display filesystem paths, local developer paths, raw provider
payloads, raw tool results, private channel messages, raw secrets, or QA029
fixture labels.

Tenant administrators must see only their authorized tenant scope.

Platform administrators may see platform-wide health and provider diagnostics.

Acme tenant administrators must not see platform-only worker, database, object
storage, or provider fleet pressure panels.

Globex tenant administrators must not see Acme evidence.

The export action is the main browser write exercised by this QA pass.

The post-UI database verifier confirms that the browser action created an
inspection access audit row with row count, checksum, and safe artifact
reference metadata.

## Who Should Use This Guide

Use this guide if you are validating Spec 057 manually.

Use this guide if you are reviewing the QA evidence captured by automation.

Use this guide if you are checking tenant isolation for the operations
workbench.

Use this guide if you are checking whether a visible operations row is backed by
database evidence rather than a fixture.

Use this guide if you are verifying export behavior after clicking the browser
button.

You do not need production credentials.

You do not need real Auth0.

You do not need real provider credentials.

You do not need a real Telegram bot.

The QA environment uses local-principal authentication and mocked external
integration modes.

## Manual QA Prerequisites

Start from the repository root.

Confirm Docker is available.

Confirm PostgreSQL can be started with `docker compose up -d postgres`.

Confirm dependencies are synced with `uv sync`.

Confirm frontend dependencies are available under `frontend/admin`.

Use the QA env file at
`specs/057-operations-and-run-debug-react-live-data/.env.qa057`.

The QA database name is `multi_agent_platform_qa057`.

The validation scripts may drop and recreate only that QA database.

Do not point this guide at a development, staging, or production database.

Do not use real external provider, Telegram, credential, or connector calls.

Copy the QA env file to `.env` only for the local QA run.

Run Alembic migrations with `uv run alembic upgrade head`.

Seed base tenants through the validation manifest or the documented SQL command.

Seed operations evidence with `uv run python scripts/qa/seed_operations_qa057.py`.

Create the artifact root `.data/qa057-artifacts` if it does not exist.

Build the React assets with `npm run --prefix frontend/admin build`.

Start the API with
`uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.

Start the worker if you are mirroring the automated flow.

Open the app in a browser at `http://127.0.0.1:8000`.

## Step-by-Step Manual QA

Step 1: Open `/auth/local-login?redirect_to=/admin/app/operations`.

Step 2: Select `platform-admin`.

Step 3: Confirm the page title reads `Operations workbench`.

Step 4: Confirm the page indicates the last 60 minutes time range.

Step 5: Confirm the generated label says the data came from live evidence.

Step 6: Confirm the summary cards are populated from live operations evidence.

Step 7: Confirm the likely-cause area references live reliability or gateway
symptoms when seeded rows exist.

Step 8: Confirm no text contains `qa029`.

Step 9: Confirm no text contains `qa029-secret-value`.

Step 10: Confirm no text contains a local path such as `/Users/`.

Step 11: Confirm no text exposes a `file:` URL.

Step 12: Confirm no raw provider response is visible.

Step 13: Confirm no raw tool result is visible.

Step 14: Confirm no private channel message is visible.

Step 15: Review the run-debug section.

Step 16: Confirm it references workflow run `57000000` or the seeded run title.

Step 17: Confirm the timeline includes safe summaries.

Step 18: Confirm the tool evidence references the safe weather summary.

Step 19: Confirm the delivery evidence references a retry-safe Telegram
summary.

Step 20: Confirm the gateway evidence is summarized without secret values.

Step 21: Open `/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`.

Step 22: Sign in as `tenant-admin-acme` if prompted.

Step 23: Confirm the tenant page shows `Tenant live evidence`.

Step 24: Confirm the Acme page shows live operational rows.

Step 25: Confirm platform-only database pressure is hidden.

Step 26: Confirm platform-only provider fleet pressure is hidden.

Step 27: Confirm platform-only worker and queue pressure is hidden.

Step 28: Confirm the tenant page still shows safe run, tool, delivery, and
export evidence.

Step 29: Confirm tenant run-debug details do not expose `OpenAI provider`.

Step 30: Confirm tenant run-debug details do not expose `gpt-qa057-live`.

Step 31: Confirm tenant links do not expose `/admin/app/governance/providers`.

Step 32: Click `Export evidence`.

Step 33: Wait for the export panel to update.

Step 34: Confirm the export summary reads that the workbench export persisted.

Step 35: Confirm the artifact value starts with `operations-export:`.

Step 36: Confirm the row count is greater than zero.

Step 37: Confirm the redaction summary mentions protected evidence classes.

Step 38: Open `/admin/app/operations?tenant_id=22222222-2222-2222-2222-222222222222`.

Step 39: Sign in as `tenant-admin-globex` if prompted.

Step 40: Confirm Globex shows zero live operational rows.

Step 41: Confirm Globex does not show the Acme seeded run.

Step 42: Confirm Globex does not show `trace-qa057-live-run`.

Step 43: Confirm Globex does not show the Acme tool summary.

Step 44: Confirm Globex does not show the Acme delivery retry summary.

Step 45: Confirm Globex still offers truthful empty export state.

Step 46: Try an Acme principal against the Globex tenant URL.

Step 47: Confirm the response fails closed.

Step 48: Confirm the response does not mention Globex details.

Step 49: Open the seeded run-debug JSON route as Acme tenant admin.

Step 50: Confirm the JSON contains the seeded run id.

Step 51: Confirm the JSON contains safe timeline, tool, and delivery evidence.

Step 52: Confirm the tenant JSON does not contain platform-only provider or
model details.

Step 53: Run `uv run python scripts/qa/verify_operations_qa057.py`.

Step 54: Confirm the verifier prints that QA057 persistence was verified.

Step 55: Confirm the verifier prints an `operations-export:` reference.

Step 56: Capture the browser screenshot after the export panel updates.

## Expected Results

The platform operations page loads successfully.

The Acme tenant operations page loads successfully.

The Globex tenant operations page loads successfully with empty evidence.

The seeded Acme page renders live audit timeline evidence.

The seeded Acme page renders live runtime trace evidence.

The seeded Acme page renders live gateway attempt evidence.

The seeded Acme page renders live capacity snapshot evidence.

The seeded Acme export action returns `complete`.

The export artifact reference starts with `operations-export:`.

The export metadata does not expose a local path.

The export metadata does not expose a storage URL.

The post-UI verifier finds at least three Acme timeline rows.

The post-UI verifier finds zero Globex timeline rows.

The post-UI verifier finds at least two run traces.

The post-UI verifier finds one gateway attempt.

The post-UI verifier finds at least one capacity snapshot.

The post-UI verifier finds an export audit row with row count.

The post-UI verifier finds an export audit row with checksum metadata.

The post-UI verifier finds an export audit row with safe artifact reference.

Cross-tenant requests fail closed.

Unsupported range filters return validation errors.

Unsupported subsystem filters return validation errors.

No deterministic QA029 fixture text appears.

## Evidence To Capture

Capture the Playwright screenshot named `qa057-live-data-ui-api-smoke.png`.

Capture the `run_spec_qa.py` command result.

Capture the `run_playwright_ui.py` command result.

Capture the output of `scripts/qa/verify_operations_qa057.py`.

Capture the curl-test output directory `.data/curl_test_runs/qa057-after-spec`.

Capture any failure logs from `/tmp/qa057-api.log`.

Capture any failure logs from `/tmp/qa057-worker.log`.

Record the browser principal used for each screenshot.

Record whether the screenshot is platform, Acme tenant, or Globex tenant scope.

Record the safe artifact reference, not a filesystem path.

Do not capture raw secrets.

Do not capture provider authorization headers.

Do not capture private channel message payloads.

Do not capture raw prompt or completion text.

## Security And Redaction Checks

Search visible UI text for `qa029`.

Search visible UI text for `qa029-secret-value`.

Search visible UI text for `provider authorization`.

Search visible UI text for `raw provider response`.

Search visible UI text for `raw tool result`.

Search visible UI text for `private channel message`.

Search visible UI text for `telegram update payload`.

Search visible UI text for `/Users/`.

Search visible UI text for `file:`.

Any match is a regression unless it appears only in this guide or validation
documentation.

Tenant views should use safe labels such as `Model provider` when gateway
evidence is tenant-visible.

Tenant views should not expose provider fleet management links.

Tenant views should not expose internal model ids.

Export references must be opaque and safe.

## Tenant Isolation Checks

Acme seeded evidence belongs to tenant
`11111111-1111-1111-1111-111111111111`.

Globex empty evidence belongs to tenant
`22222222-2222-2222-2222-222222222222`.

Acme tenant admin can see Acme live evidence.

Globex tenant admin can see Globex empty state.

Acme tenant admin cannot read the Globex operations page.

Globex tenant admin cannot read the Acme operations page.

Platform admin can read platform-wide operations state.

Platform-only panels must not appear in tenant scope.

Tenant run-debug links must stay scoped to the tenant.

Tenant export actions must persist tenant-scoped audit metadata.

Cross-tenant failure responses must not include tenant display names from the
denied scope.

## Troubleshooting

If the page does not load, check that the API process is running on port 8000.

If login does not show local principals, confirm `AUTH_MODE=local_principal`.

If the page says assets are missing, rebuild with
`npm run --prefix frontend/admin build`.

If the database has no seeded rows, rerun
`uv run python scripts/qa/seed_operations_qa057.py`.

If the verifier cannot connect, confirm `.env` points to
`multi_agent_platform_qa057`.

If the verifier cannot find an export row, click `Export evidence` again.

If the export action fails, check that the local principal has
`operations:export`.

If a cross-tenant request returns live data, stop the QA pass and report a
tenant isolation blocker.

If provider or model details appear in tenant JSON, stop the QA pass and report
a redaction blocker.

If `run_spec_qa.py` fails during quality gates, fix the active spec and rerun
the failed command plus downstream validation.

If Playwright cannot find the export button, confirm the workbench route loaded
after login and that the browser is on `/admin/app/operations`.

If curl validation fails after Spec 057, keep `queue.json` pointing at `057`
until the failure is diagnosed and resolved.
