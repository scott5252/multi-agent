# Feature Specification: Live Data Inventory And Mock Guardrails

**Feature Branch**: `codex/048-live-data-inventory-and-mock-guardrails`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Live Data Inventory And Mock Guardrails. The React admin surfaces from Specs 026 through 047 fetch backend JSON, but many backend projection builders still return deterministic fixture/demo data. The goal is to produce a deletion-grade inventory of every production code path that can return hardcoded domain rows, fixed qa0xx IDs, fake audit references, fake artifact references, fake link tokens, fake usage events, fake run IDs, or fake mutation success. The feature must define live-only policy, classify which computed system metadata is allowed, and add guardrails that prevent new mock data from being exposed by production React routes."

## Clarifications

### Session 2026-05-07

- Q: What counts as prohibited mock data versus legitimate computed system metadata? -> A: (autopilot) Prohibited mock data is any fixed domain entity, identifier, mutation result, or evidence value returned by production React routes; legitimate computed metadata must be derived from code, configuration, route registration, asset manifests, feature flags, or scanner output with a documented source.
- Q: May sample or pattern routes remain available? -> A: (autopilot) They may remain only when explicitly development/test gated or classified for retirement by Spec 049; production navigation and production route responses must not expose sample domain rows.
- Q: How should dedicated QA seed data be treated? -> A: (autopilot) QA seed data is allowed only when created through documented setup flows, domain services, repositories, QA migrations, or public/admin APIs, and scanner output must distinguish it from fixed production builders.
- Q: Are fixture markers such as qa031 prohibited? -> A: (autopilot) They are prohibited in production route responses, production frontend bundles, generated contracts, and projection builders unless narrowly allowlisted as scanner-derived or computed system metadata.
- Q: Which scanners must be CI-blocking? -> A: (autopilot) Production source import scans, marker taxonomy scans, generated contract scans, built asset scans, and route response scans must be CI-blocking for unallowlisted prohibited findings; inventory-only summaries may remain non-blocking for already mapped legacy findings while later specs remove them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inventory Production Mock Surfaces (Priority: P1)

A platform operator needs an authoritative inventory of every production React admin route, backend projection builder, frontend source file, generated contract, and built asset that can expose deterministic fixture or demo data so later live-data cleanup specs can remove the right code without guessing.

**Why this priority**: The remaining roadmap depends on a deletion-grade worklist. Without it, later specs risk missing routes, deleting test fixtures, or replacing one fake source with another.

**Independent Test**: Run the scanner against the current repository and confirm the inventory artifact lists each known production mock/demo surface from the roadmap with severity, owning route, source path, marker taxonomy, replacement spec, and durable data source guidance.

**Acceptance Scenarios**:

1. **Given** the repository after Specs 026 through 047, **When** the live-data scanner runs, **Then** it records every known deterministic production surface from `remove_mock_data_specs.md` with a route or module owner and replacement spec.
2. **Given** a production route handler or projection builder contains a fixed `qa0xx` identifier or fake domain row, **When** the scanner evaluates production paths, **Then** the finding is classified as prohibited unless it is covered by an explicit computed-system-metadata allowlist.
3. **Given** a test fixture under `tests/` or `frontend/admin/src/test`, **When** the scanner sees fixture-like markers, **Then** the marker is excluded from production findings and summarized as test-only evidence.

---

### User Story 2 - Define Live-Only Policy And Allowed Metadata (Priority: P2)

A reviewer needs a clear policy that distinguishes prohibited deterministic domain data from allowed computed system metadata so each future cleanup spec can make consistent decisions and avoid overbroad allowlists.

**Why this priority**: The scanner must be strict enough to catch fake data but precise enough to preserve legitimate migration, route inventory, asset manifest, and scanner-derived evidence.

**Independent Test**: Review the generated policy, allowlist, and inventory classifications, then verify that allowed entries are derived from code, configuration, route metadata, asset manifests, or scanner output rather than hardcoded domain entities.

**Acceptance Scenarios**:

