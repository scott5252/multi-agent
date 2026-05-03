# QA018 UI: User And Tenant Membership Administration

## Goal

This walkthrough lets a non-developer reviewer validate the browser experience
for Membership Administration. It focuses on what appears on screen, which
principal to use, which tenant scope is active, what each action means, and how
to collect evidence without exposing raw email addresses, Auth0 subject values,
tokens, or passwords.

## How To Use This Guide

Follow this guide from a fresh checkout or after resetting the QA database. The
API checks in `qa018.md` are helpful but not required before starting this UI
walkthrough. Every screenshot or reviewer note should be stored under
`/tmp/qa018-*` or `output/playwright/qa018_ui`.

Use `platform-admin` first because that principal can see the platform-level
view and can create seed data. Then switch to `tenant-admin-acme` to confirm
tenant-scoped behavior and guarded role controls.

## Environment Setup

Copy the environment file and install dependencies:

```bash
test ! -f .env || cp .env .env.qa018-ui-backup
cp specs/018-user-tenant-membership-administration/.env.qa018 .env
uv sync
mkdir -p .data/qa018-artifacts output/playwright/qa018_ui
```

Expected: the QA018 environment is active and artifact folders exist.

Start the database, reset it, and apply migrations:

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa018 && createdb -U postgres multi_agent_platform_qa018'
uv run alembic upgrade head
```

Expected: Alembic creates the membership administration tables.

Seed the Acme and Globex tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa018 <<'SQL'
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    'acme',
    'Acme',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'globex',
    'Globex',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  )
ON CONFLICT (slug) DO UPDATE
SET display_name = EXCLUDED.display_name,
    status = EXCLUDED.status,
    updated_at = CURRENT_TIMESTAMP;
SQL
```

Expected: Acme and Globex are available for local-principal tenant scopes.

Start the API server:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the server is available at `http://127.0.0.1:8000`.

In another terminal, create a small amount of browser-visible seed data:

```bash
export QA018_BASE_URL=http://127.0.0.1:8000
export QA018_ACME_TENANT=11111111-1111-1111-1111-111111111111

curl --fail --silent -H "X-Local-Principal: platform-admin" \
  "$QA018_BASE_URL/admin/memberships/api/users" \
  | tee /tmp/qa018-ui-bootstrap-platform.json

curl --fail --silent -X POST "$QA018_BASE_URL/admin/memberships/api/invitations" \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -d "{\"tenant_id\":\"$QA018_ACME_TENANT\",\"email\":\"browser.qa018@example.test\",\"requested_roles\":[\"tenant_user\"],\"idempotency_key\":\"qa018-ui-browser\"}" \
  | tee /tmp/qa018-ui-seed-invite.json
```

Expected: the seed invite returns masked email evidence and the browser page
has at least one invitation row to display.

What is happening: the API is creating reviewer-safe sample data through the
same service used by the browser form.

Why this matters: an empty page can be correct, but visible rows make redaction,
tables, and controls easier to inspect.

## Browser Walkthrough

1. Open local login.

Page URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships`

Navigation path: paste the URL into the browser.

Actions: verify the page title is `Local Login`, then find the
`platform-admin` principal card.

Expected: `platform-admin`, `tenant-admin-acme`, `tenant-user-acme`,
`auditor-acme`, and `tenant-admin-globex` are visible choices.

What is happening: local-principal mode uses a QA-only catalog and stores the
selected catalog key in a local browser cookie.

Why this matters: reviewers can switch roles without real Auth0 credentials,
while still exercising protected request authorization.

2. Sign in as platform admin.

Page URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships`

Navigation path: click the button on the `platform-admin` card.

Actions: wait for redirect to `/admin/memberships`.

Expected: the page heading is `Membership Administration`.

What is happening: the protected route authorizes a platform admin with
`membership-admin:read` and renders the server-side admin shell.

Why this matters: the feature is an admin tool, not an unauthenticated page.

3. Inspect the platform summary and redaction notice.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: already on the page after login.

Actions: read the summary band and the notice near the top of the page.

