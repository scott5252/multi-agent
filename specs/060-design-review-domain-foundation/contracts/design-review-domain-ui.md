# UI Contract: Design Review Domain Foundation

## Backend-Only Scope

Spec 060 does not add the Admin design review workspace. The UI contract here is
a route and state contract for later specs and QA reviewers.

## Route Families

- `POST /admin/design-reviews/sessions`
- `GET /admin/design-reviews/sessions`
- `GET /admin/design-reviews/sessions/{session_id}`
- `GET /admin/design-reviews/sessions/{session_id}/revisions`
- `GET /admin/design-reviews/sessions/{session_id}/rounds`
- `GET /admin/design-reviews/rounds/{round_id}`
- `GET /admin/design-reviews/rounds/{round_id}/quorum-decision`
- `GET /admin/design-reviews/sessions/{session_id}/manual-decisions`
- `POST /admin/design-reviews/sessions/{session_id}/manual-decisions`
- `GET /admin/design-reviews/sessions/{session_id}/handoff`

## Principals

- `tenant-admin-acme`: may create and inspect Acme design review records.
- `tenant-admin-globex`: may inspect only Globex records and receives truthful
  empty or denied states for Acme records.
- `platform-admin`: may inspect tenant-scoped records only with explicit tenant
  context.
- Auth0-shaped tenant and platform principals must exercise equivalent
  authorization decisions in integration tests.

## Empty And Denied States

- No sessions: return an empty session list with source/provenance metadata.
- Session has no rounds: return an empty rounds collection, not synthetic rows.
- Session has no handoff: return a pending or absent handoff state.
- Cross-tenant access: fail closed without confirming that another tenant's
  record exists.
- Unauthorized access: 401 or 403 using existing admin API conventions.

## Redaction Rules

Responses, logs, screenshots, docs, and curl output must not include:

- raw prompts or completions
- secrets, credential values, or provider authorization headers
- provider request/response payloads
- private channel messages
- memory contents
- unauthorized tenant labels
- raw external tool payloads
- raw artifact bodies, storage URLs, `file:` URIs, or local paths
- stack traces

## QA060 Review Flow

1. Create an Acme session as `tenant-admin-acme`.
2. Retry creation with the same idempotency key and confirm replayed session
   metadata with no duplicate revision.
3. List Acme sessions and open session detail.
4. Fetch revision, rounds, quorum decision, manual decision, and handoff route
   families and confirm truthful empty states where later specs have not added
   records.
5. Attempt Acme access as `tenant-admin-globex` and confirm fail-closed denial.
6. Run repository/service verifiers for immutable verdict, quorum, manual
   decision, and handoff evidence.
