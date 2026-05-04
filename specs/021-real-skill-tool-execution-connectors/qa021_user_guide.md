# QA021 User Guide: Missing Feature 2 - Real Skill Tool Execution Connectors

## Detailed Overview

This guide helps a non-developer reviewer validate the Skill Tool Diagnostics feature.
The feature belongs to the Daily Intelligence Briefing scenario.
The scenario needs calendar, Gmail, news, weather, and commute information.
The platform must not let workflow nodes call those tools directly.
Instead, tool calls pass through the SkillExecutionGateway.
The gateway checks whether the tool is installed for the tenant.
The gateway checks whether the exact skill version is allowed.
The gateway checks whether the requested operation is read-only.
The gateway checks whether the outbound provider domain is allowed.
The gateway checks whether credential metadata exists for the tenant.
The gateway checks whether credential metadata belongs to the same tenant.
The gateway blocks unsafe side effects by default.
The gateway blocks live provider probes in local QA.
The gateway returns structured outputs for workflow contracts.
The gateway records only redacted request and response summaries.
The gateway does not store raw external provider payloads inline.
The diagnostics page proves the gateway can run safe mock tools.
The diagnostics page is server-rendered in the admin console.
The diagnostics page is protected by local-principal admin login.
The diagnostics page should work without real Google or Gmail credentials.
The diagnostics page should work without real news, weather, or traffic credentials.
The mock data is deterministic so screenshots can be reviewed consistently.
The expected route is `/admin/skill-execution/ui/diagnostics`.
The expected page title is `Skill Tool Diagnostics`.
The expected QA database is `multi_agent_platform_qa021`.
The expected QA env file is `specs/021-real-skill-tool-execution-connectors/.env.qa021`.
The expected screenshot folder is `output/playwright/qa021_ui`.

## Who Should Use This Guide

Use this guide if you are reviewing the Daily Briefing connector readiness page.
Use this guide if you need evidence that mock tool execution is policy governed.
Use this guide if you are checking that secrets are not displayed.
Use this guide if you are checking that tenant isolation is represented.
Use this guide if you are checking browser-visible QA evidence.
You do not need to understand Python code to complete the browser checks.
You do need access to the local development environment.
You do need the API server running on `127.0.0.1:8000`.
You do need a local-principal user called `platform-admin`.
You should not use real personal Google, Gmail, weather, news, or traffic credentials.
You should not paste production secrets into the application.
You should not change production or shared data while running this guide.

## Manual QA Prerequisites

Confirm Python 3.12 is available.
Confirm `uv` is installed.
Confirm Docker Compose is available.
Confirm the repository is checked out locally.
Confirm you are on the QA branch for Spec 021.
Confirm the current working directory is the repository root.
Confirm `.env` can be safely replaced for QA.
Back up the current `.env` file if it exists.
Copy `specs/021-real-skill-tool-execution-connectors/.env.qa021` to `.env`.
Run `uv sync` to install dependencies.
Start PostgreSQL with Docker Compose.
Reset only the QA database named `multi_agent_platform_qa021`.
Run Alembic migrations.
Create `.data/qa021-artifacts` if it does not already exist.
Create `output/playwright/qa021_ui` if it does not already exist.
Start the API server on `127.0.0.1:8000`.
Start the worker process in a second terminal if you are running full validation.
Do not reset databases named `multi_agent_platform`, `postgres`, `template0`, or `template1`.
Do not use live-provider environment variables for local QA.

## Step-by-Step Manual QA

Open a browser.
Navigate to `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/skill-execution/ui/diagnostics`.
Wait for the Local Login page.
Choose the `platform-admin` account.
Confirm the browser redirects to the admin console.
Confirm the page title reads `Skill Tool Diagnostics`.
Confirm the left navigation contains an admin console shell.
Confirm the scope selector is visible.
Confirm the main content area is not blank.
Find the `Daily Briefing Tool Readiness` table.
Confirm the table has a Tool column.
Confirm the table has a Mode column.
Confirm the table has a Readiness column.
Confirm the table has a Credential column.
Confirm the table has an Allowed Domains column.
Confirm the table has a Latest Safe Summary column.
Confirm Google Calendar Events appears in the table.
Confirm Gmail Messages appears in the table.
Confirm News Search appears in the table.
Confirm Weather Forecast appears in the table.
Confirm Commute Lookup appears in the table.
Confirm each tool shows mode `mock`.
Confirm each tool shows readiness `ready`.
Confirm each credential cell uses redacted wording.
Confirm the Google Calendar summary mentions events.
Confirm the Gmail summary mentions messages.
Confirm the News summary mentions a news item.
Confirm the Weather summary mentions a forecast.
Confirm the Commute summary mentions commute status.
Find the `Policy Decisions` table.
Confirm each tool has a status of `succeeded`.
Confirm each row lists `tool_registered`.
Confirm each row lists `skill_installed`.
Confirm each row lists `tool_policy`.
Confirm each row lists `side_effect_policy`.
Confirm each row lists `outbound_policy`.
Confirm each row lists `execution_mode`.
Confirm each row lists `credential_policy`.
Confirm each row lists `credential_tenant`.
Confirm each listed policy check is allowed.
Open `http://127.0.0.1:8000/admin/skill-execution/api/diagnostics` in the same browser session or use curl with `X-Local-Principal: platform-admin`.
Confirm the API returns JSON.
Confirm the JSON `items` array contains five records.
Confirm the JSON records use the same tool names as the page.
Confirm the JSON does not include raw secret values.
Return to the diagnostics page.
Refresh the page.
Confirm the page still renders successfully.
Capture a full-page screenshot.
Save the screenshot in `output/playwright/qa021_ui`.

