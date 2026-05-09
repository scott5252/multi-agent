# Contract: Coordinator UI Expectations

Spec 062 is backend-first. The dedicated React workspace arrives in Spec 063.

Browser-visible evidence for this spec uses:

- `GET /openapi.json`
- `GET /admin/design-reviews/sessions`
- `GET /admin/design-reviews/sessions/{session_id}/coordinator`
- Playwright screenshot of the OpenAPI document

Future UI state must be backed by the coordinator API responses:

- Active revision summary and digest
- Round history and runtime run id
- Reviewer assignments
- Reviewer verdicts
- Quorum decision and safe rationale
- Manual-resolution state and allowed actions
- Development handoff state

UI must not:

- invent reviewer rows
- invent handoff success
- show raw prompts or completions
- show provider payloads
- show credentials or authorization headers
- hide manual-resolution state behind a generic failure

Empty states must be truthful and tenant-scoped.
