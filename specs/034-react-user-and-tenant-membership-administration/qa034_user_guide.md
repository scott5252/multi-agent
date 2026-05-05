# QA034 User Guide: Spec 034 - React User And Tenant Membership Administration

## Detailed Overview

QA034 adds a React membership administration workspace to the admin console.

The workspace is available at `/admin/app/memberships`.

The existing server-rendered fallback remains available at `/admin/memberships`.

Platform administrators use this workspace to review users across authorized tenants.

Tenant administrators use this workspace to manage only their active tenant.

The page is a working administration surface, not a landing page.

The page groups membership work into overview, directory, invitations, principal linking, role grants, status actions, access history, and audit evidence.

The overview shows backend-owned readiness cards.

The directory shows display names instead of raw identifiers.

The directory shows masked email values.

The directory shows safe subject suffixes.

The directory shows tenant membership status.

The directory shows role summaries.

The invitation panel proves idempotent invite replay.

The principal panel proves safe external identity linking for authorized platform users.

The role grant panel proves platform and tenant role eligibility.

The status panel proves principal suspend/reactivate and tenant membership status actions.

The access history panel proves allow and deny evidence is bounded.

The audit panel proves membership actions are traceable without unsafe payloads.

Mutation results show status, summary, audit reference, and next-request effect copy.

Role changes take effect on the next protected request.

Principal status changes take effect on the next protected request.

Tenant membership status changes take effect on the next protected request.

Invitation replay returns original safe audit evidence instead of creating a duplicate.

Tenant administrators cannot assign platform roles.

Tenant administrators cannot inspect Globex data while scoped to Acme.

Tenant administrators cannot mutate Globex resources from Acme scope.

Authorized platform administrators may see Globex labels as part of platform review.

The page must not render `qa034-secret-value`.

The page must not render raw email addresses as the primary identity.

The page must not render full external subjects.

The page must not render authorization headers.

The page must not render provider tokens.

The page must not render credential values.

The page must not render private messages.

The page must not render raw prompts.

The page must not render raw completions.

The page must not render local filesystem paths.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA034 in a browser.

Use this guide if you are validating platform membership administration.

Use this guide if you are validating tenant-scoped self-service administration.

Use this guide if you are validating idempotent invitations.

Use this guide if you are validating principal linking.

Use this guide if you are validating role assignment and revocation.

Use this guide if you are validating principal suspension and reactivation.

Use this guide if you are validating tenant membership status changes.

Use this guide if you are validating access history and audit evidence.

Use this guide if you need plain-language evidence notes for a reviewer.

Developers should also run `qa034.md`.

UI reviewers should also run `qa034_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes `AUTH_MODE=local_principal`.

This guide assumes the QA database is `multi_agent_platform_qa034`.

## Manual QA Prerequisites

Confirm the repository is on the QA034 branch or an equivalent working tree.

Confirm the QA034 environment file exists at `specs/034-react-user-and-tenant-membership-administration/.env.qa034`.

Confirm Docker is available for PostgreSQL.

Confirm Node dependencies can be installed in `frontend/admin`.

Confirm Python dependencies can be installed with `uv sync`.

Copy the QA034 environment file before starting local validation.

```bash
cp specs/034-react-user-and-tenant-membership-administration/.env.qa034 .env
```

Build React assets before browser review.

```bash
cd frontend/admin
npm install
npm run build
```

Prepare the database and application as described in `qa034.md`.

Open local login when the app is running.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Keep screenshots under `output/playwright/qa034_ui`.

Keep API evidence under `/tmp/qa034-*`.

## Step-by-Step Manual QA

Start with platform administrator review.

Choose `platform-admin` on the local login page.

Expected result: the browser opens `/admin/app/memberships`.

Expected result: the page title is `Membership Administration`.

Expected result: the overview cards show directory, invitation, and access-history readiness.

Expected result: the directory includes `Maya Chen`.

Expected result: the directory includes `Jordan Lee`.

Expected result: masked email values are shown.

Expected result: safe subject suffixes are shown.

Expected result: Acme is visible.

Expected result: Globex is visible only because this is authorized platform review.

Open the directory section.

Expected result: tenant, role, status, and decision filters are visible.

Expected result: raw email addresses are not the primary identity.

Expected result: role labels are understandable.

Click `Invite`.

Expected result: the mutation result says the invitation was replayed or accepted.

Expected result: the result includes an audit reference.

Expected result: the result includes next-request effect copy.

Click `Link`.

Expected result: the mutation result says the principal identity was linked.

Expected result: the result shows safe subject evidence only.

Click `Grant`.

Expected result: the mutation result says the role grant was saved.

Expected result: the result includes backend eligibility evidence.

Click the first `Revoke` control.

Expected result: the mutation result says the role grant was revoked.

Expected result: the result includes a safe audit reference.

Click the first `Suspend` control.

Expected result: the mutation result says the principal suspend action was saved.

Expected result: the next-request effect explains when the change applies.

Click `Remove membership`.

Expected result: the mutation result says tenant membership status was saved.

Expected result: status changes remain audit-visible.

Review access history.

Expected result: allow and deny records are visible.

Expected result: trace references are safe.

Review the audit timeline.

Expected result: invite replay and role revoke audit references are visible.

Expected result: safe diff summaries are visible.

Switch to tenant administrator review.

Open local login again.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships?tenant_id=11111111-1111-1111-1111-111111111111
```

