# Contract: Admin Design Review Workspace API

## GET `/admin/app/design-reviews`

Returns the React admin shell host for the design-review workspace.

## GET `/admin/app/design-reviews/bootstrap.json`

Query:

- `tenant_id` optional UUID. Required when the active principal can choose scope.
- `session_id` optional UUID. Selects a session detail when it belongs to scope.

Response `200`:

```json
{
  "title": "Design reviews",
  "description": "Live council sessions, rounds, decisions, and handoffs.",
  "state": {"state": "empty", "title": "No design reviews", "summary": "..."},
  "sessions": [],
  "selected_session": null,
  "workflow_options": [],
  "quorum_policies": [
    {"policy_key": "four_of_five_no_blockers", "label": "Four of five, no blockers"}
  ],
  "actions": {"create_session_href": "/admin/design-reviews/sessions"}
}
```

Response `403`:

```json
{"detail": "tenant scope required"}
```

## POST `/admin/design-reviews/sessions`

Existing design-review session API. The workspace uses it for create-session
actions and reloads the envelope after success.

## POST `/admin/design-reviews/sessions/{session_id}/coordinator/launch-round`

Existing coordinator launch API. The workspace uses it when a selected session
has an authorized workflow bundle.

## POST `/admin/design-reviews/sessions/{session_id}/coordinator/manual-decisions`

Existing coordinator manual-decision API. The workspace uses it only when
manual resolution is required.
