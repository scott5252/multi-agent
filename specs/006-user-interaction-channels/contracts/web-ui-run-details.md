# Web UI Run Details Contract

## Routes

| Route | Behavior |
|-------|----------|
| `GET /runs` | Lists recent authorized runs with run id, state, updated time, and quick filters. |
| `GET /runs/new` | Shows a workflow invocation form for workflows the user may start. |
| `POST /runs` | Starts a run through the same channel facade as the REST API. |
| `GET /runs/{run_id}` | Shows the run details page. |
| `GET /runs/{run_id}/events` | Streams status and timeline updates with SSE. |

## Run Details View Model

The page receives the same domain shape as `RunStatusResponse` plus:

- `timeline.items`: latest redacted timeline events
- `result`: current `RunResultResponse` when available or requested
- `artifacts.items`: artifact metadata and download actions
- `subscription`: current notification subscription state
- `callbacks.items`: callback registrations and delivery status for
  API-originated runs when the viewer is authorized
- `support.trace_id`: trace correlation value for support and operators

## Live Update Behavior

1. The page attempts SSE with `Last-Event-ID` support.
2. If SSE is unavailable or disconnects, the page polls status and timeline.
3. Polling begins at 2 seconds, backs off to 10 seconds while active, and stops
   when the run is terminal unless the user manually refreshes.
4. The last persisted status remains visible during reconnects.
5. Connection loss never changes the displayed lifecycle state to failed.

## Waiting Prompt Behavior

When a run is `waiting-for-input` and the user is authorized:

- Show prompt summary, redacted context, deadline when present, and available
  actions.
- Submit approval, rejection, resume, or cancellation with idempotency key and
  prompt version.
- Disable action controls after the first accepted response.
- If a stale response is rejected, refresh and show the latest status.

Unauthorized users may see that the run is waiting only when their permissions
allow status visibility; prompt context and actions are hidden otherwise.

## Result And Artifact Behavior

- Completed runs show final result summaries and structured result content when
  authorized.
- Failed and canceled runs show terminal summaries with no unavailable result
  body.
- Artifact rows show name, user-facing type, size when known, status, and a
  download action.
- Download actions request a fresh short-lived URL and never expose object
  storage references directly in the template.

## UX Considerations

- The run id is always copyable and visible in the first viewport.
- State labels use exactly the shared lifecycle names.
- Error banners are concise and mapped from shared error categories.
- Operator details such as trace id, callback attempts, and delivery failures
  are visible but redacted.
- Terminal notification state is visible so users can tell whether they are
  subscribed and whether delivery was attempted.
