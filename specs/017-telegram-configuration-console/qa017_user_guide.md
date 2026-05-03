# QA017 User Guide: Telegram Configuration Console

## Detailed Overview

This guide helps non-developer reviewers validate the Telegram Configuration Console.
The console lives at `/admin/telegram`.
It is part of the existing admin shell.
It is for platform administrators and authorized tenant administrators.
It shows whether Telegram is ready for protected commands.
It shows safe provider readiness.
It shows tenant Telegram enablement.
It supports one-time Telegram link tokens.
It shows linked Telegram identities in masked form.
It shows safe webhook and delivery diagnostics.
It must not show bot tokens.
It must not show webhook secret values.
It must not show private Telegram messages.
It must not show raw prompts.
It must not show workflow run results.
It must not show data for another tenant to a tenant admin.
Local QA uses fake secrets.
Local QA does not call Telegram.
Webhook validation proves local configuration shape only.
The feature builds on the existing Telegram webhook behavior.
The feature keeps screenshots safe for review.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer.
Use this guide if you are validating tenant isolation.
Use this guide if you are validating redaction.
Use this guide if you are validating admin UI behavior.
Use this guide if you are validating local-principal login.
Use this guide if you are validating link-token behavior.
Use this guide if you are validating webhook readiness.
Use this guide if you are validating diagnostics.
You do not need a real Telegram account.
You do not need a real Telegram bot token.
You do not need production credentials.
You do need a local app and database.
You do need the QA017 environment file.
You do need access to the local browser.

## Manual QA Prerequisites

Start in the repository root.
Back up any existing `.env`.
Copy `specs/017-telegram-configuration-console/.env.qa017` to `.env`.
Run `uv sync`.
Start PostgreSQL with Docker Compose.
Reset the QA017 database only.
Do not reset production databases.
Run `uv run alembic upgrade head`.
Start the API on `127.0.0.1:8000`.
Open the local login page.
Use `platform-admin` for platform checks.
Use `tenant-admin-acme` for Acme tenant checks.
Use `tenant-admin-globex` for cross-tenant denial checks.
Keep screenshots in the QA017 evidence folder.
Check that screenshots do not contain secrets.
Check that logs do not contain secrets.
Check that JSON responses do not contain secrets.

## Step-by-Step Manual QA

Step 1: Open `/auth/local-login?redirect_to=/admin/telegram`.
Step 2: Confirm the page says `Local Login`.
Step 3: Select `platform-admin`.
Step 4: Confirm the browser lands on `/admin/telegram`.
Step 5: Confirm the page title is `Telegram Configuration`.
Step 6: Confirm the admin sidebar contains `Telegram Configuration`.
Step 7: Confirm provider readiness cards are visible.
Step 8: Confirm token reference text is a safe label.
Step 9: Confirm webhook secret text is a safe label.
Step 10: Confirm no raw secret value appears.
Step 11: Capture the first console screenshot.
Step 12: Select Acme tenant scope if the scope selector is available.
Step 13: Confirm the tenant form appears.
Step 14: Check the `Enabled` box.
Step 15: Select `/run`.
Step 16: Select `/status`.
Step 17: Enter a safe status note.
Step 18: Save the form.
Step 19: Confirm the page redirects back to the console.
Step 20: Confirm protected command readiness updates.
Step 21: Reopen the form in another tab.
Step 22: Save the form in the first tab.
Step 23: Submit the older form from the second tab.
Step 24: Confirm the stale form conflict appears.
Step 25: Confirm the current settings were not overwritten.
Step 26: Click `Validate webhook`.
Step 27: Confirm a diagnostic row appears.
Step 28: Confirm the diagnostic says no external call was performed.
Step 29: Click `Issue link token`.
Step 30: Confirm the one-time token appears.
Step 31: Capture the token only for local linking.
Step 32: Refresh the page.
Step 33: Confirm the raw token no longer appears.
Step 34: Confirm the token list shows a fingerprint.
Step 35: Simulate Telegram `/link <token>` through the local webhook.
Step 36: Refresh the console.
Step 37: Confirm a linked identity row appears.
Step 38: Confirm Telegram user id is masked.
Step 39: Confirm Telegram chat id is masked.
Step 40: Confirm private message text is absent.
Step 41: Revoke the linked identity.
Step 42: Confirm the identity status changes to revoked.
Step 43: Issue another link token.
Step 44: Revoke the pending token.
Step 45: Confirm the token status changes to revoked.
Step 46: Sign out.
Step 47: Sign in as `tenant-admin-acme`.
Step 48: Open `/admin/telegram`.
Step 49: Confirm Acme tenant scope is active.
Step 50: Confirm Acme settings are visible.
Step 51: Attempt to open Acme data as `tenant-admin-globex`.
Step 52: Confirm the request is denied.
Step 53: Confirm the denial does not reveal Acme data.
Step 54: Capture a redaction-safe screenshot.
Step 55: Run the focused automated test command.
Step 56: Run the full quality gates if this is final validation.

