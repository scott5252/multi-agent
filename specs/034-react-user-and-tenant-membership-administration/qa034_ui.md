# QA034 UI Walkthrough

## Goal

QA034 UI validation proves the React membership administration page renders a safe user directory, invitation flow, principal link flow, role grant workflow, status actions, access history, audit evidence, and tenant-scoped denied states.

The route under review is /admin/app/memberships.

The browser should show the membership workspace as the first usable screen.

The browser should show sections for Overview, Directory, Invitations, Role grants, Status, Access history, and Audit.

The browser should show display names, masked email values, safe subject suffixes, tenant labels, role labels, status badges, and next-request effect messages.

The browser should not make raw identifiers the primary experience.

The browser should not show qa034-secret-value, raw email, full subject, authorization header, provider token, credential value, private message, local filesystem path, or unauthorized tenant label.

Expected: platform screenshots can show authorized Acme and Globex labels.

Expected: tenant screenshots show Acme only.

Expected: no screenshot contains qa034-secret-value.

Expected: no screenshot contains raw email.

Expected: no screenshot contains full subject.

Expected: no screenshot contains authorization header.

Expected: no screenshot contains provider token.

Expected: no screenshot contains credential value.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from .env.qa034.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, confusing role labels, or tenant-scope uncertainty.

Do not paste secrets into the browser.

Do not paste unmasked identity values into reviewer notes.

Do not paste full external subjects into reviewer notes.

Expected: QA evidence can be shared with reviewers without cleanup.

Expected: every action is explicit and user initiated.

What is happening: the browser exercises the same React route administrators use for membership administration.

Why this matters: UI validation catches layout, focus, and unsafe presentation issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/034-react-user-and-tenant-membership-administration/.env.qa034 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa034 && createdb -U postgres multi_agent_platform_qa034'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa034 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa034-artifacts output/playwright/qa034_ui
```

Expected: database, React assets, and evidence folders are ready.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: worker starts without live provider, Telegram, credential, email, or connector calls.

Open the local browser login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Expected: local login offers platform-admin and tenant-admin-acme.

## Browser Walkthrough

### Step 1: Denied Membership Route

Open:

```text
http://127.0.0.1:8000/admin/app/memberships
```

Expected: a 401 response appears when not logged in.

Expected: no directory, invite, role, status, history, or audit data appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: membership information cannot leak anonymously.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-denied.png.

### Step 2: Platform Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Choose platform-admin.

Expected: the browser redirects to /admin/app/memberships.

Expected: the shell shows React Admin.

Expected: the page heading says Membership Administration.

Expected: the directory shows Maya Chen.

Expected: the page shows masked email m***@example.test.

Expected: the page shows authorized Acme and Globex tenant labels.

What is happening: the platform principal can review authorized cross-tenant membership summaries.

Why this matters: platform support workflows need broad visibility without unsafe identity display.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-platform.png.

### Step 3: Invitation Replay

Click Invite.

Expected: the page shows Invitation replayed with original audit evidence.

Expected: the page shows audit-membership-qa034-invite-replayed.

Expected: the page shows i***@example.test.

Expected: the page does not show an unmasked invitation address.

What is happening: React submits a backend-owned invite payload with an idempotency key.

Why this matters: repeated invites must not create duplicate invitation rows.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-invite.png.

### Step 4: Principal Link And Role Grant

Click Link.

Expected: the page shows Principal identity linked with safe subject evidence.

Click Grant.

Expected: the page shows Role grant saved with backend eligibility evidence.

Click Revoke.

Expected: the page shows Role grant revoked with safe audit evidence.

What is happening: React posts identity and grant actions to server-owned membership routes.

Why this matters: role eligibility and identity linking must remain backend decisions.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-role.png.

### Step 5: Status Actions

Click Suspend.

Expected: the page shows Principal suspend action saved with audit evidence.

Click Remove membership if available.

Expected: the page shows Tenant membership status saved with audit evidence.

Expected: the page shows next protected request effect copy.

What is happening: access-changing actions use explicit backend confirmation payloads.

Why this matters: durable access decisions need clear review and audit evidence.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-status.png.

### Step 6: Access History And Audit

Review Access history.

Expected: the page shows Open membership workspace.

Expected: the page shows Assign platform role as a denied action.

Review Audit.

Expected: the page shows invitation_replayed.

Expected: the page shows role_grant_revoked.

What is happening: recent decisions and audit records are rendered as safe summaries.

Why this matters: administrators need explainability without unsafe identifiers.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-history.png.

### Step 7: Tenant Login And Cross-Tenant Denial

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships?tenant_id=11111111-1111-1111-1111-111111111111
```

Choose tenant-admin-acme.

Expected: the page shows Acme.

Expected: the page does not show Globex.

Expected: the role grant workflow does not offer platform roles.

Expected: an attempted platform role grant returns validation_error.

What is happening: the tenant principal sees only tenant-scoped membership summaries.

Why this matters: tenant self-service must fail closed for cross-tenant and platform-only actions.

Screenshot evidence: output/playwright/qa034_ui/qa034-react-memberships-tenant.png.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/034-react-user-and-tenant-membership-administration
```

Run backend quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Run full QA034 validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml --start-processes
```

Expected: all automated commands pass before screenshots are accepted.

What is happening: the QA034 manifest resets the database, builds assets, starts app processes, and captures screenshots.

Why this matters: manual observations should match automated evidence.

## UI Evidence Checklist

- Denied screenshot captured.
- Platform screenshot captured.
- Invitation screenshot captured.
- Role screenshot captured.
- Status screenshot captured.
- History screenshot captured.
- Tenant screenshot captured.
- No screenshot contains qa034-secret-value.
- No tenant screenshot contains Globex.
- No screenshot contains unmasked identity values.
- No screenshot contains authorization headers.
- No screenshot contains local filesystem paths.

Expected: every checklist item is true.

## Acceptance Notes Template

Record reviewer name.

Record browser and viewport.

Record screenshot filenames.

Record any keyboard focus issue.

Record any text clipping issue.

Record any confusing role label.

Record any unsafe evidence concern.

Record final pass or fail.

## Troubleshooting

If login does not redirect, use /auth/local-login directly.

If membership data does not load, check /admin/app/memberships/bootstrap.json.

If tenant scope shows Globex, stop and fix tenant filtering before approval.

If Invite does not update the page, inspect the network response for validation_error.

If Role grant does not update the page, confirm the selected role is eligible.

If screenshots are blank, rebuild React assets and rerun Playwright.

If QA docs validation fails, check required headings and Expected markers.

Expected: UI failures are reproducible with the local QA environment.

## Related Files

- specs/034-react-user-and-tenant-membership-administration/qa034.md
- specs/034-react-user-and-tenant-membership-administration/.env.qa034
- specs/034-react-user-and-tenant-membership-administration/qa034_user_guide.md
- frontend/admin/src/components/memberships/MembershipPage.tsx
- frontend/admin/src/components/memberships/UserDirectoryPanel.tsx
- frontend/admin/src/components/memberships/InvitationPanel.tsx
- frontend/admin/src/components/memberships/RoleGrantPanel.tsx
- frontend/admin/src/components/memberships/StatusActionsPanel.tsx
- frontend/admin/src/components/memberships/AccessHistoryPanel.tsx
- frontend/admin/src/components/memberships/MembershipAuditPanel.tsx
