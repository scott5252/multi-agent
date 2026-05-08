# QA051 User Guide: Spec 051 - Governance React Live Data

## Detailed Overview

This guide is for non-developer QA reviewers.

QA051 checks the Governance area of the React admin app.

The Governance area helps reviewers inspect model providers, prompt library records, runtime profiles, routing previews, policy history, and run provenance.

Before this change, the Governance page could rely on deterministic demonstration rows.

QA051 changes that expectation.

The page must now show records that exist in the database.

When records do not exist, the page must say so clearly.

The page must not invent a provider, prompt, profile, policy, or run.

The page must not move fake rows from the backend into the frontend.

The page must not hide fixed rows behind a new service name.

The QA run creates one safe prompt record.

That prompt is named `QA051 Governance Prompt`.

The prompt is created by a QA setup command.

The prompt exists in the QA database before the browser opens.

The browser should show that prompt.

The browser should allow a `Save summary` action.

The save action should create a new prompt draft revision.

The save action should return a safe success message.

The save action should not show the prompt template body.

The save action should not show any completion text.

The redaction preview should show summarized output.

The redaction preview should explain that protected prompt content is summarized.

The browser should also show empty provider or profile panels when the QA database has no provider or profile records.

An empty panel is acceptable.

A fake passing provider, fake profile, fake routing decision, or fake provenance row is not acceptable.

The cross-tenant check is important.

Acme owns the seeded QA prompt.

Globex must not see the Acme prompt.

If Globex can see the prompt, stop the QA run.

If any raw secret appears, stop the QA run.

If any raw prompt body appears, stop the QA run.

If any raw completion appears, stop the QA run.

If a local file path appears in the browser, stop the QA run.

The expected result is boring in the best way: live data when it exists, honest empty states when it does not, and safe summaries everywhere.

## Who Should Use This Guide

Use this guide if you are reviewing QA051 manually.

Use this guide if you need to confirm browser behavior after automated tests pass.

Use this guide if you want to compare the UI with the API evidence.

Use this guide if you are checking tenant isolation.

Use this guide if you are checking redaction.

You do not need to know the database schema.

You do need terminal access to run the listed setup and verification commands.

You do need a local browser.

You do need Docker running for PostgreSQL.

You do need the repository dependencies installed through `uv sync`.

You do need the React assets built before browser review.

Do not use this guide against a shared or production database.

Do not use a real provider credential.

Do not enable live provider probes.

Do not enable live Telegram delivery.

Do not enable external connector calls.

Keep the review local.

Keep the evidence safe.

Keep screenshots limited to the QA app.

## Manual QA Prerequisites

Start from the repository root.

Copy the QA environment.

Run `cp specs/051-governance-react-live-data/.env.qa051 .env`.

Run `uv sync`.

Start PostgreSQL with Docker Compose.

Drop and recreate only `multi_agent_platform_qa051`.

Run Alembic migrations.

Seed Acme and Globex tenant rows.

Run `uv run python scripts/qa/seed_governance_qa051.py`.

Build the React assets with `npm run --prefix frontend/admin build`.

Start the API on `127.0.0.1:8000`.

Open the local login page.

Use only the local principal choices shown by the app.

Prepare a folder or notes file for screenshots.

Use `/tmp/qa051-ui-post-api-notes.txt` for written notes.

Use `output/playwright/qa051_ui` for automated screenshot evidence.

Confirm `.env` contains `APP_NAME=multi-agent-platform-qa051`.

Confirm `.env` contains `AUTH_MODE=local_principal`.

Confirm `.env` contains `multi_agent_platform_qa051`.

Confirm `.env` contains `.data/qa051-artifacts`.

Confirm `.env` does not contain production references.

Confirm `.env` does not contain credential values.

Confirm `.env` uses `qa051/` for secret references.

If any prerequisite fails, fix the environment before opening the browser.

## Step-by-Step Manual QA

