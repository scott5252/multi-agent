# Data Model: User Interaction Channels

## ChannelSession

Represents an authenticated or link-pending interaction context for Web UI,
Web API, or Telegram.

**Fields**: `channel_session_id`, `tenant_id`, `platform_identity_id`,
`channel_type`, `channel_subject`, `auth_state`, `created_at`, `last_seen_at`,
`expires_at`, `metadata`.

**Relationships**: Owns many normalized channel actions, notification
subscriptions, and delivery attempts. Telegram sessions may be connected by a
TelegramIdentityLink.

**Validation rules**: Protected actions require `auth_state = linked` or an
equivalent authenticated Web/API session. `channel_subject` is unique within
channel type and tenant when linked.

## TelegramIdentityLink

Durable association between a Telegram user/chat and a platform identity.

**Fields**: `telegram_identity_link_id`, `tenant_id`, `platform_identity_id`,
`telegram_user_id`, `telegram_chat_id`, `link_token_hash`, `status`,
`created_at`, `expires_at`, `linked_at`, `revoked_at`.

**Relationships**: Creates or updates a Telegram ChannelSession after token
consumption.

**Validation rules**: Link tokens are one-time, short-lived, hashed at rest,
and tenant-scoped. Expired, reused, or revoked links cannot authorize protected
actions.

**State transitions**: `pending` -> `linked`; `pending` -> `expired`;
`linked` -> `revoked`.

## NormalizedChannelRequest

Canonical envelope for a user action received from any channel.

**Fields**: `normalized_request_id`, `tenant_id`, `platform_identity_id`,
`channel_session_id`, `channel_type`, `action_type`, `run_id`, `prompt_id`,
`idempotency_key`, `trace_id`, `source_request_id`, `input_payload`,
`received_at`, `authorization_outcome`, `user_visible_outcome`.

**Relationships**: May produce a WorkflowInvocationRequest, approval/resume
decision, artifact URL grant, notification acknowledgement, callback
registration, or status/result read audit.

**Validation rules**: Duplicate-prone actions require `idempotency_key`.
Protected actions require tenant and platform identity. Trace ids must be
present before runtime calls.

## ChannelIdempotencyRecord

Stores the first accepted outcome for duplicate-prone channel actions.

**Fields**: `idempotency_record_id`, `tenant_id`, `platform_identity_id`,
`channel_type`, `action_type`, `idempotency_key`, `request_fingerprint`,
`status`, `stored_response`, `run_id`, `created_at`, `expires_at`.

**Validation rules**: Unique key across tenant, actor, channel type, action
type, and idempotency key. Matching replays return `stored_response`;
fingerprint mismatches return `idempotency_conflict`.

**State transitions**: `in_progress` -> `accepted`; `in_progress` -> `failed`;
terminal idempotency states are immutable until retention expiry.

## UserVisibleRun

Projection of runtime state for channels.

**Fields**: `run_id`, `tenant_id`, `requester_identity_id`, `visible_state`,
`internal_runtime_status`, `progress_summary`, `latest_timeline_sequence`,
`waiting_prompt_id`, `terminal_outcome`, `result_availability`,
`artifact_availability`, `created_at`, `updated_at`, `finished_at`.

**Relationships**: References existing runtime run, timeline events, waiting
prompt, result metadata, artifacts, subscriptions, callbacks, and audits.

**Validation rules**: `visible_state` is exactly one of `queued`, `running`,
`waiting-for-input`, `completed`, `failed`, or `canceled`.

## TimelineEvent

User-facing, redacted event shown through REST, Web UI, and callback payloads.

**Fields**: `timeline_event_id`, `tenant_id`, `run_id`, `sequence`,
`event_type`, `visible_state`, `summary`, `severity`, `occurred_at`,
`trace_id`, `source_channel`, `step_ref`, `prompt_ref`, `artifact_ref`,
`metadata`.

**Relationships**: Derived from runtime timeline/audit records and linked to a
UserVisibleRun.

**Validation rules**: Sequence is monotonic per run. Payloads must be safe for
the requesting user's authorization context and must not include raw secrets,
artifact bytes, or unauthorized results.

## WaitingPromptView

Channel-safe view of a durable runtime approval or resume prompt.

**Fields**: `prompt_id`, `tenant_id`, `run_id`, `prompt_type`, `prompt_version`,
`visible_state`, `summary`, `context`, `allowed_actions`, `eligible_reviewers`,
`deadline_at`, `created_at`, `answered_at`.

**Relationships**: References runtime approval/input state and accepted
ChannelDecisionResponse records.

**Validation rules**: Actions are available only when the prompt is current and
the run is in `waiting-for-input`. Submitted prompt version must match current
prompt version.

**State transitions**: `open` -> `approved`; `open` -> `rejected`; `open` ->
`resumed`; `open` -> `canceled`; `open` -> `superseded`; terminal prompt
states reject later decisions with the latest run status.

