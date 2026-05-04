# QA024 User Guide: Missing Feature 5 - Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Detailed Overview

This guide explains QA024 in plain language for manual reviewers.

QA024 protects workflow publishing.

A workflow can say that an automated test suite is required before publishing.

Before QA024, a reviewer could see a manual-looking result field in the workflow document.

QA024 makes the publish gate look at real Agent Test Bench runs instead.

The important rule is simple.

A required suite must have a current passing run in the repository.

Current means same tenant.

Current means same workflow draft.

Current means same draft revision.

Current means the run status is passing.

If any of those pieces are missing, the workflow should not publish.

The gate should explain the problem with safe language.

Safe language means no raw secrets.

Safe language means no fixture body.

Safe language means no raw transcript.

Safe language means no hidden tenant suite name.

Safe language means no artifact contents.

Reviewers should focus on what the gate allows and what it blocks.

Reviewers do not need to understand the implementation classes to complete this guide.

The main screens are the Workflow Registry and the Agent Test Bench.

The main outcome is the Required Test Evidence section on the publish gate.

The section should show required, passing, missing, failing, and stale counts.

Ready evidence should enable publication.

Blocked evidence should disable publication.

Manual status fields should not change the outcome.

Cross-tenant evidence should not reveal private names.

This guide uses the QA024 local environment only.

## Who Should Use This Guide

Use this guide if you are a product reviewer.

Use this guide if you are a QA reviewer.

Use this guide if you are validating browser behavior before a pull request merges.

Use this guide if you need to confirm tenant isolation.

Use this guide if you need to collect screenshots.

Use this guide if you are not comfortable reading PostgreSQL directly.

Developers can also use the guide as a manual smoke test.

The companion `qa024.md` includes more command-line evidence.

The companion `qa024_ui.md` includes a browser-first walkthrough.

## Manual QA Prerequisites

You need the repository checkout on your machine.

You need Docker available for PostgreSQL.

You need the `uv` command available.

You need a browser.

You need permission to run local shell commands.

You do not need real Auth0 credentials.

You do not need real model provider credentials.

You do not need real Telegram credentials.

You do not need any customer data.

Use the file `.env.qa024`.

Use the database `multi_agent_platform_qa024`.

Use fake `qa024/` secret references only.

Start from the repository root.

Back up an existing `.env` file if one exists.

Copy `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/.env.qa024` to `.env`.

Run `uv sync`.

Run `docker compose up -d postgres`.

Reset the QA database.

Run `uv run alembic upgrade head`.

Seed Acme and Globex tenants.