## Expected Results

The login page loads without an error.
The `platform-admin` account is selectable.
The diagnostics route returns HTTP 200 after login.
The page title is `Skill Tool Diagnostics`.
All five Daily Briefing tool families are visible.
All five tool families run in mock mode.
All five tool families report ready status.
All five latest summaries are short and safe.
No external provider login is requested.
No browser popup asks for Google OAuth.
No page text includes a raw access token.
No page text includes a raw refresh token.
No page text includes an API key value.
No page text includes a password.
No page text includes raw email body text.
No page text includes sensitive URL query strings.
Policy decisions are visible for every tool.
Every policy decision shown for the mock diagnostics is allowed.
The API diagnostics endpoint returns five records.
The screenshot clearly shows the page title and the readiness table.

## Evidence To Capture

Capture the Local Login screenshot.
Capture the redirected diagnostics page screenshot.
Capture the direct diagnostics route screenshot.
Capture the API diagnostics JSON if you are doing API evidence.
Record the date and time of the validation.
Record the branch name.
Record the QA database name.
Record the browser used.
Record whether the API and worker were running.
Record any unexpected HTTP status code.
Record any visible error message.
Record whether redaction markers are visible.
Record whether any raw secret-like value appears.
Record whether all five tools are present.
Record whether all five tools show ready status.
Store screenshots under `output/playwright/qa021_ui`.
Store API notes under `.data/qa021-artifacts` when useful.

## Security And Redaction Checks

Search the page text for `secret`.
If `secret` appears only in safe explanatory labels, note it.
Search the page text for `access_token`.
Search the page text for `refresh_token`.
Search the page text for `api_key`.
Search the page text for `Bearer`.
Search the page text for `sk-`.
Search the page text for `ya29`.
Search the page text for raw email body wording.
Search the page text for provider URLs with private query strings.
Confirm credential references are redacted.
Confirm summaries are short.
Confirm summaries do not include full email bodies.
Confirm summaries do not include personal OAuth values.
Confirm denied security behavior is covered by automated tests.
Confirm local live probes are not required for manual QA.
Do not add real credentials to make the page green.

## Tenant Isolation Checks

Confirm the diagnostics request carries a tenant identifier internally.
Confirm the QA tenant is `11111111-1111-1111-1111-111111111111` when no tenant is selected.
Confirm credential metadata in QA belongs to that same tenant.
Confirm cross-tenant credential behavior is covered by automated tests.
Confirm the page does not display another tenant name as credential evidence.
Confirm the API does not expose credential metadata from another tenant.
Confirm platform-admin can view the diagnostics page.
Confirm unauthenticated users cannot view the diagnostics page.
Confirm tenant-specific validation should use a tenant-scoped principal when added.
Confirm no production tenant identifier is used in local QA.

## Troubleshooting

If the login page is empty, check `LOCAL_PRINCIPAL_CATALOG_JSON`.
If login fails, confirm `AUTH_MODE=local_principal`.
If the diagnostics page returns 401, confirm the local-principal cookie or header is set.
If the diagnostics page returns 403, confirm `skill-execution:read` is in the principal permissions.
If the diagnostics page returns 503, check database connectivity and admin audit tables.
If the page is blank, check the API server log.
If the page does not show five tools, rerun the targeted tests.
If readiness is blocked, inspect the policy decision text.
If outbound policy is denied, confirm the local QA policy bundle is being used.
If credential policy is denied, confirm the mock credential metadata exists.
If live probes are denied in local QA, that is expected.
If external provider login appears, stop and report a regression.
If raw secrets appear, stop and report a security regression.
If screenshots are missing, check the Playwright output directory.
If the worker fails to start, capture the worker log but continue browser diagnostics if the API works.
If full coverage takes a long time, run the targeted `--no-cov` command first.
If the QA database reset fails, confirm Docker Compose PostgreSQL is running.
If migrations fail, capture the Alembic output.
If the browser cannot reach the API, confirm the server uses port 8000.
If another process uses port 8000, stop it or restart the API on the expected port for validation.
If the environment was changed for QA, restore `.env.autopilot-backup` after validation.
