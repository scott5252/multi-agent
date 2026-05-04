# Research: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Decision: Use Existing Agent Test Bench Runs As The Authoritative Evidence

**Decision**: Required-test readiness for workflow publication will be derived from `AgentTestSuite`, `AgentTestRun`, and related repository queries.

**Rationale**: The test bench already persists tenant-owned suites, target metadata, run status, target version, safe mode, redaction summaries, and publish-gate helper APIs. Reusing this store removes the current manual status-copy risk.

**Alternatives considered**:

- Keep trusting `latest_result_status` in workflow documents. Rejected because copied values can be stale, forged, or cross-tenant.
- Store a separate workflow evidence table. Rejected for this feature because existing run records already contain the required target and status metadata.

## Decision: Current Draft Revision ID Is The Freshness Boundary

**Decision**: For workflow drafts, the evidence target is `target_type=workflow_draft`, `target_id=<workflow_draft_id>`, and `target_version=<workflow_draft_revision_id>`.

**Rationale**: A draft save creates an immutable revision record and supersedes prior validation. Binding evidence to the revision means a passing run for an older document cannot publish a changed draft.

**Alternatives considered**:

- Use revision number. Rejected because UUID revision IDs are globally unambiguous.
- Use document hash. Rejected because test-bench APIs already model target version as a string and the revision ID is easier for admins to trace.

## Decision: Fail Closed For Platform Scope With Tenant-Owned Tests

**Decision**: If a platform-scoped workflow declares required tests and no tenant evidence context is available, validation reports required evidence as unavailable.

**Rationale**: Agent test suites are tenant-owned today. Guessing a tenant or allowing platform workflows to borrow tenant evidence would violate isolation.

**Alternatives considered**:

- Let platform admins reference any tenant suite. Rejected because this leaks tenant evidence and creates unclear ownership.
- Add platform-owned test suites now. Rejected as scope expansion requiring schema and authorization changes.

## Decision: Preserve Legacy Fields As Compatibility Metadata

**Decision**: Existing `latest_result_status`, `latest_result_id`, and `executed_at` fields remain parseable, but workflow validation and publish gates ignore them for readiness.

**Rationale**: Existing drafts and tests can still load while the bypass is closed.

**Alternatives considered**:

- Remove fields from the schema. Rejected because it would break existing documents and migrations without adding security value.

## Decision: Store Safe Evidence Snapshots In Existing Gate Payloads

**Decision**: Required-test evidence is represented as `ReferenceReadinessSnapshot` entries with safe pin payloads and counts in `RequiredTestSummary`.

**Rationale**: Publish gates already digest reference snapshots and pin summaries. Adding test-suite snapshots to that path makes replay and bundle provenance straightforward.

**Alternatives considered**:

- Add a separate publish-gate evidence response. Rejected because admins already consume the publish gate response and version summary.