Step 1: Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance`.

Step 2: Select `platform-admin`.

Step 3: Confirm the page title says `Governance`.

Step 4: Save a screenshot named `/tmp/qa051-ui-login.png`.

Step 5: Look for `QA051 Governance Prompt`.

Step 6: Confirm the prompt card includes safe summary language.

Step 7: Confirm the prompt card has a `Save summary` button.

Step 8: Confirm the prompt card has preview buttons.

Step 9: Confirm empty provider or profile panels are written as empty states if no records exist.

Step 10: Confirm the page does not show fixed qa031 governance labels.

Step 11: Click `Save summary`.

Step 12: Wait for the result section to appear.

Step 13: Confirm the result says the prompt draft summary was saved.

Step 14: Save a screenshot named `/tmp/qa051-ui-prompt-save.png`.

Step 15: Click `Preview redaction check`.

Step 16: Confirm the preview says protected prompt content is summarized.

Step 17: Confirm the seeded prompt template sentence is not shown.

Step 18: Save a screenshot named `/tmp/qa051-ui-redaction-preview.png`.

Step 19: Run `uv run python scripts/qa/verify_governance_qa051.py`.

Step 20: Copy the output into `/tmp/qa051-ui-post-api-notes.txt`.

Step 21: Open the local login page again.

Step 22: Select `tenant-admin-globex`.

Step 23: Open `/admin/app/governance`.

Step 24: Confirm `QA051 Governance Prompt` is not visible.

Step 25: Confirm Globex sees empty or unavailable states when no Globex records exist.

Step 26: Save a screenshot named `/tmp/qa051-ui-cross-tenant-empty.png`.

Step 27: Review every screenshot for raw secrets, raw prompt text, raw completions, authorization headers, private run payloads, and local paths.

Step 28: Record the final result in `/tmp/qa051-ui-post-api-notes.txt`.

## Expected Results

Expected result 1: the login page lists local QA principals.

Expected result 2: platform admin reaches the Governance React page.

Expected result 3: the page shows `QA051 Governance Prompt`.

Expected result 4: empty provider panels say no authorized live provider connections exist.

Expected result 5: empty profile panels say no authorized live runtime profile records exist.

Expected result 6: prompt save returns an accepted backend result.

Expected result 7: prompt save creates a newer durable draft revision.

Expected result 8: redaction preview shows summary-only output.

Expected result 9: Globex does not see Acme prompt data.

Expected result 10: no raw credential value appears.

Expected result 11: no raw prompt body appears.

Expected result 12: no raw completion appears.

Expected result 13: no provider authorization header appears.

Expected result 14: no private run payload appears.

Expected result 15: no fake qa031 governance row appears in production UI.

Expected result 16: screenshots and notes are clearly named with qa051.

Expected result 17: the post-UI verification command passes.

Expected result 18: any failure is recorded before rerunning.

## Evidence To Capture

Capture the login screenshot.

Capture the seeded governance screenshot.

Capture the prompt save screenshot.

Capture the redaction preview screenshot.

Capture the cross-tenant empty screenshot.

Capture the output from `scripts/qa/verify_governance_qa051.py`.

Capture the platform bootstrap API response summary.

Capture the Acme prompt route response summary.

Capture the Globex empty route response summary.

Capture the automated Playwright screenshot path.

Capture any redaction concern as a written note.

Capture the exact principal used for each browser check.

Capture the time the QA database was recreated.

Capture the command output if the seed script reports the prompt already exists.

Capture the command output if the post-UI verification reports revision count.

Do not capture real credentials.

Do not capture private messages.

Do not capture raw prompts.

Do not capture raw completions.

Do not capture production URLs.

## Security And Redaction Checks

Search the page visually for secret-like text.

Search the screenshots for secret-like text.

Search the API notes for secret-like text.

The allowed secret text pattern is a qa051 reference label, not a value.

Safe references may look like `qa051/provider-placeholder`.

Unsafe values may look like raw tokens, keys, or provider headers.

The page may say a credential reference exists.

The page may show a fingerprint.

The page may not show the credential itself.

The page may summarize a prompt.

The page may not show the full prompt template.

The page may summarize a preview.

The page may not show a raw completion.

The page may show audit reference ids.

The page may not show protected run payloads.

If you are unsure whether something is secret, treat it as a blocker and ask for review.

## Tenant Isolation Checks

Acme owns the QA prompt.

Globex is a separate tenant.

Platform admin can inspect platform-wide governance state.

Tenant admin Acme can inspect Acme prompt governance state.

Tenant admin Globex must not inspect Acme prompt governance state.

The easiest negative check is to log in as `tenant-admin-globex`.

After logging in as Globex, open `/admin/app/governance`.

Look for `QA051 Governance Prompt`.

The prompt must not be present.

The page should show empty or unavailable states for missing Globex records.

The page should not include Acme labels in hidden error text.

The page should not include Acme prompt ids in visible text.

If the cross-tenant check fails, do not mark QA051 complete.

## Troubleshooting

If the app does not start, confirm Docker PostgreSQL is running.

If the database is missing, recreate only `multi_agent_platform_qa051`.

If the login page is unavailable, confirm the API is listening on port 8000.

If local principals are missing, confirm `.env.qa051` was copied.

If the Governance page is unavailable, confirm the React build completed.

If the QA prompt is missing, rerun the seed script.

If `Save summary` is missing, check the prompt route as platform admin.

If the save action returns an error, copy the safe error text into your notes.

If post-UI verification fails, do not rely on the screenshot alone.

If the redaction preview leaks the template sentence, stop immediately.

If Globex can see the Acme prompt, stop immediately.

If a command fails because of unrelated dirty worktree changes, record the failure and keep the validated worktree in place.

Do not commit between specs during this autopilot run.

Do not reset the worktree.

Do not delete prior validated spec changes.

Rerun only the failing validation after fixing the qa051 issue.

When the issue is fixed, rerun Playwright and post-UI verification together.

When all checks pass, qa051 can be recorded as complete in status history.
