# Research: Token Usage And Cost Analytics

## Decision: Use ModelGateway As The Capture Boundary

**Decision**: Usage events are recorded only for model invocations routed
through `ModelGateway`.

**Rationale**: ModelGateway is already the policy-governed boundary for
provider access, retry/breaker summaries, operation idempotency, provider model
selection, and safe audit metadata. Capturing there avoids ungoverned direct
provider calls and aligns usage records with existing gateway attempts.

**Alternatives considered**:

- Capture in provider adapters. Rejected because adapters do not have complete
  workflow, tenant, prompt, agent, and authorization context.
- Capture in workflow runtime only. Rejected because gateway calls can also
  occur from probes, validation, and admin workflows.

## Decision: Extend Normalized Gateway Usage Safely

**Decision**: Extend provider usage normalization to support input, output,
cached, reasoning, total, provider billable units, and per-field status flags.

**Rationale**: Providers expose different token details. A richer normalized
shape lets analytics distinguish confirmed values from calculated or missing
values without tying storage to one provider.

**Alternatives considered**:

- Store raw provider usage payload. Rejected because it can include provider
  metadata drift and is harder to audit for redaction.
- Store only total tokens. Rejected because cost estimates and cached-token
  savings need category-level values.

## Decision: Use Versioned Internal Pricing Metadata

**Decision**: Cost estimates use immutable `llm_pricing_versions` records
managed inside the platform.

**Rationale**: Internal pricing versions are deterministic, auditable, and
safe for local QA. They avoid external provider calls, make historical events
explainable, and preserve estimates after pricing updates.

**Alternatives considered**:

- Fetch pricing live from providers. Rejected because it creates external side
  effects, availability coupling, and non-deterministic QA.
- Encode pricing in source constants only. Rejected because admins need
  effective-date versions and historical references.

## Decision: Query-Time Rollups For MVP

**Decision**: Dashboard rollups are computed from indexed event rows at query
time for the first implementation. `llm_usage_rollups` exists as the future
materialization target.

**Rationale**: The feature requires correctness and tenant isolation first.
Query-time rollups simplify reconciliation and avoid a worker aggregation path
until performance tests prove the need for materialization.

**Alternatives considered**:

- Build aggregation jobs immediately. Rejected as extra operational scope for
  MVP.
- Store only rollups. Rejected because drilldowns, exports, and reconciliation
  require event-level records.

## Decision: Object Storage For CSV Payloads

**Decision**: Export requests store metadata in PostgreSQL and CSV content in
the existing storage provider when generated.

**Rationale**: This follows the constitution's tiered-storage rule and keeps
large payloads out of PostgreSQL. Metadata remains queryable and auditable.

**Alternatives considered**:

- Inline CSV responses only. Rejected because larger exports need retention,
  audit, and retrieval metadata.
- Store CSV bytes in a JSON/text DB column. Rejected as blob storage in
  PostgreSQL.

## Decision: Preserve Estimates During Reconciliation

**Decision**: Late confirmed usage creates a reconciliation record linking the
original event to corrected values and updates current event values for
dashboard totals.

**Rationale**: Operators need current totals to improve when providers send
late confirmed usage, while audit and export history remain explainable.

**Alternatives considered**:

- Delete and recreate events. Rejected because it destroys audit continuity.
- Leave estimates forever. Rejected because confirmed usage should improve
  finance accuracy.

## Decision: Denied Access Audit Is Best-Effort But Explicit

**Decision**: Usage routes attempt to write denied-access audit metadata before
returning 403, and tests assert this path through the usage service/repository.

**Rationale**: Denied access to cost data is a security signal. The audit
payload must be safe and must not reveal unauthorized tenant/run details.

**Alternatives considered**:

- Rely on web access logs. Rejected because logs do not provide structured
  tenant/action/filter metadata.
