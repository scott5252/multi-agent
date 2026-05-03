# QA018 User Guide: User And Tenant Membership Administration

## Detailed Overview

Membership Administration is the admin console area for managing who can use
the platform and which tenant or platform roles they hold. Platform
administrators can see all tenants and can manage Auth0-backed identities,
local-principal test identities, platform role grants, tenant role grants,
principal suspension, tenant membership status, invitations, and safe access
history.

Tenant administrators get a narrower version of the same workflow. They can
invite users to their own tenant, assign permitted tenant roles, remove or
suspend tenant memberships, and view tenant-scoped user status. They cannot
assign platform roles, cannot manage another tenant, and cannot inspect another
tenant's users by guessing URLs or identifiers.

The feature does not store passwords. Auth0 remains the identity provider for
real authentication, while local-principal mode remains available for local QA.
The admin surface stores identity references and role/membership metadata. It
renders masked email addresses, safe subject labels, role codes, status values,
trace ids, and summaries.

## Who Should Use This Guide

Use this guide if you are reviewing the feature manually and do not need to
understand the full codebase. You should be comfortable opening a browser,
copying commands from a terminal guide, and recording whether the screen
matches the expected result.

Platform administrators should use the `platform-admin` local login principal.
Tenant administrators should use `tenant-admin-acme` first. Use
`tenant-admin-globex` only when checking tenant isolation.

## Manual QA Prerequisites

1. Ask the implementer to prepare the QA018 environment from
   `specs/018-user-tenant-membership-administration/.env.qa018`.
2. Confirm the API is running at `http://127.0.0.1:8000`.
3. Confirm the dedicated database is `multi_agent_platform_qa018`.
4. Confirm any evidence files are saved under `/tmp/qa018-*` or
   `output/playwright/qa018_ui`.
5. Use a clean browser session or clear the local QA cookie if switching roles
   produces confusing results.

Expected result: local login and Membership Administration are reachable
without real Auth0 credentials.

## Step-by-Step Manual QA

1. Open local login at
   `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships`.

Expected result: the page title says `Local Login`, and the list includes
`platform-admin`.

2. Select `platform-admin`.

Expected result: the browser redirects to `/admin/memberships` and the page
heading says `Membership Administration`.

3. Review the summary area at the top of the page.

Expected result: you see current scope, active principals, invitations, and
active grants.

4. Read the notice under the page heading.

Expected result: it explains that the page shows masked emails, safe subject
labels, role codes, status, trace ids, and audit summaries only.

5. Locate the Create Invitation form.

Expected result: it has Email, Idempotency key, tenant role checkboxes, and an
Invite button.

6. Create a test invitation with an address such as
   `manual.qa018@example.test`.

Expected result: the page refreshes and the invitation appears with masked
email text and a hash, not the full address.

7. Submit the same invitation again with the same idempotency key.

Expected result: the visible invitation evidence remains a single active
invitation rather than a pile of duplicates.

8. Scroll to Principals.

Expected result: rows show display names, masked email values or unavailable
text, safe subject labels, provider names, and active or suspended status.

9. Review platform actions in the Principals table.

Expected result: platform scope offers Suspend or Reactivate actions depending
on the status.

10. Review the Create Role Grant form.

Expected result: the form lets the platform admin pick a principal, scope, and
role. Invalid combinations are rejected by the server even if the selector can
display them.

11. Review Role Grants.

Expected result: role code, scope, tenant, status, and Revoke action are clear.

12. Review Tenant Memberships.

Expected result: tenant memberships show tenant id, status, source, and
Suspend, Restore, or Remove controls as appropriate.

13. Review Invitations.

Expected result: invitation rows show masked email, hash, tenant, roles,
status, and expiration.

14. Review Access History.

Expected result: history rows show action, decision, reason, trace id, and
time without raw secrets.

15. Review Membership Audit.

