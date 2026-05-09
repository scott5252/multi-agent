# QA063 User Guide: Spec 063 - Admin Design Review Workspace

## Detailed Overview

The Admin Design Review workspace is a browser page for tenant admins.
It shows Design Reviewer Council sessions.
It shows each session's current status.
It shows safe request summaries.
It shows immutable design revision summaries.
It shows review rounds and runtime run references.
It shows reviewer verdict summaries.
It shows quorum decisions.
It shows manual decisions when people need to intervene.
It shows final development handoff references after approval.
The page is intentionally live-data only.
That means an empty tenant must look empty.
That also means a successful handoff must come from the database.
The page should never use hidden sample records to look successful.
The page should keep sensitive content out of the browser.
Sensitive content includes raw prompts.
Sensitive content includes model completions.
Sensitive content includes provider request and response payloads.
Sensitive content includes secrets.
Sensitive content includes authorization headers.
Sensitive content includes private channel messages.
Sensitive content includes memory contents.
Sensitive content includes raw external tool payloads.
The page is part of the existing Admin shell.
It uses local-principal authentication for QA.
It must preserve tenant scope.
It must preserve safe navigation and focus behavior.
It must avoid product copy that talks about implementation frameworks.
The reviewer's job is to prove that real records appear and fake records do not.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer.
Use this guide if you need to confirm the workspace in a local deterministic environment.
Use this guide if you need to capture browser screenshots for release review.
Use this guide if you need to verify empty tenant behavior.
Use this guide if you need to verify redaction boundaries.
Use this guide if you need to verify manual-resolution behavior.
You do not need to understand the backend implementation to follow this guide.
You do need access to the local repository and Docker.
You do need a browser that can open `http://127.0.0.1:8000`.

## Manual QA Prerequisites

Confirm Docker is running.
Confirm the repository dependencies are available.
Confirm PostgreSQL can start through Docker Compose.
Confirm the qa063 environment file exists.
Confirm no production credentials are in the environment file.
Confirm no live provider probes are enabled.
Confirm the local-principal catalog includes Acme and Globex.
Confirm the API and worker terminals can be opened separately.
Confirm screenshots can be saved under `output/playwright/qa063_ui`.
Confirm review notes can be saved under `/tmp/qa063-ui-notes.txt`.

## Step-by-Step Manual QA

1. Copy the environment file.

```bash
cp specs/063-admin-design-review-workspace/.env.qa063 .env
```

Expected result: `.env` now points at the qa063 database.

2. Install dependencies.

```bash
uv sync
```

Expected result: dependencies are installed or already present.

3. Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running.

4. Recreate the qa063 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa063 && createdb -U postgres multi_agent_platform_qa063'
```

Expected result: the database is empty and ready.

5. Apply migrations.

```bash
uv run alembic upgrade head
```

Expected result: the database has all schema objects.

6. Seed the QA workspace.

```bash
uv run python scripts/qa/seed_design_review_workspace_qa063.py
```

Expected result: the seed command prints `Seeded QA063 design review workspace live records`.

7. Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the server starts successfully.

8. Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews
```

Expected result: the local login page is displayed.

9. Select the Acme tenant admin principal.

Expected result: the browser opens the Design reviews workspace.

10. Check the page header.

Expected result: the page title is Design reviews and the copy describes sessions, rounds, decisions, and handoffs.

11. Check shell context.

Expected result: Acme is the active tenant scope.

12. Check summary cards.

Expected result: counts are present and match seeded records.

13. Check session list.

Expected result: a seeded Acme session appears with status and revision information.

14. Select the seeded session.

Expected result: the detail panel shows the safe request summary.

15. Check revision history.

Expected result: revision summaries and digests are visible, but raw design payloads are not visible.

16. Check round history.

Expected result: the review round appears with reviewer count and quorum count.

17. Check verdict summaries.

Expected result: reviewer keys, verdicts, scores, blocker counts, safe summaries, and digests are visible.

18. Check quorum decision.

Expected result: approval count, blocker count, policy version, and safe rationale are visible.

19. Check handoff.

Expected result: the development handoff reference is visible for approved sessions.

20. Check create form.

Expected result: request summary, quorum policy, workflow option, and submit controls are available.

21. Create a new safe session.

Expected result: the new session appears after the action completes.

22. Launch a review round when a workflow is available.

Expected result: a live round appears and includes a runtime run reference.

23. Review manual-resolution controls when available.

Expected result: manual controls appear only when the session is in manual resolution.

24. Open the Globex tenant workspace.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: Acme records do not appear.

25. Capture screenshot evidence.

Expected result: the screenshot shows safe live data and active tenant context.

## Expected Results

The Acme workspace shows live seeded records.
The Globex workspace does not show Acme records.
Empty states do not contain sample sessions.
The selected session detail shows safe summaries only.
Verdicts show safe summaries and digests only.
The quorum panel explains the decision safely.
The handoff panel shows a safe reference only.
Create actions persist live sessions.
Launch actions create live rounds.
Manual actions persist live decisions.
The browser remains within the Admin shell.
Keyboard focus is visible.
Controls have accessible labels.
No implementation-framework labels appear in product copy.
No raw prompt or provider content appears.
No secret-like value appears.

## Evidence To Capture

Capture a screenshot of the Acme workspace.
Capture a screenshot of the selected session detail.
Capture a screenshot of the empty Globex state.
Capture `/tmp/qa063-seed.txt` from the seed command.
Capture `/tmp/qa063-verify.txt` from the verify command.
Capture the Playwright screenshot path.
Capture frontend test output.
Capture backend route test output.
Capture full Spec Kit QA output.
Capture full curl regression output.
Do not capture raw database dumps.
Do not capture raw model payloads.

## Security And Redaction Checks

Search the page for secret-like values.
Search the page for raw prompt text.
Search the page for provider payload words.
Search the page for authorization headers.
Search the page for private channel content.
Search the page for memory content.
Search the page for raw external tool payloads.
Confirm only safe summaries, digests, IDs, statuses, and references appear.
Confirm errors are safe summaries.
Confirm screenshots can be attached to review notes.

## Tenant Isolation Checks

Use Acme first.
Record the Acme seeded session ID.
Switch to Globex.
Confirm the Acme session ID is absent.
Confirm the session list is empty or contains only Globex records.
Confirm the selected-session panel does not show Acme details.
Try a direct Globex request for Acme tenant scope if needed.
Expected result: the API denies access or returns no cross-tenant data.

## Troubleshooting

If the page does not load, confirm the API is running.
If login does not redirect, confirm the local-principal catalog is loaded.
If Acme records are missing, rerun the seed script.
If Globex shows records, stop and file a blocker.
If the create action fails, capture the safe error only.
If launch is disabled, confirm workflow options exist.
If manual actions are missing, confirm the session status is manual resolution.
If the UI shows unsafe copy, stop and file a blocker.
If Playwright fails to capture a screenshot, retry after confirming the route loads manually.
If full curl regression fails, inspect the first failed command before rerunning.