Expected: summary tiles show current scope, active principals, invitations, and
active grants. The notice says masked emails, safe subject labels, role codes,
status, trace ids, and audit summaries are shown only.

What is happening: the page model combines principals, invitations,
memberships, grants, access history, and membership audits into one snapshot.

Why this matters: the UI tells reviewers what data is intentionally displayed
and what must stay hidden.

4. Inspect the Create Invitation form.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: scroll to `Create Invitation`.

Actions: note the Email field, Idempotency key field, `tenant_user` checkbox,
`tenant_admin` checkbox, and Invite button. Type
`ui.review.qa018@example.test`, set idempotency key `qa018-ui-review`, keep
`tenant_user` selected, and submit.

Expected: the browser returns to Membership Administration and the Invitations
table shows a masked email row rather than the full address.

What is happening: the browser posts to `/admin/memberships/invitations` and
the service creates or replays an active invitation.

Why this matters: the primary UI workflow uses the same idempotent invitation
logic as the JSON API.

5. Inspect the Principals table.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: scroll to `Principals`.

Actions: confirm each row has Display name, Email, Subject, Provider, Status,
and Platform action columns.

Expected: emails are masked or unavailable, subjects use safe labels, and
active principals show Suspend controls only at platform scope.

What is happening: local and Auth0-backed principal metadata is rendered in a
password-free summary.

Why this matters: platform admins need enough context to manage access without
revealing sensitive identity values in screenshots.

6. Inspect the Create Role Grant form.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: scroll to `Create Role Grant`.

Actions: open each selector. Observe the Principal selector, Scope selector,
and Role selector.

Expected: platform scope allows platform and tenant choices in the form, while
server-side guardrails still deny invalid combinations.

What is happening: the template exposes controls, and the service enforces the
actual role eligibility rules.

Why this matters: UI controls are convenient, but authorization must live in
the protected service path.

7. Inspect Role Grants and Tenant Memberships.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: scroll below the role grant form.

Actions: look for status pills, tenant ids, role codes, and Revoke, Suspend,
Restore, or Remove actions where rows exist.

Expected: active grants can be revoked, active memberships can be suspended or
removed, suspended memberships can be restored, and removed memberships have no
restore shortcut in the visible row.

What is happening: durable role grants and tenant memberships are shown as
separate lifecycle records.

Why this matters: revoking a role and suspending a membership are different
administrative decisions with different audit trails.

8. Inspect Invitations, Access History, and Membership Audit.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: scroll to the bottom sections.

Actions: confirm Invitations display Email, Hash, Tenant, Roles, Status, and
Expires. Confirm Access History displays Time, Action, Decision, Reason, and
Trace. Confirm Membership Audit displays Created, Action, Decision, Summary,
and Trace.

Expected: no raw submitted email, no password, no token, and no raw Auth0
subject appears in these sections.

What is happening: access decisions and membership audit records are projected
into safe reviewer summaries.

Why this matters: support and security reviewers need evidence of changes and
denials without expanding sensitive payloads.

9. Switch to Acme tenant admin.

Page URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111`

Navigation path: open the local login page again and click
`tenant-admin-acme`.

Actions: wait for redirect to Membership Administration with the Acme tenant
id in the query string.

Expected: the scope label says `Tenant 11111111-1111-1111-1111-111111111111`
and the page lists only Acme-scoped membership data.

What is happening: tenant admin requests are forced to their own tenant scope.

Why this matters: tenant admins must not inspect or mutate other tenants.

10. Try a tenant-admin invitation.

Page URL:
`http://127.0.0.1:8000/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111`

Navigation path: use the Create Invitation form.

Actions: enter `acme.ui.qa018@example.test`, set idempotency key
`qa018-ui-acme`, select `tenant_user`, and submit.

Expected: the page redirects back to the same tenant-scoped URL, and the
Invitations table shows a masked Acme invite.

What is happening: an Acme tenant admin creates an Acme-scoped invite.

Why this matters: tenant self-service works for permitted tenant roles.

11. Confirm cross-tenant denial through the browser or API note.

