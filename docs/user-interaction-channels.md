# User Interaction Channels

The channel layer exposes one shared workflow-run interaction model through
Web UI pages, Telegram webhook commands, and Web API endpoints. Channel adapters
normalize tenant, platform identity, action type, trace id, source request id,
and idempotency key before touching run state.

## Supported Channels

- **Web API**: `POST /runs`, status, timeline, SSE events, result, approval,
  cancel, subscription, callback, and artifact URL endpoints.
- **Web UI**: `GET /runs`, `GET /runs/new`, `POST /runs`, and
  `GET /runs/{run_id}` render the same run status, timeline, result,
  notification, callback, and artifact data.
- **Telegram**: `/start`, `/link`, `/run`, `/status`, `/approve`, `/reject`,
  `/resume`, `/cancel`, `/result`, `/artifacts`, `/subscribe`, `/watch`, and
  `/unwatch` route through the same facade after identity linking.

## Lifecycle

Channels expose exactly `queued`, `running`, `waiting-for-input`, `completed`,
`failed`, and `canceled`. Internal runtime states are mapped at the boundary so
clients can recover by run id without depending on worker-specific states.

## Identity And Authorization

Web UI and Web API requests reuse the existing Auth0 or local-principal
dependencies. Telegram requires a signed-in platform user to create a
short-lived one-time link token, then `/link <token>` associates the Telegram
chat and user with that platform identity. Protected Telegram commands are
denied until linking succeeds.

## Idempotency And Rate Limits

Duplicate-prone actions require `X-Idempotency-Key` or a channel-native
equivalent. Matching replays return the first accepted outcome; mismatched
payloads return `idempotency_conflict`. Rate limits are enforced by tenant,
identity, channel, and action type, with stricter channel throttles permitted.

## Approvals And Resume

Waiting prompts show prompt id, prompt version, allowed actions, and safe
context. Decisions are accepted only when the prompt is current, the action is
allowed, and the reviewer is authorized. Stale responses return the latest run
status without changing the run.

## Notifications, Callbacks, And Artifacts

The initiating user is automatically subscribed to terminal notifications.
Additional authorized users can subscribe per run. API clients can register
HTTPS callbacks for terminal, waiting prompt, and artifact-ready events.
Artifacts are listed as metadata; all channels create short-lived
platform-authenticated download URLs instead of returning bytes directly.

## Troubleshooting

Use the run id and trace id from status responses or the Web UI support panel
to inspect audits, timeline events, notification attempts, callback attempts,
and artifact access grants. Telegram messages stay concise; detailed error
categories are stored in channel evidence.

