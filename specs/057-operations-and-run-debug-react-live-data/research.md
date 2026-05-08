# Research: Operations And Run Debug React Live Data

## Decision: Use Live Service And Repository Sources For Workbench Data

**Rationale**: `OperationsConsoleService`, dependency health checks, reliability
repositories, runtime orchestration repositories, audit-debugging repositories,
provider/gateway repositories, channel repositories, skill execution
diagnostics, usage analytics, and storage metadata already represent the
authoritative operational state. Reading those sources keeps the workbench
honest and avoids moving deterministic QA029 rows behind another abstraction.

**Alternatives considered**:

- Keep deterministic workbench rows and label them as examples. Rejected
  because production routes would still show fake operational data.
- Store a new synthetic workbench snapshot table as the only source. Rejected
  because it would lag the actual operational records and create another
  synchronization problem.

## Decision: Tenant Views Hide Platform-Only Pressure

**Rationale**: Tenant administrators need tenant-visible run, delivery, usage,
export, and safe log evidence. Platform-only database pool, worker queue,
provider fleet, object-storage, and global breaker pressure can reveal shared
infrastructure details and should render as hidden, unavailable, or summarized
only when existing policy allows safe visibility.

**Alternatives considered**:

- Show all platform pressure to tenant admins. Rejected due tenant isolation and
  shared infrastructure disclosure risk.
- Remove tenant workbench access entirely. Rejected because tenant admins need
  their own run, delivery, usage, and export triage.

## Decision: Bound Workbench Queries To The Last 60 Minutes By Default

**Rationale**: The current workbench contract already uses a 60-minute default.
Keeping that default limits query cost and makes QA seeds deterministic. Future
presets can be added only when backed by bounded repository queries and
validation coverage.

**Alternatives considered**:

- Allow arbitrary start/end dates immediately. Rejected because unbounded
  operational queries create performance and validation risk.
- Use a 24-hour default. Rejected because it increases query volume without a
  clear user requirement for this cleanup spec.

## Decision: Resolve Run Debug From Runtime And Audit Evidence

**Rationale**: Direct run-debug links must reflect the requested run ID. Runtime
run records, timeline events, graph evidence, gateway attempts, delivery
attempts, usage records, and audit-debug records can provide safe summaries.
Missing runs should return not found and unauthorized runs should fail closed.

**Alternatives considered**:

- Keep the deterministic QA029 run when a run is missing. Rejected because it is
  the core bug this spec removes.
- Return a partial fake run with empty sections. Rejected because it would still
  misrepresent existence and status.

## Decision: Derive Likely Causes Deterministically From Safe Symptoms

**Rationale**: Likely-cause summaries should be reproducible from dependency,
reliability, runtime failure, provider attempt, delivery, usage, and skill
diagnostic categories. This avoids live model calls, keeps redaction simple, and
lets tests assert exact safe summaries.

**Alternatives considered**:

- Use a live model to summarize likely causes. Rejected due external-call,
  prompt, and repeatability risk.
- Omit likely causes. Rejected because the existing workbench user value
  includes triage guidance.

## Decision: Persist Workbench Export Evidence Through Existing Storage

**Rationale**: Export actions are safe mutations and should create durable
request/audit evidence plus storage-backed artifact metadata. Browser/API
responses should expose safe artifact references only, never `file:` URIs or
local paths.

**Alternatives considered**:

- Return a synthetic artifact id. Rejected because it is not durable evidence.
- Return the storage URL directly. Rejected because local paths and storage
  details must not appear in browser/API output.

## Decision: QA057 Seed Uses Real Tables With Safe Records

**Rationale**: The spec requires both empty and seeded live behavior. QA057 will
seed Acme operations records inside the 60-minute window and leave Globex empty
for isolation checks. Seed data may use repository/model helpers in test or QA
paths, but production builders must read the persisted rows through live
services and repositories.

**Alternatives considered**:

- Seed frontend fixtures only. Rejected because React must consume backend
  contracts backed by live data.
- Reuse QA029 fixed identifiers in production. Rejected because scanner
  guardrails must block fixed workbench rows after this spec.
