# UI Contract: Workflow Registry React Parity

## Canonical Routes

- `/admin/app/workflows`: React workflow registry and builder entry.
- `/admin/app/workflows/new`: React create workflow state.
- `/admin/app/workflows/drafts/{workflow_draft_id}`: React draft editing state.
- `/admin/app/workflows/drafts/{workflow_draft_id}/validate`: React validation state or mutation result.
- `/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate`: React publish-gate state.
- `/admin/app/workflows/drafts/{workflow_draft_id}/revisions`: React revision history state.
- `/admin/app/workflows/versions/{workflow_version_bundle_id}`: React published version detail.

## Legacy Route Behavior

- `/admin/workflows/ui` redirects to `/admin/app/workflows`.
- `/admin/workflows/new` redirects to `/admin/app/workflows/new`.
- `/admin/workflows/drafts/{workflow_draft_id}/editor` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}`.
- `/admin/workflows/drafts/{workflow_draft_id}/revisions/ui` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}/revisions`.
- `/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate`.
- `/admin/workflows/versions/{workflow_version_bundle_id}/detail` redirects to `/admin/app/workflows/versions/{workflow_version_bundle_id}`.
- Legacy POST form actions return backend JSON or non-Jinja problem responses when a browser redirect would hide validation or stale-conflict state.

All redirects preserve authorized `tenant_id`, filters, saved-filter intent, workflow ids, draft ids, revision ids, publish-gate anchors, and safe return intent when unambiguous.

## Required UI States

- Loading
- Empty workflow registry
- Workflow list with filters and saved-filter entry
- Create workflow
- Draft edit with dirty/stale markers
- Field help
- Reference picker
- Graph preview with keyboard-readable node and edge lists
- Validation panel
- Publish gate with required evidence
- Revision history
- Published version detail
- Sharing state
- Stale conflict recovery
- Denied
- Dependency unavailable
- Legacy route retired/gone

## Redaction Rules

The UI must not display raw secrets, credential values, provider authorization headers, private channel messages, raw prompts, raw completions, memory contents, raw run payloads, raw tool payloads, raw test transcripts, full Telegram identifiers, post-creation link tokens, local filesystem paths, stack traces, or unauthorized tenant labels.

## Accessibility Rules

- Graph nodes and edges must be inspectable through keyboard-readable lists.
- Publish blockers and validation findings must have text equivalents linked to affected sections.
- Create, save, validate, publish, copy, restore, and share actions must expose disabled, busy, accepted, stale, denied, and unavailable states without layout shift.
- Direct-link recovery and denied/unavailable responses must include safe next actions.
