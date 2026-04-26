# Production Audit Debugging

Production audit debugging records immutable, tenant-scoped evidence for
workflow runs and exposes it through administrator APIs. Timelines, runtime
traces, lineage, version bundles, notification state, secret-access metadata,
redacted exports, structured logs, metrics, and capture gaps share the same
trace identifiers.

## Timeline Inspection

Use `GET /admin/runs/{workflow_run_id}/timeline` with a tenant id to inspect
the chronological event stream. Events include lifecycle states, failed-stage
summaries, runtime decisions, linked trace records, capture gaps, and safe
details only.

## Trace Fields

Trace records link to a same-tenant timeline event and include trace id,
correlation id, type, status, outcome, duration, policy outcome, subject
reference, and safe input/output/error summaries.

## Replay

`GET /admin/runs/{workflow_run_id}/replay` assembles ordered immutable replay
events. Replay never re-executes tools, models, notifications, secret
resolution, memory writes, or workflow side effects.

## Lineage

Lineage responses show parent-child, retry, resumption, and delegation edges.
Unauthorized related runs are represented as redacted boundary nodes.

## Version Bundles

Bundle views expose the pinned execution bundle digest, workflow version,
contract references, prompt references, model configuration references,
tool-policy references, activation state at acceptance, and migration refs.
Raw workflow definitions and prompt bodies are not rendered.

## Notifications

Notification traceability stores destination category, delivery status, attempt
count, latest attempt time, safe failure reason, provider correlation reference,
and triggering timeline event.

## Secret Access

Secret-access records store requester metadata, secret reference id/version,
credential scope, policy outcome, access outcome, reason code, run context, and
trace id. Raw secret values, credential values, provider tokens, and decrypted
metadata are forbidden.

## Redaction

Classification is default-deny for dynamic fields. Safe identifiers,
categories, digests, counts, durations, policy outcomes, and bounded safe
summaries may be stored and rendered. Prompt content, memory content, secrets,
credentials, unknown payload bodies, and oversized payloads are summarized or
masked for the viewer.

## Exports

`POST /admin/runs/{workflow_run_id}/exports` creates a redacted debug-evidence
export request. Export metadata is append-only and uses the same authorization
and viewer-aware redaction rules as interactive inspection.

## Escalation

If capture is unavailable for security or governance evidence, protected
actions fail closed. Diagnostic capture failures create capture-gap markers,
emit metrics, and appear in timeline, replay, and export evidence.
