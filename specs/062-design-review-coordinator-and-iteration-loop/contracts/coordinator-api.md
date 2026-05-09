# Contract: Design Review Coordinator API

## GET /admin/design-reviews/sessions/{session_id}/coordinator

Returns a live coordinator state projection for one tenant-scoped session.

Query:

- `tenant_id`: UUID

Response fields:

- `state.kind`: `ready`, `pending`, `empty`, `denied`, or `unavailable`
- `session`: existing `DesignReviewSessionResponse`
- `active_revision`: current revision response or null
- `latest_round`: latest round response or null
- `latest_quorum_decision`: quorum decision response
- `handoff`: handoff response
- `manual_resolution_required`: boolean
- `next_action`: safe action hint

## POST /admin/design-reviews/sessions/{session_id}/coordinator/launch-round

Launches one coordinator round for the session active revision.

Request:

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "workflow_version_bundle_id": "33333333-3333-3333-3333-333333333333",
  "idempotency_key": "qa062-launch-round-1",
  "max_rounds": 3,
  "execution_mode": "deterministic",
  "reviewers": [
    {
      "reviewer_key": "product-fit",
      "role_key": "product-fit-reviewer",
      "enabled": true
    }
  ]
}
```

Response:

- `session`
- `round`
- `active_revision`
- `workflow_run_id`
- `replayed`
- `state`

HTTP status:

- `201` for new round
- `200` for idempotent replay
- `403` for tenant denial
- `404` for missing session
- `409` for invalid session state
- `422` for validation errors

## POST /admin/design-reviews/rounds/{round_id}/coordinator/complete

Records safe verdict evidence and evaluates quorum.

Request:

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "idempotency_key": "qa062-complete-round-1",
  "safe_synthesis_summary": "Council recommends handoff.",
  "next_revision_summary": "Revise spacing and hierarchy before the next round.",
  "verdicts": [
    {
      "reviewer_key": "product-fit",
      "verdict": "approved",
      "score": 5,
      "blocking_issue_count": 0,
      "safe_feedback_summary": "Product fit is ready.",
      "output_digest": "qa062-product-fit-digest"
    }
  ]
}
```

Response:

- `session`
- `round`
- `active_revision`
- `created_revision`
- `quorum_decision`
- `handoff`
- `state`
- `next_action`
- `replayed`

## POST /admin/design-reviews/sessions/{session_id}/coordinator/manual-decisions

Records and applies a manual decision.

Request:

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "round_id": "44444444-4444-4444-4444-444444444444",
  "decision_type": "revise",
  "safe_rationale": "Reviewer evidence was incomplete, so a focused revision is required.",
  "accepted_risk": false,
  "idempotency_key": "qa062-manual-revise",
  "next_revision_summary": "Manual revision requested after incomplete evidence."
}
```

Response:

- `manual_decision`
- `session`
- `active_revision`
- `created_revision`
- `handoff`
- `state`
- `next_action`
- `replayed`

## Error Contract

Coordinator errors use existing FastAPI problem behavior with safe detail text.
Errors never reveal cross-tenant existence, raw reviewer payloads, raw model
content, credentials, or provider payloads.