Page URL:
`http://127.0.0.1:8000/admin/memberships?tenant_id=22222222-2222-2222-2222-222222222222`

Navigation path: while signed in as `tenant-admin-acme`, navigate directly to
the Globex URL.

Actions: capture the resulting page or browser error as
`/tmp/qa018-ui-cross-tenant-note.txt`.

Expected: access is denied and the page does not show Globex membership rows.

What is happening: the route compares the selected tenant id with the
principal's tenant id and fails closed.

Why this matters: the UI must not allow an Acme admin to infer Globex users.

12. Collect reviewer evidence.

Page URL: `http://127.0.0.1:8000/admin/memberships`

Navigation path: return to platform admin if needed.

Actions: save screenshots for local login, platform page, Acme tenant page,
and denied Globex attempt. Save notes under `/tmp/qa018-ui-reviewer-notes.txt`.

Expected: screenshots contain only masked emails and safe summaries.

What is happening: this creates a record that can be attached to PR review.

Why this matters: QA018 acceptance includes browser-visible proof, not just
unit tests.

## Required Automated Evidence

Run focused UI and membership tests:

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_memberships_ui.py \
  tests/integration/api/test_admin_memberships_api.py \
  tests/unit/api/test_membership_ui_models.py \
  tests/unit/admin/memberships \
  tests/docs/test_membership_administration_docs.py
```

Expected: focused tests pass.

Run required quality commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality gates pass.

Run the configured Playwright flow:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml --start-processes
```

Expected: Playwright captures `01-local-login.png`,
`02-user-tenant-membership-administration-target.png`, and
`03-user-tenant-membership-administration-direct-target.png` under
`output/playwright/qa018_ui`.

## UI Evidence Checklist

- Expected: local login screenshot shows `platform-admin`.
- Expected: platform page screenshot shows `Membership Administration`.
- Expected: summary cards show current scope, active principals, invitations,
  and active grants.
- Expected: Create Invitation form has Email, Idempotency key, role checkboxes,
  and Invite button.
- Expected: Principals table uses masked email or unavailable text.
- Expected: Role Grants table shows role codes and safe status pills.
- Expected: Tenant Memberships table shows tenant ids and status actions.
- Expected: Invitations table shows masked email and hash only.
- Expected: Access History and Membership Audit show trace ids and summaries.
- Expected: Acme tenant admin cannot view Globex scope.

## Acceptance Notes Template

```text
QA018 UI reviewer:
Date:
Browser:
Local login screenshot:
Platform page screenshot:
Acme tenant page screenshot:
Denied Globex evidence:
Redaction notes:
Tenant isolation notes:
Automated Playwright output:
Unexpected behavior:
```

Expected: every evidence item is filled out before review is marked complete.

## Troubleshooting

- Local login page does not show QA018 principals: copy `.env.qa018` to `.env`
  and restart the API server.
- Membership page returns 401: sign in with local login or clear stale cookies
  and sign in again.
- Membership page returns 403 as tenant admin: verify the URL uses the same
  tenant id as the selected local principal.
- Invitation form returns an error: use a valid email address and select only
  `tenant_user` or `tenant_admin` as a tenant admin.
- Tables are empty: seed data through the curl block in Environment Setup.
- Screenshots show raw email values: preserve the screenshot and treat it as a
  redaction regression unless the value is still inside the editable form field
  you are typing.
- Playwright cannot start the server: ensure PostgreSQL is running and the
  database was migrated.

## Related Files

- `specs/018-user-tenant-membership-administration/qa018.md`
- `specs/018-user-tenant-membership-administration/.env.qa018`
- `specs/018-user-tenant-membership-administration/qa018_user_guide.md`
- `src/multi_agent_platform/api/routers/admin_memberships.py`
- `src/multi_agent_platform/api/ui/memberships.py`
- `src/multi_agent_platform/web_admin/templates/memberships/index.html`
- `tests/integration/api/test_admin_memberships_ui.py`
- `specs/_autopilot/018-user-tenant-membership-administration/validation.yml`
