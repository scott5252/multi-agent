# Telegram Webhook Contract

## Endpoint

`POST /channels/telegram/webhook/{secret}`

The `{secret}` path segment or equivalent configured header must match the
platform Telegram webhook secret. Invalid provider authentication records a
rejected delivery audit event and returns a generic success response when
needed to prevent provider retry storms.

## Supported Commands

| Command | Protected | Behavior |
|---------|-----------|----------|
| `/start` | No | Shows linking status and safe help text. |
| `/link <token>` | No | Consumes a one-time platform link token and creates a Telegram identity link. |
| `/run <workflow> [inputs]` | Yes | Starts a workflow through the shared channel facade. |
| `/status <run_id>` | Yes | Returns persisted status and latest progress summary. |
| `/approve <run_id> <prompt_id>` | Yes | Accepts an approval prompt when current and authorized. |
| `/reject <run_id> <prompt_id>` | Yes | Rejects a prompt when current and authorized. |
| `/resume <run_id> <prompt_id> [payload]` | Yes | Submits resume input when current and authorized. |
| `/cancel <run_id>` | Yes | Requests cancellation through the shared channel facade. |
| `/result <run_id>` | Yes | Returns result availability and a safe summary. |
| `/artifacts <run_id>` | Yes | Lists artifact metadata and short-lived download actions. |
| `/subscribe <run_id>` | Yes | Subscribes the linked user to terminal notifications. |

## Duplicate Handling

Telegram `update_id` is stored as a provider idempotency key. Duplicate updates
return the stored outcome and do not create another run, decision, cancellation,
notification acknowledgement, or artifact URL grant.

## Linking Behavior

1. A signed-in platform user creates a one-time Telegram link token.
2. The user sends `/link <token>` in Telegram.
3. The platform verifies the token hash, tenant, expiry, and one-time status.
4. The Telegram user/chat is linked to the platform identity.
5. Protected commands are allowed only after the link is active.

Expired, reused, malformed, or tenant-mismatched tokens return a safe message
that asks the user to create a fresh token from the Web UI.

## Completion Messages

Terminal notifications include:

- Run identifier
- Terminal state: `completed`, `failed`, or `canceled`
- Redacted summary
- Next action labels such as "View result", "Artifacts", or "View details"
- A trace/support reference when configured

Terminal notifications must not include raw final result bodies, secrets,
artifact bytes, or artifact URLs unless the URL is freshly authorized for the
linked platform identity.

## Error Messages

Telegram presents concise user-facing text mapped from the shared error
categories:

- `unauthorized`: "I could not verify access to that run."
- `missing_input`: "I need more information before I can do that."
- `invalid_run_id`: "I could not find that run for your account."
- `invalid_lifecycle_action`: "That run is no longer waiting for this action."
- `rate_limited`: "That action is temporarily rate limited."
- `platform_failure`: "The platform could not complete that action. Try again
  with the run id."

Detailed diagnostics are recorded in channel audit and delivery attempt
records rather than sent to Telegram.