1. **Given** migration dashboard evidence reports route availability or React asset manifest status, **When** the scanner classifies it, **Then** it is allowed only as computed system metadata with a documented derivation source.
2. **Given** a response includes fake workflows, prompts, providers, skill packages, users, deliveries, usage events, link tokens, run IDs, audit IDs, or artifact references, **When** the live-only policy is applied, **Then** the response is marked prohibited for production routes.
3. **Given** a future spec needs a temporary exception, **When** the allowlist is reviewed, **Then** the exception must name the route, source path, marker, reason, replacement spec, and removal condition.

---

### User Story 3 - Block New Production Mock Regressions (Priority: P3)

A maintainer needs automated guardrails that fail when new production React routes or assets expose unallowlisted fixture markers so the live-data cleanup does not regress while Specs 049 through 059 are implemented.

**Why this priority**: The cleanup spans many specs. Guardrails must prevent new deterministic data from entering production code while domain-specific replacements are still in progress.

**Independent Test**: Add a synthetic prohibited marker to a production route or frontend source fixture in a local branch and confirm the scanner/test command exits nonzero with a redaction-safe finding that points to the file and marker class.

**Acceptance Scenarios**:

1. **Given** a new production route imports a test fixture module, **When** CI scanner tests run, **Then** the command fails and reports the import path without exposing raw secrets or payloads.
2. **Given** `/admin/app` JSON endpoints are exercised with an empty QA database, **When** route response scans run, **Then** responses must contain live data, allowed computed metadata, or truthful empty/denied/unavailable states only.
3. **Given** the same routes are exercised after documented QA seeding, **When** route response scans run, **Then** seeded rows must be backed by persisted state or domain services and must not be frontend or backend fixed demo data.

### Edge Cases

- A route may be legitimate computed metadata rather than domain data, such as React asset manifest availability, route inventory, feature flag summaries, scanner-derived migration evidence, or decommission status.
- A production source file may contain historical spec names or documentation strings that are not returned by runtime routes; such findings must be low severity or informational unless they can reach production responses.
- Built frontend assets may contain `qa0xx` strings from test-only code only if the build excludes test modules; otherwise the scanner must flag the built asset and trace it back to a production import.
- Empty databases are expected to produce sparse UI states. The route response scanner must treat truthful empty states as success, not as missing data.
- Scanner output must be redaction-safe even when route responses contain unexpected error payloads.
- The feature must not replace major deterministic domain builders; that removal is reserved for Specs 050 through 057 and the final gate in Spec 058.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a live-data scanner that inventories production React admin route handlers, backend projection builders, frontend production source, generated TypeScript contracts, and built assets for prohibited deterministic fixture markers.
- **FR-002**: System MUST classify findings by severity, marker taxonomy, source file, route or asset owner, owning roadmap spec, replacement spec, durable data source expectation, and whether the finding can reach production responses.
- **FR-003**: System MUST define a live-only policy that prohibits hardcoded domain entities, fixed `qa0xx` identifiers, fake audit references, fake artifact references, fake link tokens, fake usage events, fake run IDs, fake mutation success, fake workflows, fake providers, fake prompts, fake skill packages, fake users, and fake delivery attempts in production React route responses.
- **FR-004**: System MUST allow computed system metadata only when it is derived from code/configuration, route registration, feature flags, asset manifests, scanner output, or other non-domain system state, and each allowed item MUST include a reason and source.
- **FR-005**: System MUST preserve test fixtures under test-only paths and QA seed helpers while preventing production code from importing or mirroring those fixtures.
- **FR-006**: System MUST enumerate every production `/admin/app` JSON endpoint covered by the React admin UI and identify the local-principal role needed to exercise each route.
- **FR-007**: System MUST add route response scans for empty QA database state and seeded QA database state that verify responses do not contain unallowlisted fixture markers.
- **FR-008**: System MUST include Auth0-shaped backend route tests and local-principal browser validation for the inventory and guardrail surface.
- **FR-009**: System MUST update migration dashboard evidence or equivalent reviewer-facing documentation with inventory totals, allowed computed metadata, prohibited findings, replacement spec mapping, and readiness status.
- **FR-010**: System MUST add CI-suitable tests or commands that fail when production code imports test fixtures or exposes new unallowlisted fixture markers.
- **FR-011**: System MUST keep scanner output, route response evidence, docs, screenshots, and logs free of raw secrets, provider authorization headers, raw prompts, raw completions, memory contents, private channel messages, raw tool payloads, raw run payloads, stack traces, full external identifiers, local filesystem paths, and unauthorized tenant labels.
- **FR-012**: System MUST produce the required QA artifacts for `qa048`, including API/quality guide, UI walkthrough, QA environment file, manual user guide, and reviewer notes.
- **FR-013**: System MUST NOT remove or replace major deterministic domain builders in this spec except to fix scanner false positives or to avoid returning scanner-owned fixture data.

