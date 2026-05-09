# Research: Design Reviewer Template, Test Bench, And Publish Gates

## Decision: Use an explicit install action

**Decision**: Provide a tenant-scoped admin install action for the Design
Reviewer Council template, with idempotent replay semantics and safe setup
summaries.

**Rationale**: The roadmap requires reusable templates and QA evidence to be
explicit durable setup rather than hidden fixture behavior. A direct action is
auditable, testable, and easy for the Admin workspace and curl regression to
exercise.

**Alternatives considered**:

- Hidden seed script: rejected because production Admin would not have a real
  setup path.
- Migration-created template: rejected because tenant admins need explicit
  control and idempotency.
- Static in-memory template: rejected because publish evidence must attach to a
  durable workflow draft revision.

## Decision: Reuse Workflow Registry draft and publish gates

**Decision**: The install service creates or reuses a workflow draft using the
existing workflow registry service and evaluates readiness through the existing
publish-gate path.

**Rationale**: Workflow registry already owns draft revisions, validation,
publish bundles, sharing, and required evidence freshness. Reusing it avoids a
parallel publication mechanism.

**Alternatives considered**:

- Separate design-review template table: rejected unless implementation finds a
  missing durable field, because the template is primarily a workflow draft plus
  evidence.
- Direct SQL writes: rejected because service-layer validation, audit, tenant
  checks, and revision semantics would be bypassed.

## Decision: Attach Agent Test Bench required evidence

**Decision**: Installation creates or reuses a required Agent Test Bench suite
for the workflow draft and launches safe-mode runs targeted to the current draft
revision.

**Rationale**: Existing publish gates can require fresh passing Test Bench
evidence. The roadmap specifically asks for deterministic and model-backed
safe-mode behavior and current evidence before publish.

**Alternatives considered**:

- Store evidence in design-review session tables: rejected because it would not
  integrate with current workflow publish gates.
- Treat QA scripts as evidence: rejected because publish gates need durable
  repository-backed records.

## Decision: Surface template readiness in Admin workspace

**Decision**: Extend the Spec 063 design-review workspace envelope with a live
template setup summary and install action.

**Rationale**: Admin users need to understand whether the tenant has installed
the council template and whether evidence is ready. The same workspace already
anchors design-review sessions, rounds, and handoffs.

**Alternatives considered**:

- Add a standalone page: rejected for this spec because the existing workspace
  is the natural operational surface.
- Render static guidance only: rejected because Admin routes must be live-data
  only and must not imply setup has succeeded.

## Decision: Keep local QA deterministic and provider-safe

**Decision**: Local QA uses deterministic Test Bench runs and model-backed
safe-mode records that prove gateway boundaries without calling live provider
services.

**Rationale**: The repository guidance forbids real provider calls unless a
spec explicitly approves them. This spec asks for safe-mode behavior, so
evidence should verify boundaries without external side effects.

**Alternatives considered**:

- Live model probes: rejected because they require credentials and can leak
  provider behavior into non-deterministic QA.
- UI-only validation: rejected because the publish gate must use durable
  evidence, not screenshots.
