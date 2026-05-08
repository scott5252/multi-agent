# UI Contract: Membership And Access React Live Data

## Route Family

- `/admin/app/memberships` serves the React membership workspace.
- `/admin/app/memberships/bootstrap.json` returns the dashboard envelope consumed by `MembershipPage`.
- Mutation endpoints for invitations, principal linking/status, role grants, role grant revocation, and membership status return `MembershipMutationResult`.
- `/admin/app/memberships/access-history.json` and `/admin/app/memberships/audit.json` return bounded live lists for detail panels.

## Required UI States

- **Live seeded state**: Directory, invitations, role grants, status actions, access history, support override evidence, and audit timeline render persisted records for the authorized scope.
- **Empty state**: Fresh qa054 database renders no rows and displays truthful empty or unavailable summaries for every panel.
- **Denied state**: Cross-tenant or unauthorized requests return safe problem details or denied membership states without names, email details, tenant labels, grants, audit payloads, or counts from the forbidden scope.
- **Mutation accepted/replayed**: A visible result panel shows persisted invitation, grant, principal, or membership evidence with masked identity details and audit reference.
- **Mutation stale/denied/unavailable**: The UI shows safe field errors, conflict summaries, confirmation requirements, or unavailable state without claiming success.

## Rendering Rules

- The browser may sort, filter, and navigate already-authorized data, but it must not decide authorization, tenant scope, role eligibility, replay status, revision validity, redaction, or audit visibility.
- Full emails, raw external subjects, raw IdP claims, tokens, secrets, local paths, stack traces, raw audit payloads, full Telegram identifiers, and unauthorized tenant labels must not appear in DOM text, screenshots, or exported artifacts.
- Empty arrays remain empty; the frontend must not inject fixture users, invitations, grants, decisions, support overrides, or audits.
- All visible actions use backend-provided `AdminAction` metadata and post to backend-owned endpoints.

## QA Interaction Contract

- Playwright loads the membership workspace with local-principal authentication.
- The flow creates or replays a tenant invitation through the visible invitation form.
- The flow verifies the mutation result panel, refreshed invitation list, and absence of raw sensitive strings.
- Post-UI verification confirms persisted invitation and audit evidence through the backend API or a redaction-safe qa054 database query.