Start the API on `http://127.0.0.1:8000`.

Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui`.

Choose `tenant-admin-acme` first.

Keep a notes file named `/tmp/qa024-reviewer-notes.txt`.

Keep screenshots under `output/playwright/qa024_ui`.

## Step-by-Step Manual QA

Step 1: Sign in as Acme Tenant Admin.

Expected result: the Workflow Registry opens.

What this proves: the local login flow is working.

Step 2: Confirm the page is scoped to Acme.

Expected result: the page does not show Globex-only data.

What this proves: tenant scope is applied before any evidence checks.

Step 3: Create a workflow draft named `QA024 Required Evidence Draft`.

Expected result: the draft opens in the workflow editor.

What this proves: there is a workflow candidate to validate.

Step 4: Save the draft.

Expected result: the editor reports a current revision.

What this proves: the publish gate has a target version to evaluate.

Step 5: Record the draft id and revision id in your notes.

Expected result: your notes include both values.

What this proves: later checks can compare the suite run target.

Step 6: Open the Agent Test Bench.

Expected result: the Agent Tests page loads for Acme.

What this proves: the reviewer can create repository evidence.

Step 7: Create a test suite for the workflow draft.

Expected result: the suite target type is workflow draft.

What this proves: the suite is aimed at the same kind of target as the workflow.

Step 8: Set the target id to the draft id.

Expected result: the suite saves without error.

What this proves: the suite belongs to the candidate workflow.

Step 9: Set the target version to the current revision id.

Expected result: the suite target version matches the draft revision.

What this proves: the run can be current instead of stale.

Step 10: Add one deterministic mock case.

Expected result: the case saves.

What this proves: the suite has something to run.

Step 11: Run the suite in mock mode.

Expected result: the run passes.

What this proves: the repository has passing evidence.

Step 12: Return to the workflow editor.

Expected result: the draft is still in Acme scope.

What this proves: the workflow and suite share a tenant.

Step 13: Add the suite as a required test.

Expected result: the workflow document saves.

What this proves: the publish gate now knows which suite to require.

Step 14: If saving created a new revision, rerun the suite for that revision.

Expected result: the run target version equals the latest revision.

What this proves: the evidence is current.

Step 15: Validate the workflow draft.

Expected result: validation passes with no blocking required-test finding.

What this proves: repository-backed evidence is accepted.

Step 16: Open the publish gate.

Expected result: the Required Test Evidence section is visible.

What this proves: the UI exposes evidence counts to reviewers.

Step 17: Confirm the passing count is one.

Expected result: missing, failing, and stale counts are zero.

What this proves: the ready path is correctly classified.

Step 18: Confirm publish is enabled.

Expected result: the publish action is available.

What this proves: current passing evidence unlocks publication.

Step 19: Change the workflow draft.

Expected result: a new revision is created.

What this proves: the old run should now be stale.

Step 20: Validate without rerunning the suite.

Expected result: validation blocks.

What this proves: old revision evidence is rejected.

Step 21: Open the publish gate again.

Expected result: stale evidence is listed.

What this proves: the UI explains why publication is blocked.

Step 22: Reference a suite that has no current run.

Expected result: missing evidence is listed.

What this proves: absent evidence fails closed.

Step 23: Create or simulate a failing current run.

Expected result: failed evidence is listed.

What this proves: current failed evidence does not unlock publishing.

Step 24: Sign in as Globex Tenant Admin.

Expected result: Globex can only see Globex data.

What this proves: cross-tenant access is separated.

Step 25: Create a Globex suite named `Globex Private Suite`.

Expected result: the suite saves in Globex scope.

What this proves: there is private cross-tenant data for the denial check.

Step 26: Sign back in as Acme Tenant Admin.

Expected result: Acme workflow pages load again.

What this proves: the reviewer returned to the original tenant.

Step 27: Attempt to use the Globex suite id as an Acme requirement.

Expected result: validation blocks.

What this proves: cross-tenant evidence is not accepted.

Step 28: Look for the text `Globex Private Suite` on the Acme gate.

Expected result: the text is not visible.

What this proves: denied evidence does not leak suite names.

Step 29: Set a manual latest result status to `passed` if the editor exposes it.

Expected result: validation still uses repository evidence.

What this proves: manual status cannot bypass the gate.

Step 30: Save screenshots of the ready and blocked gates.

Expected result: screenshots are stored under `output/playwright/qa024_ui`.

What this proves: the QA pass has visible evidence.

## Expected Results

The Local Login page should show QA024 principals.

The Workflow Registry should load for Acme.

The Agent Test Bench should load for Acme.

An Acme suite run for the current draft revision should be accepted.

A stale suite run should be rejected.

A missing suite run should be rejected.

A failing suite run should be rejected.

A Globex suite should not be accepted for an Acme workflow.

The Acme publish gate should not display the private Globex suite name.

The publish gate should show Required Test Evidence.

The publish gate should show clear counts.

The publish gate should enable publish only in the ready case.

The publish gate should disable publish in blocked cases.

Published metadata should pin safe evidence summaries.

Manual `latest_result_status` should not make the gate ready.

The UI should not expose raw fixture bodies.

The UI should not expose raw transcripts.

The UI should not expose secret-looking values.

The UI should not expose authorization headers.

## Evidence To Capture

Capture a screenshot of the login page.

Capture a screenshot of the Workflow Registry.

Capture a screenshot of the Agent Test Suite target fields.

Capture a screenshot of the passing run.

Capture a screenshot of the ready publish gate.

Capture a screenshot of the stale publish gate.

Capture a screenshot of the missing evidence state.

Capture a screenshot or note for the failing evidence state.

Capture a note that the manual status bypass failed.

Capture a note that the Globex suite name was hidden.

Capture the focused pytest command result.

Capture the full quality gate result if you run it locally.

Store reviewer notes in `/tmp/qa024-reviewer-notes.txt`.

Store screenshots in `output/playwright/qa024_ui`.

## Security And Redaction Checks

Look for raw fixture values on the publish gate.

Expected result: none are visible.

Look for raw run transcripts.

Expected result: none are visible.

Look for provider tokens or secret values.

Expected result: none are visible.

Look for `Authorization` headers.

Expected result: none are visible.

Look for `Bearer` tokens.

Expected result: none are visible.

Look for the private Globex suite name while signed in as Acme.

Expected result: it is not visible.

Confirm safe summaries are still useful.

Expected result: they say missing, stale, failed, or passing.

## Tenant Isolation Checks

Acme should see Acme workflow drafts.

Acme should see Acme test suites.

Acme should not see Globex test suites.

Globex should see Globex test suites.

Globex should not see Acme workflow drafts.

Globex evidence should not satisfy Acme workflow requirements.

Acme evidence should not satisfy Globex workflow requirements.

Cross-tenant errors should be safe.

Cross-tenant errors should not reveal target names.

Cross-tenant errors should not reveal suite names.

Cross-tenant errors should not reveal run ids unless the id is already part of the submitted Acme requirement.

Platform-scope drafts with tenant required tests should fail closed.

## Troubleshooting

If login does not show QA principals, copy `.env.qa024` again and restart the API.

If the database has old records, reset `multi_agent_platform_qa024`.

If a suite run is stale, rerun the suite after saving the workflow draft.

If a ready gate is blocked, compare draft revision id and run target version.

If an Acme reviewer sees a Globex suite name, treat it as a security bug.

If screenshots do not save, create `output/playwright/qa024_ui`.

If tests fail with coverage during a focused run, rerun the focused command with `--no-cov`.

If Docker is not running, start Docker and rerun PostgreSQL setup.

If port `8000` is busy, stop the other local API before starting QA024.

If the UI and database disagree, refresh the page after validation.

If the publish button stays disabled after fixing evidence, validate the draft again.

If automated Playwright fails at login, confirm the local login URL includes `/admin/workflows/ui`.
