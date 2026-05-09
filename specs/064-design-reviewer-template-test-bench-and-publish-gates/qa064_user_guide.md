# QA064 User Guide: Spec 064 - Design Reviewer Template, Test Bench, And Publish Gates

## Detailed Overview

The Design Reviewer Council template setup feature gives tenant admins a reusable starting point.
It installs a council workflow draft for a tenant.
It connects that draft to required Agent Test Bench evidence.
It runs deterministic evidence in local QA.
It runs governed model backed safe evidence without live side effects.
It evaluates whether the current draft revision is ready for publication.
It shows readiness in the Design reviews workspace.
The user-facing workflow is explicit.
An admin chooses setup instead of receiving hidden fixture data.
The setup action is idempotent.
Running setup twice should not create duplicate workflow drafts.
Running setup twice should not create duplicate required suites.
Running setup twice should not create duplicate case definitions.
The workspace remains live-data only.
Template setup does not create a design review session.
Template setup does not invent reviewer verdict rows.
Template setup does not invent handoff data.
The page must be safe for tenant admins to view.
It must not show raw prompts.
It must not show raw completions.
It must not show provider request or response payloads.
It must not show secrets or authorization headers.
It must not show private channel messages.
It must not show memory contents.
It must not show raw external tool payloads.
It must show safe IDs, statuses, summaries, and artifact references.

## Who Should Use This Guide

Use this guide if you are validating the Admin setup experience manually.
Use this guide if you are reviewing release evidence for Spec 064.
Use this guide if you need to explain the council template to another admin.
Use this guide if you need to confirm tenant isolation.
Use this guide if you need to confirm publish readiness behavior.
Use this guide if you need to confirm local QA avoids live provider calls.
You need Docker.
You need the local repository.
You need the qa064 environment file.
You need a browser that can open `http://127.0.0.1:8000`.
You do not need external identity services.
You do not need live provider credentials.
You do not need Telegram access.
You do not need external connector access.

## Manual QA Prerequisites

Confirm Docker is running.
Confirm PostgreSQL is available through Docker Compose.
Confirm `uv sync` can complete.
Confirm npm dependencies are installed or installable under `frontend/admin`.
Confirm `.env.qa064` exists.
Confirm the local-principal catalog includes Acme and Globex.
Confirm Acme has tenant admin and test-bench permissions.
Confirm Globex does not receive Acme state.
Confirm static secret references use the `qa064/` prefix.
Confirm live provider probes are disabled.
Confirm live Telegram delivery is disabled.
Confirm external connector calls are disabled.
Confirm screenshots can be saved under `output/playwright/qa064_ui`.
Confirm review notes can be saved under `/tmp/qa064-ui-notes.txt`.

## Step-by-Step Manual QA

1. Copy the qa064 environment file.

```bash
cp specs/064-design-reviewer-template-test-bench-and-publish-gates/.env.qa064 .env
```

Expected result: the active environment targets `multi_agent_platform_qa064`.

2. Install dependencies.

```bash
uv sync
```

Expected result: repository dependencies are ready.

3. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running.

4. Recreate the qa064 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa064 && createdb -U postgres multi_agent_platform_qa064'
```

Expected result: the qa064 database is empty.

5. Apply migrations.

```bash
uv run alembic upgrade head
```

Expected result: all schema objects exist.

6. Seed local principals.

```bash
uv run python scripts/qa/seed_local_principals.py
```

Expected result: Acme and Globex principals are available.

7. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the API starts successfully.

8. Install the council template.

```bash
uv run python scripts/qa/seed_design_review_template_qa064.py
```

Expected result: the command prints `Seeded QA064 design review council template evidence`.

9. Verify backend state.

```bash
uv run python scripts/qa/verify_design_review_template_qa064.py
```

Expected result: the command prints `Verified QA064 design review template evidence`.

10. Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews
```

Expected result: local login options are visible.

11. Choose Acme tenant admin.

Expected result: the Design reviews workspace opens for Acme.

12. Check the template setup panel.

Expected result: the panel says the council template has current required evidence.

13. Check evidence modes.

Expected result: deterministic and model backed safe evidence are listed.

14. Check publish readiness.

Expected result: the publish gate appears ready.

15. Check the session list.

Expected result: no design review sessions appear from template setup alone.

16. Run setup again from the UI if the action is available.

Expected result: the page remains ready and no duplicate sessions appear.

