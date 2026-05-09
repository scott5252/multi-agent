# Contract: Design Reviewer Council Template UI

## Workspace Placement

The Design Review Admin workspace shows a template setup panel before the
session list. The panel is backed by `template_setup` from
`/admin/app/design-reviews/bootstrap.json`.

## Required States

- `not_installed`: Shows the safe summary and an install action for authorized
  admins. The session list remains live and may be empty.
- `evidence_pending`: Shows workflow draft identifiers and a pending evidence
  status.
- `evidence_failed`: Shows a safe blocking summary and does not present the
  template as ready.
- `stale`: Shows that current workflow draft evidence must be refreshed.
- `ready`: Shows current required evidence and publish readiness.
- `published`: Shows the published template summary when publish state is
  available from workflow registry.
- `denied`: Shows safe problem details without leaking template identifiers.

## Interaction Requirements

- Authorized admins can trigger the install action from the panel.
- The action sends tenant scope, a deterministic idempotency key for local QA,
  and safe-mode defaults.
- After success, the workspace refreshes from backend state.
- Error states render safe problem details and keep existing live session data
  visible when permitted.

## Copy Guardrails

- Visible UI copy must not claim setup succeeded unless the backend reports
  installed, ready, or published state.
- Visible UI copy must not mention internal test fixtures as production data.
- UI must not display raw prompts, completions, secrets, provider payloads,
  private channel messages, memory contents, unauthorized payloads, or raw
  external tool payloads.
