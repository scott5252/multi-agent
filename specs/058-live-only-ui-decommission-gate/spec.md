# Feature Specification: Live-Only UI Decommission Gate

**Feature Branch**: `codex/058-live-only-ui-decommission-gate`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Live-Only UI Decommission Gate. After Specs 050 through 057 replace deterministic domain builders with live projections, the final feature must remove obsolete mock/demo modules and enforce CI gates that prove production React routes never return backend-generated fixture data. The system must document live seed requirements, empty-state behavior, allowed computed metadata, test fixture boundaries, and rollback guidance."

## Clarifications

### Session 2026-05-08

- Q: What scanner surfaces are in scope for the final live-only gate? → A: Scan production admin UI route handlers, projection services, generated contracts, built production assets, navigation/bootstrap responses, and route response probes; classify test-only paths, docs, QA seed helpers, and historical specs through explicit policy instead of treating them as production failures (autopilot).
- Q: Are QA marker strings fully banned? → A: Fixed QA markers and fixture-like IDs are blocking in production code, built production assets, and production route responses when they masquerade as domain data; they remain allowed in tests, frontend test data, QA seed helpers, QA docs, validation manifests, and historical specs when explicitly categorized (autopilot).
- Q: How should built assets be scanned? → A: Scan only production-shipped built assets and manifests for prohibited user-visible fixture/domain markers, while treating content hashes, generated module identifiers, sourcemap-only references, and contract enum/schema names as non-blocking unless they surface fake domain data (autopilot).
- Q: How should route response probes authenticate? → A: Use deterministic local-principal and Auth0-shaped test principals for platform and tenant scopes, fail closed when a route lacks an authorized probe, and never broaden route permissions to make the scan pass (autopilot).
- Q: What QA seed data is required? → A: Seed representative persisted records for each completed live-data admin surface plus a fresh empty-state database path; if a surface is legitimately computed or empty, document that route's seed requirement as none with the expected reason (autopilot).
- Q: Which old modules are deleted versus retained? → A: Delete or disconnect obsolete deterministic production builders once no production import remains; retain fixtures only under test, QA, docs, or historical-spec boundaries with scanner policy entries and rollback guidance (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enforce Live-Only Route Contracts (Priority: P1)

Platform maintainers need a final decommission gate that classifies every
production admin UI route as live data, computed system metadata, empty,
denied, unavailable, or out of scope, and blocks regressions when a production
route returns deterministic fixture data.

**Why this priority**: Specs 050 through 057 replaced domain builders
individually. The platform still needs one central gate that proves those
surfaces stay live-only after future route or contract changes.

**Independent Test**: Run the live-only gate against the production admin UI
route inventory and verify that each route has an allowed classification and no
blocking mock/demo finding.

**Acceptance Scenarios**:

1. **Given** the production admin UI route inventory, **When** the gate scans
   route handlers, contracts, built assets, and response probes, **Then** every
   route is classified with a live-data source, computed-system source, or
   truthful empty/denied/unavailable outcome.
2. **Given** a production route returns a fixed domain row, fixed QA marker, or
   fake artifact/audit/run reference, **When** the gate runs, **Then** the
   result is blocking and identifies the owning route, evidence, and required
   remediation.
3. **Given** a route legitimately returns computed system metadata, **When**
   the gate runs, **Then** the result records why the metadata is allowed and
   does not require persisted domain rows.

---

### User Story 2 - Prove Empty And Seeded Live Behavior (Priority: P2)

Reviewers need the decommission gate to prove that production UI routes render
truthful empty states in a fresh database and live persisted evidence in a
seeded database, using authorized principals.

**Why this priority**: A route can pass static scanning while still hiding
fixture data behind response assembly or while showing populated UI in an empty
database. The final gate must test behavior, not only source text.

**Independent Test**: Run route response scans for empty and seeded QA states
with platform and tenant principals, then verify no route invents rows or leaks
unauthorized tenant details.

**Acceptance Scenarios**:

1. **Given** a fresh QA database with only required tenant/principal setup,
   **When** response probes load production admin UI JSON routes, **Then** the
   routes show empty, denied, unavailable, or computed-system states without
   invented domain rows.
2. **Given** a seeded QA database with persisted live evidence for representative
   admin surfaces, **When** response probes and browser validation run, **Then**
   displayed rows and references trace back to seed records, domain services, or
   allowed computed metadata.
3. **Given** a tenant-scoped principal, **When** the gate probes seeded routes,
   **Then** other-tenant labels, unauthorized operational detail, secrets, raw
   payloads, and private message content are absent.

---

### User Story 3 - Retire Obsolete Demo Surfaces Safely (Priority: P3)

Maintainers need obsolete deterministic projection modules, sample routes, and
migration-only mock helpers to be removed or explicitly retained as test-only
fixtures, with documentation that explains seed requirements and rollback.

**Why this priority**: Deleting old builders is valuable only if reviewers can
distinguish production mock data from legitimate tests and recover safely when a
live-only gate exposes missing seed coverage.

**Independent Test**: Inspect the decommission report and QA docs after the
gate runs, then verify each obsolete surface is deleted, dev/test-only, or
documented as allowed computed metadata with rollback guidance.

**Acceptance Scenarios**:

1. **Given** an obsolete deterministic production module is no longer imported
   by live routes, **When** decommission tasks run, **Then** the module is
   deleted or moved behind an explicit test-only boundary.
2. **Given** a fixture marker remains in tests, frontend test data, QA guides,
   or historical specs, **When** the gate scans it, **Then** the result records
   the allowed policy category rather than failing production validation.
3. **Given** a route cannot be seeded with representative live data, **When**
   reviewers read the QA guide, **Then** it names the missing seed requirement,
   expected empty-state behavior, and rollback or remediation path.

### Edge Cases

- A production route has no persisted rows but is expected to return computed
  system metadata such as asset manifest availability or migration scanner
  status.
- A route is reachable only by platform administrators and must fail closed for
  tenant administrators.
- A route returns safe route/bootstrap metadata that contains implementation
  terminology but no domain fixture rows.
- Built assets contain test-only fixture strings from bundled tests or QA docs
  that are not shipped through production routes.
- Generated contracts include schema examples, enum values, or historical
  route names that resemble fixture markers.
- QA seed setup partially succeeds and leaves a route in a truthful unavailable
  or empty state.
- A deleted deterministic module is still imported by a route test, docs sample,
  or stale generated asset.
- A legacy compatibility URL redirects to the new UI shell and must be checked
  without treating the redirect itself as mock data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain a production admin UI route inventory
  that identifies each route's owning surface, principal scope, response type,
  and live-data classification.
- **FR-002**: The live-only gate MUST block production route handlers and
  projection services from returning fixed domain entities, fixed QA markers,
  fake audit references, fake artifact references, fake link tokens, fake run
  IDs, fake usage events, fake workflow records, fake provider records, fake
  prompt/profile records, fake package records, fake users, fake delivery
  attempts, or fake mutation success.
- **FR-003**: The gate MUST allow computed system metadata only when the result
  is derived from current code, configuration, route inventory, generated asset
  state, scanner output, or explicit service availability.
- **FR-004**: The gate MUST distinguish production code and response surfaces
  from test-only fixtures, frontend test data, QA seed helpers, QA docs, and
  historical specification artifacts.
- **FR-005**: The gate MUST scan production route responses in both empty and
  seeded QA states and MUST verify that empty states do not invent domain rows.
- **FR-006**: Seeded route validation MUST prove representative production UI
  rows, IDs, audit references, artifact references, and summary counts trace to
  persisted records, authorized services, or allowed computed metadata.
- **FR-007**: Route response probes MUST authenticate with platform and
  tenant-shaped principals as appropriate for each route and MUST fail closed
  when authorization is missing or ambiguous.
- **FR-008**: The gate MUST flag any route response, browser-visible text,
  screenshot, export, log, or QA artifact that exposes raw secrets, credential
  values, provider authorization headers, raw prompts, raw completions, memory
  contents, raw run payloads, private channel messages, raw tool payloads,
  raw test transcripts, full Telegram identifiers, link tokens after creation,
  local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-009**: The decommission report MUST list every removed, retained, or
  allowed deterministic surface with owner, route impact, policy rationale, and
  remediation or rollback guidance.
- **FR-010**: The gate MUST fail validation when a production route depends on
  test fixture modules or frontend test data for backend-owned JSON contracts.
- **FR-011**: The system MUST document the seed requirements and expected empty
  state for every production admin UI route included in the live-only gate.
- **FR-012**: The gate MUST be runnable in local QA and CI-style validation and
  MUST produce deterministic, redaction-safe evidence that can be attached to
  QA docs and reviewer notes.
- **FR-013**: The gate MUST preserve compatibility redirects and historical docs
  unless they cause production UI responses to expose prohibited fixture data.
- **FR-014**: Required validation MUST include QA document validation, full Spec
  QA, browser UI validation, post-UI route/API or database evidence, and the
  multi-agent curl regression before the next spec starts.

### Key Entities *(include if feature involves data)*

- **Route Live-Data Classification**: The policy category for a production UI
  route, including live data, computed system metadata, truthful empty state,
  denied, unavailable, redirect-only, or out of scope.
- **Live-Only Gate Finding**: A scanner or route-probe result that identifies
  a prohibited or allowed fixture-like marker with severity, route, evidence,
  policy category, and remediation.
- **Route Response Probe**: An authenticated request against a production UI
  JSON or bootstrap surface in an empty or seeded QA state.
- **Seed Requirement**: The setup data or service condition needed for a route
  to show representative live rows during QA.
- **Decommission Decision**: The recorded outcome for an obsolete mock/demo
  surface: deleted, retained as test-only, allowed as computed metadata, or
  blocked pending remediation.
- **Rollback Record**: Reviewer-facing guidance that explains how to restore a
  deleted surface or relax a gate safely if validation exposes a false positive.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of production admin UI routes in the inventory have an
  explicit live-only classification and zero unresolved blocking findings.
- **SC-002**: Empty QA route probes complete without invented domain rows, fixed
  QA IDs, fake audit references, fake artifact references, or unauthorized
  tenant labels.
- **SC-003**: Seeded QA route probes and browser validation prove at least one
  representative live-data path or allowed computed-system path for every
  production admin UI surface.
- **SC-004**: Production route handlers and projection services import no
  test-only fixture modules or obsolete deterministic builders.
- **SC-005**: Reviewers can identify seed requirements, allowed fixture
  boundaries, decommission decisions, validation commands, and rollback
  guidance from QA docs and reviewer notes without reading implementation code.

## Assumptions

- Specs 050 through 057 have already converted their bounded production
  surfaces to live projections or truthful empty/denied/unavailable states.
- Test fixtures may remain under test-only paths and QA seed helpers may create
  deterministic records in dedicated QA databases for validation.
- Computed metadata is allowed only when it reflects current system state and
  is not pretending to be persisted domain data.
- This feature validates and removes production mock/demo surfaces; it does not
  rename migration-era user-facing labels, which is handled by Spec 059.
- User-managed commits happen after all remaining specs complete, so this
  feature records state in queue/status files without requiring an intermediate
  Git commit.