17. Refresh the browser.

Expected result: the template panel still reports ready state.

18. Open Globex through local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: Globex does not show Acme template readiness.

19. Capture Acme screenshot evidence.

Expected result: the screenshot shows ready template state and safe labels.

20. Capture Globex screenshot evidence.

Expected result: the screenshot shows isolated empty state.

## Expected Results

Acme can install the council template.
Acme can replay template installation safely.
Acme sees current required evidence.
Acme sees deterministic evidence.
Acme sees model backed safe evidence.
Acme sees ready publish-gate state.
Acme session rows remain empty after template setup alone.
Globex does not see Acme template setup.
Globex cannot install Acme template setup.
The install route returns safe JSON.
The workspace bootstrap returns safe JSON.
The React page shows safe labels.
The React page does not reveal raw sensitive content.
Evidence files contain safe IDs and statuses.
Screenshots contain no protected payloads.
Manual notes contain no protected payloads.

## Evidence To Capture

Capture `/tmp/qa064-seed.txt`.
Capture `/tmp/qa064-verify.txt`.
Capture `.data/qa064-artifacts/evidence/qa064-template-seed.json`.
Capture `.data/qa064-artifacts/evidence/qa064-template-verify.json`.
Capture `output/playwright/qa064_ui/qa064-scenario-enhancement-smoke.png`.
Capture the focused backend test output.
Capture the focused frontend test output.
Capture the typecheck output.
Capture the build output.
Capture the Spec Kit QA output.
Capture the Playwright output.
Capture the curl regression output directory.
Record any failure as a safe summary only.

## Sensitive Data Rules

Do not copy prompt text into notes.
Do not copy model completion text into notes.
Do not copy provider payloads into notes.
Do not copy authorization headers into notes.
Do not copy secret values into notes.
Do not copy private channel messages into notes.
Do not copy memory contents into notes.
Do not copy raw external tool payloads into notes.
Do copy status names.
Do copy artifact references.
Do copy workflow draft identifiers.
Do copy suite identifiers.
Do copy run identifiers.
Do copy safe evidence mode labels.

## Security And Redaction Checks

Confirm the template panel shows status labels, not raw reviewer transcripts.
Confirm evidence files store run identifiers, not raw model output.
Confirm the verify helper writes safe JSON only.
Confirm no secret-like value appears in the browser.
Confirm no authorization header appears in the browser.
Confirm no provider request payload appears in the browser.
Confirm no provider response payload appears in the browser.
Confirm no private channel message appears in the browser.
Confirm no memory content appears in the browser.
Confirm no raw external tool payload appears in the browser.
Confirm cross-tenant denial returns safe problem details.
Confirm screenshots are safe to attach to review.
Confirm notes include safe summaries only.
Confirm artifact references point to qa064 evidence paths.

## Tenant Isolation Checks

Use Acme for the successful setup path.
Use Globex for the isolation path.
Confirm Acme can install the council template for Acme.
Confirm Acme can replay the install action for Acme.
Confirm Globex cannot install the council template for Acme.
Confirm Globex workspace bootstrap returns not installed state for Globex.
Confirm Globex does not see Acme workflow draft identifiers.
Confirm Globex does not see Acme suite identifiers.
Confirm Globex does not see Acme required evidence status.
Confirm Globex does not see Acme publish readiness.
Confirm empty session lists remain tenant-specific.
Confirm every manual note names the active tenant.

## Troubleshooting

If setup reports not installed, rerun the seed helper.
If setup reports stale, confirm no newer draft revision was saved after evidence was created.
If setup reports evidence failed, inspect the safe verification output.
If the UI does not show ready state, reload the workspace after seeding.
If Globex shows Acme state, stop and file a tenant isolation blocker.
If sessions appear after template setup alone, stop and file a live-data blocker.
If Playwright cannot log in, confirm local-principal mode.
If the build fails, run the focused React tests first.
If backend tests fail, run the template service test first.
If curl regression fails, inspect the first failed curl command output.

## Release Reviewer Notes

The template setup is additive.
It does not replace existing design review sessions.
It does not alter coordinator runtime behavior.
It does not require a hidden fixture.
It does not require live provider credentials in local QA.
It does not require external side effects.
It should make first-run Admin setup more discoverable.
It should make publish readiness easier to audit.
It should keep evidence tied to the current workflow draft revision.
It should leave empty tenants honestly empty.
