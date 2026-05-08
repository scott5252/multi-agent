# Reviewer Notes: Spec 054 Membership And Access React Live Data

## Scope

Spec 054 replaces deterministic membership React data with live repository and
service-backed projections for directory rows, invitations, memberships, role
grants, access history, support overrides, and audit evidence.

## Implementation Notes

- Membership route builders now depend on `MembershipRepository` and
  `MembershipAdministrationService`.
- The membership dashboard includes provenance, truthful empty-state metadata,
  and support override summaries.
- Membership mutation builders use durable services for invitations, role
  grants, principal links, and status actions.
- Frontend membership panels render live support override evidence and consume
  regenerated TypeScript contracts.
- Scanner guardrails now treat old QA034 membership markers as blocking in
  production membership surfaces.

## QA Notes

- QA environment: `specs/054-membership-and-access-react-live-data/.env.qa054`
- Seed script: `scripts/qa/seed_membership_qa054.py`
- Post-UI verifier: `scripts/qa/verify_membership_qa054.py`
- Main browser route: `/admin/app/memberships`
- Playwright action: sign in as `tenant-admin-acme`, click `Invite`, and verify
  `Invitation created in persisted membership state.`

## Safety Notes

- No real provider calls are used.
- No real Telegram calls are used.
- QA secrets use the `qa054/` static reference prefix.
- Browser and API output must not include raw emails, full subjects, provider
  tokens, credential values, local paths, stack traces, or unauthorized tenant
  labels.

## Commit Notes

No intermediate commit is required for this spec. The autopilot is intentionally
continuing in the dirty worktree until the full remove-mock-data sequence is
complete and the user commits.