Expected result: audit rows show action, decision, summary, trace id, and
safe metadata.

16. Switch to `tenant-admin-acme` using local login with redirect to
   `/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111`.

Expected result: the page says the current scope is the Acme tenant id.

17. Create an Acme invitation as tenant admin.

Expected result: tenant-scoped invitation succeeds when requested roles are
`tenant_user` or `tenant_admin`.

18. Try to browse directly to the Globex scope while still signed in as Acme:
   `/admin/memberships?tenant_id=22222222-2222-2222-2222-222222222222`.

Expected result: access is denied or the request fails closed without listing
Globex membership data.

19. Try to assign a platform role through API evidence or a controlled form
   test as tenant admin.

Expected result: the request is denied.

20. Return to platform admin and confirm the audit table includes safe
   summaries for allowed and denied actions.

Expected result: audit entries explain what happened without showing raw email
addresses, passwords, tokens, or full Auth0 subject strings.

## Expected Results

Successful QA means the browser and API agree on these outcomes:

- Platform admin can open Membership Administration.
- Tenant admin can open Membership Administration only for their tenant.
- Invitations are created with masked email evidence.
- Replaying the same active invitation is idempotent.
- Auth0 subject linking stores safe identity references and no passwords.
- Platform admin can create and revoke platform or tenant role grants.
- Tenant admin can assign only tenant roles in their own tenant.
- Tenant admin cannot inspect or mutate another tenant.
- Principal suspension and reactivation are visible in the next request path.
- Role changes, denials, and membership updates create audit-safe records.
- Access history shows safe action, decision, reason, and trace evidence.

## Evidence To Capture

Capture these artifacts:

- Screenshot of local login showing QA018 principals.
- Screenshot of platform Membership Administration page.
- Screenshot of Acme tenant-scoped Membership Administration page.
- Screenshot or note for the denied Globex attempt.
- Screenshot of invitation rows showing masked email and hash.
- Screenshot of Access History and Membership Audit rows.
- Terminal evidence files under `/tmp/qa018-*`.
- Playwright screenshots under `output/playwright/qa018_ui`.

Write a short note for each screenshot that states which principal was signed
in, which URL was open, and what expected result it proves.

## Security And Redaction Checks

Look carefully for these unsafe values:

- Full submitted email addresses in tables, audit summaries, or screenshots.
- Password fields or password storage prompts.
- Raw Auth0 subject values where a masked subject should appear.
- Access tokens, API keys, or authorization headers.
- Tenant data from another tenant.
- Stack traces or internal exception details in normal denial flows.

Expected result: visible data uses masked emails, hashes, safe subject labels,
role codes, status, trace ids, and summaries. Editable input fields may show
what the reviewer is typing, but persisted rows should not show raw values.

## Tenant Isolation Checks

Use Acme and Globex for isolation:

1. Sign in as `tenant-admin-acme`.
2. Open the Acme Membership Administration URL.
3. Confirm Acme scoped data is visible.
4. Change the URL tenant id to Globex.
5. Confirm the request is denied or fails closed.
6. Try to create an invitation for Globex through API evidence if available.
7. Confirm the response is denied.

Expected result: Acme admins do not see Globex users, memberships,
invitations, role grants, access history, or audit records.

## Troubleshooting

- If local login does not list QA018 principals, restart the API after copying
  `.env.qa018` to `.env`.
- If the page is empty, ask the implementer to run the seed steps in
  `qa018.md` or create an invitation from the form.
- If a tenant admin sees platform actions, confirm which principal is currently
  signed in.
- If a tenant admin can open another tenant's URL, record it as a security
  regression.
- If screenshots show raw email values outside an input field, record it as a
  redaction regression.
- If Playwright screenshots differ from manual screenshots, prefer the manual
  notes and attach both for review.
- If Docker or PostgreSQL is unavailable, mark environment setup blocked and
  do not mark the feature accepted until database-backed checks run.

