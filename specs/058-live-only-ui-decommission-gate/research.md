# Research: Live-Only UI Decommission Gate

## Decision: Extend The Existing Live-Data Inventory As The Final Gate

**Rationale**: Spec 048 already introduced route targets, marker kinds,
allowlist entries, findings, evidence, and dashboard summaries. Extending that
boundary keeps migration hardening evidence in one place and avoids a second
scanner with overlapping policy.

**Alternatives considered**:

- Create a standalone CI-only scanner script. Rejected because the browser
  migration dashboard still needs the same classification and reviewer evidence.
- Move all policy into frontend checks. Rejected because backend-owned JSON
  contracts and authorization decisions must remain server-side.

## Decision: Block Fixture-Like Markers Only In Production-Reachable Surfaces

**Rationale**: QA seed scripts, tests, validation manifests, feature docs, and
historical specs intentionally use deterministic IDs. The gate should prevent
production routes from returning those values as live domain data without
making validation impossible.

**Alternatives considered**:

- Ban every `qa0xx` marker in the repository. Rejected because QA fixtures and
  spec artifacts need stable identifiers.
- Allow all generated contract markers. Rejected because generated contracts
  can still expose fake production defaults if source routes define them.

## Decision: Scan Production Built Assets With Narrow False-Positive Policy

**Rationale**: Built assets are what browsers receive, so they must not contain
user-visible fake domain rows. Content hashes, generated chunk names,
sourcemap-only references, and enum/schema names are not domain rows unless the
same marker appears in visible route data or UI copy.

**Alternatives considered**:

- Skip built assets and trust source scans. Rejected because stale production
  assets can keep forbidden strings after source cleanup.
- Treat every built string as blocking. Rejected because bundlers create
  non-domain identifiers that do not reach users as data.

## Decision: Route Probes Use Explicit Platform And Tenant Principals

**Rationale**: The final gate must prove authorization and tenant isolation at
the same time as live-only behavior. Probes should use the same deterministic
principal shapes used by existing route tests and local-principal browser QA.

**Alternatives considered**:

- Probe only as platform admin. Rejected because tenant-scoped leaks would be
  missed.
- Probe without authentication. Rejected because denied states are not enough
  to prove authorized route behavior.

## Decision: Validate Both Fresh And Seeded QA States

**Rationale**: Empty databases must render honest empty/unavailable states, and
seeded databases must prove representative routes read persisted records. The
gate is complete only when both behaviors are visible in evidence.

**Alternatives considered**:

- Validate only seeded data. Rejected because old deterministic builders often
  hide in empty-state behavior.
- Validate only empty state. Rejected because route projections could be empty
  while broken for real persisted data.

## Decision: Delete Production Mock Surfaces Only After Import Ownership Is Clear

**Rationale**: Some deterministic strings belong in test fixtures or historical
specs. Deleting production modules is safe when no production route imports
them and tests have moved to fixture paths or live seed helpers.

**Alternatives considered**:

- Delete every file with fixture markers. Rejected because this would remove
  legitimate tests and QA setup.
- Leave obsolete production modules as unused code. Rejected because stale
  modules invite future regressions and confuse reviewer evidence.

## Decision: CI-Style Validation Runs Through Existing Spec QA

**Rationale**: `run_spec_qa.py`, QA doc validation, Playwright, and the
multi-agent curl runner already coordinate database setup, migrations, local
server processes, and artifact capture. The gate should plug into that
validation chain rather than creating an independent CI runner.

**Alternatives considered**:

- Add a separate CI job outside Spec QA. Rejected for this spec because local
  autopilot validation must prove the behavior immediately.
- Run route probes only in Playwright. Rejected because API-level evidence is
  easier to assert and safer for redaction checks.

## Decision: Rollback Guidance Is Reviewer Documentation, Not Runtime Toggle

**Rationale**: Reintroducing mock data through a runtime flag would undermine
the live-only policy. Rollback guidance should explain how to revert a
specific removal or narrow a false positive under review.

**Alternatives considered**:

- Add a "show demo data" flag. Rejected because production route handlers must
  not expose backend-generated fixture rows.
- Omit rollback guidance. Rejected because decommissioning code still needs a
  safe review and recovery path.
