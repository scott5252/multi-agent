# Research: Operations Console Logs And Performance

## Decision: Aggregate Existing Safe Operational Records

**Decision**: Build the operations console from existing safe records and
services: health checks, reliability capacity snapshots, model provider
connections and gateway attempts, Telegram settings/readiness metadata, usage
events, and audit-debugging timeline/trace records.

**Rationale**: The constitution requires operability, tenant isolation, and
secret hygiene. Existing records already carry tenant ids, trace ids, safe
summaries, and redacted metadata. Reading raw log files would bypass those
controls and create deployment-specific behavior.

**Alternatives Considered**:

- Raw application log file tailing: rejected because redaction and retention are
  not uniformly enforced.
- New operational events table: deferred because existing audit/debugging and
  gateway records are sufficient for v1 and avoid a migration.

## Decision: Platform Admin And Auditor Only For V1

**Decision**: Operations Console access is restricted to platform admins and
auditors with explicit operations permissions.

**Rationale**: The prompt states platform logs are platform-admin or auditor
only and tenant admin views are optional only if explicitly included. No
tenant-specific operations UX was included in the manifest.

**Alternatives Considered**:

- Tenant-scoped limited views: rejected for v1 because role boundaries and
  redaction semantics would need a separate tenant-facing spec.

## Decision: Bounded Query Strategy

**Decision**: Use indexed database predicates for tenant id, trace id, run id,
and time ranges where available, then apply secondary component/severity/status
and dependency matching in memory over a bounded candidate set.

**Rationale**: Existing sources have different schemas. A bounded candidate set
keeps the first release simple while performance tests enforce that the time
range path remains safe.

**Alternatives Considered**:

- Cross-source search index: deferred until operators need full-text log search.
- JSONB-only filters across all sources: rejected for SQLite parity in tests and
  mixed source schemas.

## Decision: Export Through Existing Artifact Storage And Audit Table

**Decision**: Export redacted CSV rows through the configured storage provider
and record allowed/denied export metadata through existing
`audit_inspection_access_events`.

**Rationale**: The platform already separates artifact payloads from
transactional metadata. Reusing the audit inspection table satisfies export
auditability without adding a feature-specific table.

**Alternatives Considered**:

- Return CSV inline only: rejected because the requirement asks for export
  artifacts.
- Create a dedicated operations export table: deferred until export lifecycle
  management requires persisted status pages.

## Decision: Screenshot-Safe UI

**Decision**: The server-rendered UI shows compact operational panels, links to
existing admin tools, redaction and retention notices, and redacted log rows.

**Rationale**: Operations dashboards are repeated-use work surfaces. The UI
should be dense, scan-friendly, and aligned with the existing admin shell.

## Open Questions

None. Autopilot selections resolved low-risk ambiguity and did not conflict
with the constitution.
