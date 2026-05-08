# QA054 UI Walkthrough: Membership And Access React Live Data

## Goal

Guide a reviewer through browser evidence for qa054.

Expected: the React membership workspace loads from live backend records.

Expected: the browser shows seeded Acme membership rows only after the QA seed
command persists them.

Expected: the reviewer can click `Invite` and see an accepted mutation result.

Expected: the post-UI verifier proves the invitation exists in the qa054
database after the browser action.

Expected: the browser never displays raw email, full subject, credential,
provider token, stack trace, local path, or unauthorized tenant content.

What is happening: the page is using `/admin/app/memberships/bootstrap.json`
and membership mutation routes rather than fixed production helper rows.

Why this matters: qa054 is only done if browser-visible data is backed by the
same database rows the API and verifier inspect.

## How To Use This Guide

Use this walkthrough with `qa054.md`.

Save screenshots under `output/playwright/qa054_ui`.

Save reviewer notes under `/tmp/qa054-ui-reviewer-notes.txt`.

Save browser console notes under `/tmp/qa054-ui-console-notes.txt`.

Save post-action API notes under `/tmp/qa054-ui-post-api-notes.txt`.

Expected: screenshot filenames include qa054.

Expected: notes mention the local principal and tenant being reviewed.

Expected: API notes identify the invitation by safe hash or masked label.

Expected: reviewer notes avoid copying unsafe payload content.

What is happening: automated Playwright follows the same flow as this manual
walkthrough.

Why this matters: manual evidence and automated evidence should match.

## Environment Setup

Copy the QA environment.

```bash
cp specs/054-membership-and-access-react-live-data/.env.qa054 .env
```

Expected: `.env` now contains `APP_NAME=multi-agent-platform-qa054`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are available.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL service is running.

Reset the qa054 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa054 && createdb -U postgres multi_agent_platform_qa054'
```

Expected: only the qa054 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete successfully.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa054 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist.

Seed membership records.

```bash
uv run python scripts/qa/seed_membership_qa054.py
```

Expected: the command prints the seeded qa054 tenant id.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

## Browser Walkthrough

Open the local login route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Expected: the local-principal login page appears.

Choose the Acme tenant admin principal.

```text
tenant-admin-acme
```

Expected: the browser redirects to `/admin/app/memberships`.

Confirm the page title.

```text
Membership Administration
```

Expected: the page title is visible.

Confirm the seeded user.

```text
Maya Chen
```

Expected: the seeded Acme tenant admin appears in the directory.

Confirm support override evidence.

```text
Support overrides
```

Expected: the support override panel renders persisted qa054 evidence.

Confirm audit evidence.

```text
Role grant created from qa054 live seed.
```

Expected: the audit panel renders the seeded safe summary.

Confirm the invitation form default.

```text
invite.replay@example.test
```

Expected: the form is ready to create a browser-driven invitation.

Click `Invite`.

```text
Invite
```

Expected: the page shows an accepted invitation result.

Confirm the mutation summary.

```text
Invitation created in persisted membership state.
```

Expected: the browser reports the backend mutation result.

Capture a screenshot.

```bash
mkdir -p output/playwright/qa054_ui
```

Expected: screenshot evidence can be saved in the qa054 output directory.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_membership_qa054.py
```

Expected: the verifier reports at least one Playwright invitation.

What is happening: the browser sends a POST to
`/admin/app/memberships/invitations`.

Why this matters: the QA action proves durable backend mutation instead of
static rendering.

## Required Automated Evidence

Run document validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/054-membership-and-access-react-live-data
```

Expected: QA docs pass validation.

Run spec API validation.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml
```

Expected: membership route, redaction, and quality checks pass.

Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml --start-processes
```

Expected: the browser action and screenshot complete.

Run focused frontend tests.

```bash
npm run --prefix frontend/admin test -- --run Membership SupportOverride AccessHistory RoleGrant Invitation PrincipalLink StatusActions RawIdentifier
```

Expected: membership component tests pass.

Run frontend typecheck.

```bash
npm run --prefix frontend/admin typecheck
```

Expected: TypeScript typecheck passes.

Run frontend build.

```bash
npm run --prefix frontend/admin build
```

Expected: production React assets build.

Run Ruff.

```bash
uv run ruff check .
```

Expected: lint checks pass.

Run Ruff format check.

```bash
uv run ruff format --check .
```

Expected: formatting checks pass.

Run mypy.

```bash
uv run mypy src
```

Expected: type checks pass.

Run full coverage.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: coverage stays at or above the project gate.

## UI Evidence Checklist

Record the login principal in `/tmp/qa054-ui-reviewer-notes.txt`.

Record the active tenant in `/tmp/qa054-ui-reviewer-notes.txt`.

Record whether `Maya Chen` appears for Acme.

Record whether Globex remains empty.

Record whether support override evidence is visible only in authorized scope.

Record the screenshot path under `output/playwright/qa054_ui`.

Record the invitation result summary.

Record verifier output after the browser action.

Expected: evidence references only safe labels and masked identifiers.

Expected: reviewer notes do not include raw database rows.

## Acceptance Notes Template

QA database: `multi_agent_platform_qa054`.

Principal used: `tenant-admin-acme`.

Positive tenant: `Acme`.

Isolation tenant: `Globex`.

Browser route: `/admin/app/memberships`.

Action performed: `Invite`.

Expected result seen: `Invitation created in persisted membership state.`

Screenshot path: `output/playwright/qa054_ui/qa054-live-data-ui-api-smoke.png`.

Verifier command: `uv run python scripts/qa/verify_membership_qa054.py`.

Verifier result: record the safe count summary.

## Troubleshooting

If `tenant-admin-acme` is missing, confirm `.env.qa054` was copied into `.env`.

If `Maya Chen` is missing, rerun the seed script.

If `Invite` is disabled, confirm the Acme tenant scope is active.

If the mutation result does not appear, inspect browser console notes and API
logs under `/tmp/qa054-api.log`.

If the verifier fails, rerun Playwright before the verifier.

If unauthorized Globex content appears, stop because tenant isolation failed.

If raw email or token-like text appears, stop because redaction failed.

## Related Files

- `specs/054-membership-and-access-react-live-data/qa054.md`
- `specs/054-membership-and-access-react-live-data/.env.qa054`
- `scripts/qa/seed_membership_qa054.py`
- `scripts/qa/verify_membership_qa054.py`
- `frontend/admin/src/components/memberships/MembershipPage.tsx`
- `frontend/admin/src/components/memberships/InvitationPanel.tsx`
- `src/multi_agent_platform/admin/memberships/react_memberships.py`
