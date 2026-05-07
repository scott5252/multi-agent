# Data Model: User-Facing Run UI React Port And Jinja Removal

## Run Invocation

- **Fields**: `workflow_id`, `inputs`, `channel`, `client_session_id`, `callback_url`, idempotency header.
- **Rules**: JSON clients must send an idempotency key. Browser form compatibility may derive a deterministic key from workflow and principal. Inputs are displayed only as safe summaries.
- **State transitions**: Request creates or replays a `Run Status` projection.

## Run Status

- **Fields**: `run_id`, `state`, `progress_summary`, `latest_timeline_cursor`, `permitted_actions`, `trace_id`, optional waiting prompt, terminal outcome, result availability, artifact availability, subscribed flag.
- **Rules**: Tenant actor must be authorized for the run. Cross-tenant and unavailable runs return safe problem/unavailable states.
- **State transitions**: Updated by start, cancel, prompt decision, and runtime progress.

## Timeline Event

- **Fields**: `event_id`, `sequence`, `event_type`, `state`, `summary`, `severity`, `occurred_at`, `trace_id`.
- **Rules**: Timeline payloads are summaries only and must not include raw prompts, run payloads, completions, or private messages.

## Waiting Prompt

- **Fields**: `prompt_id`, `prompt_type`, `prompt_version`, `summary`, safe context, allowed actions, optional deadline.
- **Rules**: Decisions must include the prompt version and idempotency key. Stale prompt versions return safe conflict responses.

## Run Result

- **Fields**: `run_id`, `availability`, `state`, `trace_id`, optional summary, optional redacted structured result.
- **Rules**: Raw result bodies and private channel content remain unavailable to the browser.

## Artifact Metadata

- **Fields**: `artifact_id`, `name`, `user_facing_type`, `status`, `download_url_available`, optional size.
- **Rules**: Browser displays metadata only. Download requests create short-lived grants and never expose filesystem/object-storage paths.

## Subscription And Callback Registration

- **Fields**: registration identifier, channel/callback status, event types, idempotency evidence.
- **Rules**: UI displays registration status only; callback URLs and secrets are not echoed in screenshots or QA artifacts.

## Compatibility Redirect

- **Fields**: legacy path, destination path, allowlisted query keys, route parameters, status code.
- **Rules**: Browser routes use authenticated `303` redirects and preserve only safe tenant context.
