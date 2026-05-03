# Data Model: Operations Console Logs And Performance

No new database tables are required for v1.

## Operations Dashboard Snapshot

Aggregated DTO returned by the operations service.

- `generated_at`: timestamp when the snapshot was assembled.
- `scope_type`: `platform`.
- `health_status`: overall health/readiness label.
- `dependency_count`: number of dependency checks.
- `status_cards`: safe cards for system health, dependencies, storage,
  capacity, providers, Telegram/channel readiness, reliability, latency,
  throughput, and error rate.
- `capacity`: worker, queue, retry, dead-letter, DB pool, artifact, breaker,
  and fairness metrics from the latest reliability capacity snapshot.
- `dependencies`: health-check rows from runtime health.
- `providers`: model provider health summaries.
- `usage`: token and usage-event totals for the selected time range.
- `logs`: bounded redacted operational log rows.
- `links`: safe admin links to run inspection, reliability controls, model
  providers, Telegram configuration, and usage analytics.

## Operational Log Filter

Request DTO for dashboard and log APIs.

- `trace_id`: optional trace id string.
- `tenant_id`: optional UUID for platform-admin/auditor filtering.
- `run_id`: optional workflow run UUID.
- `component`: optional component or category such as `runtime`, `gateway`,
  `model_provider`, `telegram`, `reliability`, or `audit`.
- `severity`: optional safe criticality label.
- `status`: optional lifecycle or outcome status.
- `dependency`: optional dependency/provider/channel key.
- `start`: optional inclusive start timestamp.
- `end`: optional exclusive end timestamp.
- `limit`: required bounded result limit, max 500.

Validation rules:

- `end` must be greater than `start` when both are provided.
- Tenant admins are not authorized in v1.
- Queries without time bounds are still limited.

## Operational Log Event

Redacted row derived from existing persisted records.

- `event_id`: source-prefixed stable id.
- `source`: `audit_timeline`, `gateway_attempt`, `runtime_trace`, or other safe
  source.
- `occurred_at`: timestamp.
- `tenant_id`: optional UUID.
- `trace_id`: optional trace id.
- `run_id`: optional workflow run UUID.
- `component`: safe component name.
- `severity`: safe severity/criticality label.
- `status`: safe lifecycle/outcome status.
- `dependency`: optional safe dependency/provider/model key.
- `summary`: redacted safe summary.
- `details`: safe key/value metadata, with sensitive keys dropped or masked.
- `links`: optional safe admin links.

Redaction rules:

- Drop or replace keys containing prompt, completion, content, message, secret,
  token, password, api key, authorization, credential, memory, payload,
  traceback, stack trace, or raw.
- Truncate long strings.
- Never include raw model responses, prompts, channel messages, or secrets.

## Operations Export Artifact

Export result returned by API.

- `export_id`: generated UUID for this export operation.
- `artifact_uri`: storage provider URI.
- `artifact_sha256`: CSV checksum.
- `artifact_size_bytes`: byte length.
- `row_count`: exported row count.
- `filters`: safe filter snapshot.
- `requested_by`: principal id.
- `audit_event_id`: inspection access audit event id when available.
- `created_at`: timestamp.

## Operations Access Scope

Authorization DTO.

- `principal_id`: requester.
- `role`: `platform_admin` or `auditor`.
- `can_export`: true only with `operations:export`.
- `tenant_filter_allowed`: true for platform/admin auditor filtering, false for
  tenant-admin platform log access.

## Existing Source Records

- `audit_timeline_events`: run lifecycle, categories, safe summaries, trace ids.
- `audit_runtime_trace_records`: runtime trace duration and outcomes.
- `gateway_invocation_attempts`: model/provider latency, outcome, usage
  availability, safe audit summary.
- `llm_usage_events`: token throughput and usage status.
- `reliability_capacity_snapshots`: worker, queue, DB pool, retry,
  dead-letter, breaker, and artifact pressure.
- `model_provider_connections`: provider health and model counts.
- `telegram_diagnostic_events` and settings: channel readiness metadata.
- `audit_inspection_access_events`: export and denial audit metadata.