## ChannelDecisionResponse

Accepted or rejected response to an approval, rejection, resume, or cancel
action.

**Fields**: `decision_response_id`, `tenant_id`, `run_id`, `prompt_id`,
`platform_identity_id`, `action`, `decision_payload`, `idempotency_key`,
`accepted`, `rejection_category`, `latest_status_snapshot`, `trace_id`,
`created_at`.

**Validation rules**: Must pass authorization, lifecycle, prompt freshness, and
idempotency checks before changing runtime state.

## RunNotificationSubscription

Per-run preference for terminal notifications.

**Fields**: `notification_subscription_id`, `tenant_id`, `run_id`,
`platform_identity_id`, `channel_session_id`, `channel_type`, `event_types`,
`status`, `created_at`, `created_by`, `revoked_at`.

**Relationships**: Has many NotificationDeliveryAttempt records. The initiating
user receives an automatic subscription when a run is accepted.

**Validation rules**: Subscribers must be authorized for the run at subscribe
time and again before delivery.

**State transitions**: `active` -> `revoked`; `active` -> `authorization_lost`.

## NotificationDeliveryAttempt

Evidence that a terminal or prompt notification was attempted.

**Fields**: `notification_delivery_attempt_id`, `tenant_id`,
`notification_subscription_id`, `run_id`, `channel_type`, `event_type`,
`payload_fingerprint`, `delivery_status`, `provider_message_id`,
`failure_category`, `attempt_number`, `next_retry_at`, `trace_id`,
`created_at`, `delivered_at`.

**Validation rules**: Payloads contain run id, terminal state, redacted summary,
and next available action only. Authorization is re-checked before each send.

**State transitions**: `scheduled` -> `delivered`; `scheduled` -> `retrying`;
`retrying` -> `delivered`; `retrying` -> `failed`; any non-terminal attempt may
become `suppressed` when authorization or preferences no longer allow delivery.

## RunResultView

Channel-safe result retrieval response.

**Fields**: `run_id`, `tenant_id`, `availability`, `visible_state`, `summary`,
`structured_result`, `failure_summary`, `cancellation_summary`, `expires_at`,
`trace_id`.

**Validation rules**: `availability` distinguishes `available`, `failed`,
`canceled`, `unavailable`, `expired`, and `unauthorized`. Result content is
included only for authorized completed runs with available results.

## ArtifactAccessGrant

Short-lived authorization for retrieving one run artifact.

**Fields**: `artifact_access_grant_id`, `tenant_id`, `run_id`, `artifact_id`,
`platform_identity_id`, `channel_type`, `idempotency_key`, `download_url`,
`expires_at`, `status`, `created_at`, `trace_id`.

**Relationships**: References existing artifact metadata and object-storage
provider references.

**Validation rules**: Artifact access is at least as restrictive as result
retrieval. Grants are short-lived, platform-authenticated, audited, and never
deliver bytes directly through Telegram or JSON responses.

## ApiCallbackRegistration

Per-run callback subscription for API clients.

**Fields**: `api_callback_registration_id`, `tenant_id`, `run_id`,
`platform_identity_id`, `callback_url`, `event_types`, `signing_secret_ref`,
`status`, `created_at`, `revoked_at`.

**Relationships**: Has many ApiCallbackDeliveryAttempt records and references
UserVisibleRun/TimelineEvent payloads.

**Validation rules**: Callback URL must use HTTPS outside local development.
Registrations require authorization for the run and idempotency for create or
replace operations.

**State transitions**: `active` -> `revoked`; `active` -> `disabled`.

## ApiCallbackDeliveryAttempt

Evidence and retry state for one callback event delivery.

**Fields**: `api_callback_delivery_attempt_id`, `tenant_id`,
`api_callback_registration_id`, `run_id`, `event_id`, `event_type`,
`payload_fingerprint`, `signature`, `delivery_status`, `http_status`,
`failure_category`, `attempt_number`, `next_retry_at`, `trace_id`,
`created_at`, `delivered_at`.

**Validation rules**: Payloads include event id and trace id, are signed, and
are retried with exponential backoff. Failed callback delivery never changes
the workflow run state.

## InteractionAuditRecord

Durable audit evidence for channel actions.

**Fields**: `interaction_audit_record_id`, `tenant_id`, `platform_identity_id`,
`channel_type`, `channel_session_id`, `action_type`, `run_id`, `prompt_id`,
`artifact_id`, `authorization_outcome`, `error_category`,
`user_visible_outcome`, `trace_id`, `created_at`, `redacted_metadata`.

**Validation rules**: Records are append-only and content-light. They store
identifiers, outcomes, and redacted summaries, not secrets, Telegram raw
message text containing sensitive payloads, result bodies, or artifact bytes.