### Key Entities

- **Mock Data Finding**: A scanner finding for a prohibited or reviewed marker, including marker class, source path, route owner, severity, replacement spec, and reachability evidence.
- **Route Scan Target**: A production React JSON endpoint with route path, principal role, tenant scope, expected empty-state behavior, and seeded-state setup requirement.
- **Computed Metadata Allowlist Entry**: A reviewed exception for non-domain system metadata with derivation source, reason, scope, and removal condition when temporary.
- **Scan Run Summary**: The aggregate evidence for a scanner run, including totals, failed checks, skipped test-only paths, redaction-safe output paths, and command status.
- **Replacement Spec Mapping**: The roadmap mapping that points each prohibited production surface to Specs 049 through 058 for live-data removal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The scanner inventory covers 100 percent of known production mock/demo surfaces listed in `remove_mock_data_specs.md` for Spec 048.
- **SC-002**: A newly introduced unallowlisted fixture marker in production route, projection, frontend source, generated contract, or built asset checks causes the scanner or associated test command to fail with a redaction-safe finding.
- **SC-003**: Every enumerated `/admin/app` JSON route has an empty-database response scan and a seeded-database response scan, or a documented reason why the route is computed metadata only.
- **SC-004**: Test-only fixture paths are excluded from production findings with zero false-positive failures in `tests/` and `frontend/admin/src/test`.
- **SC-005**: Reviewers can identify the replacement spec and durable data source expectation for each prohibited production finding in one generated inventory artifact.
- **SC-006**: Backend quality gates, frontend build/type gates, QA document validation, Playwright UI validation, post-UI API/database verification, and the full curl walkthrough pass for `qa048`.

## Assumptions

- The source of truth for the initial worklist is `remove_mock_data_specs.md`, and the scanner may expand that list when it finds additional production surfaces.
- Production React route handlers are FastAPI routes and backend projection services under `src/multi_agent_platform`; production frontend source is under `frontend/admin/src` excluding test-only modules.
- Generated contracts and built assets are scanned because fixture markers can leak through generation or bundling even when source files look clean.
- QA seed data is allowed only when created through documented setup flows, domain services, repositories, migrations intended for QA, or public/admin APIs.
- The migration dashboard is an acceptable reviewer-facing evidence location when it presents scanner-derived or computed system metadata rather than fake domain rows.
- Future specs may leave existing prohibited findings in place temporarily, but no new unallowlisted production fixture markers may be introduced after Spec 048.

## Testing Instructions

- Run the live-data scanner in inventory mode and CI mode.
- Run focused unit and integration tests for scanner taxonomy, allowlist behavior, route enumeration, production import guardrails, empty-database responses, seeded-database responses, and redaction safety.
- Run generated contract checks, frontend tests/typecheck/build for affected React evidence surfaces, and full repository quality gates.
- Run Spec QA validation, Playwright UI validation through local-principal login, post-UI API or QA database verification, and the `multi-agent-curl-test` runner before marking the spec complete.

## PR Review Guidance

- Confirm the scanner finds all roadmap-listed production surfaces and does not merely encode the current inventory by hand.
- Confirm allowlist entries are narrow, justified, and tied to computed system metadata rather than domain fixture data.
- Confirm production code cannot import test fixtures and that test-only markers do not fail CI.
- Confirm scanner, route responses, screenshots, and docs are redaction-safe.
- Confirm major live-data replacements are deferred to later specs unless a small scanner false-positive fix requires a local change.

## Documentation Impact

- Add or update QA048 API guide, UI walkthrough, QA environment file, manual user guide, and reviewer notes.
- Update migration or live-data cleanup documentation with the generated inventory artifact, live-only policy, and replacement spec mapping.
- Update README or quickstart references only if the new scanner command becomes part of the standard local validation flow.