Choose `tenant-admin-acme`.

Expected result: the browser opens the React membership workspace in Acme scope.

Expected result: Acme is visible.

Expected result: Globex is not visible.

Expected result: platform-admin role choices are not visible.

Expected result: tenant role choices are visible.

Click `Invite`.

Expected result: tenant invite replay or creation succeeds for Acme roles.

Click `Grant`.

Expected result: tenant role grant succeeds only for permitted tenant roles.

Review access history.

Expected result: denied platform-role evidence is shown safely.

Review audit records.

Expected result: cross-tenant denial evidence does not reveal unauthorized tenant details.

## Expected Results

The React shell loads without routing back to a disabled-route fallback.

The React workspace is usable with mouse and keyboard.

The page has no overlapping text.

The page has no clipped button labels.

The page has no nested card layouts.

The page shows icons for invitation, principal link, grants, revocation, suspension, and reactivation controls.

The platform flow shows authorized platform scope.

The tenant flow shows only the active tenant.

The invite flow returns idempotency replay evidence.

The role grant flow returns backend-owned eligibility evidence.

The revoke flow returns audit evidence.

The status flow returns next-request effect copy.

The access history panel shows bounded safe records.

The audit panel shows safe summaries.

The UI never displays `qa034-secret-value`.

The UI never displays raw email as the primary identity.

The UI never displays a full external subject.

The UI never displays authorization headers.

The UI never displays provider tokens.

The UI never displays credential values.

## Evidence To Capture

Capture a screenshot of the platform dashboard.

Capture a screenshot after the invite action.

Capture a screenshot after the role grant or revoke action.

Capture a screenshot after a status action.

Capture a screenshot of access history.

Capture a screenshot of the audit timeline.

Capture a screenshot of the Acme tenant view.

Record the local login principal used for each screenshot.

Record whether the page used `/admin/app/memberships`.

Record whether any unsafe text appeared.

Record whether tenant isolation passed.

Record whether reviewer notes match the automated evidence in `qa034.md`.

## Security And Redaction Checks

Search screenshots and API evidence for the QA034 fake secret marker.

```bash
rg -n "qa034-secret-value" /tmp/qa034-* output/playwright/qa034_ui || true
```

Search for unsafe identity and credential labels.

```bash
rg -n "raw email|full subject|authorization header|provider token|credential value|private message|full external subject" /tmp/qa034-* output/playwright/qa034_ui || true
```

Expected result: both searches return no unsafe evidence.

Authorized platform evidence may include the tenant label `Globex`.

Tenant-scoped evidence for Acme must not include `Globex`.

## Tenant Isolation Checks

Use `tenant-admin-acme` for the tenant isolation pass.

Confirm the tenant URL includes the Acme tenant ID.

Confirm Acme appears in the directory, history, and audit records.

Confirm Globex does not appear in the tenant dashboard.

Confirm Globex does not appear in tenant screenshots.

Confirm a platform-role grant attempt returns a safe denial.

Confirm a cross-tenant invite attempt returns a safe denial in API evidence.

Confirm the denial text does not reveal unauthorized tenant details.

Confirm raw identifier detail is not available to tenant administrators.

Confirm tenant administrators can still perform permitted Acme invite and role actions.

## Troubleshooting

If the page shows `React admin unavailable`, confirm the API process is running.

If the page redirects to login, choose a local principal again.

If the page loads without React styles, rebuild frontend assets.

If the membership data does not load, check `/admin/app/memberships/bootstrap.json`.

If tenant data looks cross-scoped, confirm the URL includes the Acme tenant ID.

If Globex appears in an Acme tenant screenshot, treat it as a blocker.

If a mutation result is missing an audit reference, treat it as a blocker.

If unsafe text appears in screenshots or `/tmp/qa034-*`, delete the unsafe evidence and fix the source.

If the database fails to migrate, recreate only `multi_agent_platform_qa034`.

If another QA database is selected, stop and correct `.env`.

If browser clicks miss controls, use the visible button labels from `qa034_ui.md`.

If local login is unavailable, confirm `AUTH_MODE=local_principal`.
