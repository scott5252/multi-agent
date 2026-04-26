# Research: Production Audit And Debugging

## Durable Audit Capture

**Decision**: Store security/governance audit events, runtime timeline events,
trace records, capture gaps, inspection access records, export records, and
redaction/correction events in append-only PostgreSQL tables with idempotent
capture keys.

**Rationale**: PostgreSQL is the platform source of truth for workflow state,
lineage, audit metadata, and retention metadata. Append-only rows preserve
replay, incident review, and governance evidence while idempotency allows
workers to retry safely after crashes.

**Alternatives considered**: Log-only audit streams were rejected because they
do not provide tenant-scoped inspection APIs or transactional durability.
Mutable timeline projections alone were rejected because corrections and
redactions would erase historical evidence.

## Fail-Closed Audit Policy

**Decision**: Classify capture events as `security_governance`,
`runtime_required`, or `diagnostic`. Security/governance capture failures fail
closed; diagnostic failures create unavailable markers and metrics.

**Rationale**: The spec requires fail-closed behavior for governance evidence
and explicit unavailable states for non-security trace gaps. Criticality lets
runtime services remain operable for non-authoritative traces without silently
losing important evidence.

**Alternatives considered**: Failing every capture gap closed was rejected
because diagnostic telemetry should not halt otherwise valid work. Allowing
all capture gaps was rejected because access denials, secret access, policy
decisions, exports, and protected inspection events need durable governance
evidence.

## Trace Ids, Structured Logs, And Metrics

**Decision**: Propagate `trace_id`, `tenant_id`, `workflow_run_id`,
`timeline_event_id`, `run_step_id`, and `correlation_id` through runtime,
audit, and inspection services. Emit structured logs and metrics from the same
capture facade that writes durable records.

**Rationale**: Operators need a consistent join key across logs, metrics,
timeline events, traces, and API responses. Centralizing telemetry emission
prevents each runtime subsystem from inventing incompatible field names.

**Alternatives considered**: Per-module logging conventions were rejected
because they would make trace and timeline completeness hard to test. A full
external tracing dependency was deferred because the repository already has
observability helpers and the required operator surface is PostgreSQL-backed.

## Query Model

**Decision**: Provide query-ready PostgreSQL projections for run summaries,
lineage, notification delivery state, and version-bundle references while
keeping immutable source rows as the authority.

**Rationale**: Direct run lookup must return in p95 <= 2 seconds and filtered
search in p95 <= 5 seconds. Projections allow indexed, tenant-scoped access
without giving operators database access or assembling every response from raw
audit rows.

**Alternatives considered**: Querying only raw event rows was rejected for
search latency and response-shape complexity. A separate search service was
rejected for initial scope because PostgreSQL indexes and bounded filters are
sufficient for the defined scale.

## Replay Views

**Decision**: Replay views render an ordered, redacted event stream from
timeline and trace records without re-executing models, tools, notifications,
secret resolution, or memory writes.

**Rationale**: The feature needs debugging replay, not behavioral replay.
Operators must understand what happened and why, while avoiding side effects,
data drift, or accidental disclosure of protected content.

**Alternatives considered**: Re-running workflows was rejected because it
would violate version-pinned execution, produce side effects, and diverge from
the historical incident. Screenshot-style static reports were rejected because
operators need linked trace data, lineage navigation, and filters.

## Redaction And Classification

**Decision**: Classify every captured field before storage or rendering and
default unknown dynamic payloads to redacted summaries. Store safe identifiers,
digests, lengths, status categories, policy outcomes, and bounded error
summaries instead of raw sensitive payloads.

**Rationale**: The spec forbids raw secrets, credentials, unauthorized prompt
content, and unauthorized memory content in logs, traces, exports, and review
notes. Classification at capture time plus viewer-aware serialization protects
both persisted records and API responses.

**Alternatives considered**: Rendering-time redaction only was rejected
because sensitive values might still be persisted or logged. Allow-listing a
small set of known payload types without a default deny posture was rejected
because tools and agents can produce unexpected payloads.

## Parent-Child Lineage And Version Bundles

**Decision**: Represent lineage as authorized graph JSON and version bundles
as pinned run context attached to timeline, replay, and export responses.
Unauthorized related runs appear as redacted boundary nodes.

**Rationale**: Parent-child runs, retries, resumptions, delegated executions,
and pinned bundles are central to debugging multi-agent behavior. Graph-shaped
responses support both API clients and minimal admin UI visualization while
preserving tenant boundaries.

**Alternatives considered**: Flat related-run lists were rejected because they
hide nested relationships and retry/resume edges. Exposing raw workflow bundle
documents was rejected because operators need safe references and activation
metadata, not full protected definitions.

## Export Handling

**Decision**: Generate debug-evidence exports through the audit service,
persist export metadata in PostgreSQL, store payloads through existing artifact
storage, and audit export creation/share attempts before releasing links.

**Rationale**: Exports are governance artifacts and must apply the same tenant,
role, retention, and redaction rules as interactive inspection. Object storage
avoids using PostgreSQL as a blob store.

**Alternatives considered**: Returning large exports inline was rejected for
latency, retention, and access-control reasons. Manual SQL export was rejected
because the feature explicitly removes the need for direct database access.

## Testing Strategy

**Decision**: Validate trace and timeline completeness with deterministic run
fixtures that produce lifecycle transitions, handoffs, validations, memory
writes, tool allow/deny decisions, model selections, notifications, secret
access, lineage, capture gaps, and authorization failures.

**Rationale**: Completeness is an end-to-end property. Tests must prove every
expected runtime event is present, linked to a timeline event, redacted for the
viewer, queryable through admin APIs, and covered by logs/metrics/traces.

**Alternatives considered**: Isolated unit tests alone were rejected because
they cannot prove event linkage or query completeness. Manual QA alone was
rejected because the constitution requires automated coverage and repeatable
review evidence.