## Expected Results

The console loads for platform admins.
The console loads for authorized tenant admins.
Tenant users without admin permissions are denied.
Acme tenant admins see only Acme.
Globex tenant admins see only Globex.
Platform admins can inspect platform readiness.
Platform admins can select tenant scope.
Provider readiness does not show real token values.
Webhook readiness does not show secret values.
Local webhook validation does not contact Telegram.
Tenant enablement saves with a fresh revision token.
Stale forms show a conflict.
Stale forms do not overwrite current values.
One-time link tokens are shown only once.
Stored token rows show fingerprints only.
Linked identities show masked ids only.
Diagnostics show safe categories only.
Screenshots are safe to share with reviewers.
Automated tests pass.
Coverage remains at least 90 percent.

## Evidence To Capture

Capture the local login screen.
Capture the platform console screen.
Capture the tenant console screen.
Capture the stale conflict state.
Capture the webhook validation diagnostic.
Capture the link token one-time display.
Capture the token fingerprint list after refresh.
Capture the masked linked identity list.
Capture the revoked identity state.
Capture the cross-tenant denial result.
Capture terminal output for focused tests.
Capture terminal output for quality gates.
Save Playwright screenshots under `output/playwright/qa017_ui`.
Keep API response samples free of secret values.
Keep notes about any unexpected empty state.

## Security And Redaction Checks

Search the page HTML for `qa017-fake-token`.
Search the page HTML for `local-dev-secret`.
Search screenshots for raw bot token values.
Search screenshots for webhook secret values.
Search screenshots for raw Telegram user ids.
Search screenshots for raw Telegram chat ids.
Search diagnostics for private message text.
Search diagnostics for raw prompt text.
Search diagnostics for run result text.
Search logs for token-looking values.
Search JSON responses for forbidden values.
Confirm references use labels or fingerprints.
Confirm identifiers use masks.
Confirm metadata uses safe categories.
Confirm denied pages do not expose tenant data.

## Tenant Isolation Checks

Use `tenant-admin-acme` for Acme.
Use `tenant-admin-globex` for Globex.
Record the Acme tenant id.
Record the Globex tenant id.
Open Acme settings as Acme.
Open Globex settings as Globex.
Try Acme settings as Globex.
Expect `403`.
Try Globex settings as Acme.
Expect `403`.
Issue a token as Acme.
Confirm Globex cannot list it.
Create an Acme linked identity.
Confirm Globex cannot list it.
Create Acme diagnostics.
Confirm Globex cannot list them.
Check that denied responses are generic.
Check that denied responses do not include tenant names.

## Troubleshooting

If login fails, confirm `.env.qa017` was copied.
If local principals are missing, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.
If the database fails, confirm only `multi_agent_platform_qa017` is reset.
If migrations fail, run `uv run alembic upgrade head`.
If the console is denied, confirm the principal has `telegram-config:read`.
If saves are denied, confirm `telegram-config:write`.
If token actions are denied, confirm `telegram-config:tokens`.
If diagnostics are denied, confirm `telegram-config:diagnostics`.
If readiness is not ready, confirm Telegram settings exist in `.env`.
If webhook validation looks external, stop and report it.
If raw secrets appear, stop and report a security failure.
If raw Telegram ids appear, stop and report a redaction failure.
If stale conflicts do not appear, repeat with two tabs.
If screenshots contain secrets, discard and recapture after fixing the issue.
If Playwright cannot connect, confirm the API is running on port 8000.
If the worker fails, check `/tmp/qa017-worker.log`.
If the API fails, check `/tmp/qa017-api.log`.
If coverage fails, inspect missing lines for Telegram config files.
If a result is unclear, write down the route, principal, tenant id, and trace id.
