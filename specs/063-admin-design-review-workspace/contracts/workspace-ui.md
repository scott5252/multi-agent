# Contract: Admin Design Review Workspace UI

## Route

- `/admin/app/design-reviews`

## Primary Panels

- Header with active-scope context and live-data provenance.
- Summary cards for total sessions, reviewing sessions, manual-resolution sessions, and approved handoffs.
- Create-session form with request summary, quorum policy, workflow option, and submit action.
- Session list with status, active revision, quorum policy, workflow reference, and selection control.
- Selected-session detail with revision summaries, round history, verdict summaries, quorum decision, manual decisions, and handoff reference.
- Manual-resolution form shown only for manual-resolution sessions.

## States

- Loading: while the envelope is requested.
- Empty: when no sessions exist for the tenant.
- Denied: when active scope cannot access tenant records.
- Validation error: when create/manual inputs fail.
- Dependency unavailable: when the backend envelope cannot be loaded.

## Accessibility

- All controls have visible labels or accessible names.
- Session selection is keyboard reachable.
- Mutation results are announced through visible status panels.
- Tables use semantic headers.
- Forms preserve focus and do not rely on color alone.
