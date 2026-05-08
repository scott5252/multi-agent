# Feature Specification: React Contract Provenance And Sample Route Retirement

**Feature Branch**: `codex/049-react-contract-provenance-and-sample-route-retirement`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for React Contract Provenance And Sample Route Retirement. The goal is to establish shared response provenance, empty-state, and live-data conventions for React contracts, remove or development-gate the sample patterns route, and stop production frontend components from supplying QA revision/idempotency defaults. Production React pages must either display live repository-backed data, computed system metadata, or a truthful empty state that names the missing live setup without inventing records."

## Clarifications

### Session 2026-05-07

- Q: Should provenance be modeled as shared envelope metadata or per-page ad hoc fields? -> A: (autopilot) Use shared backend-owned provenance and empty-state metadata that pages can embed consistently, while allowing page-specific detail inside typed metadata fields.
- Q: What should happen to `/admin/app/patterns` in production? -> A: (autopilot) Hide it from production navigation and ensure production-like requests cannot return sample data; retain only an explicit development-only gate if local development still needs it.
- Q: How should empty states describe missing live data? -> A: (autopilot) Empty states must state the missing durable setup or unavailable dependency in safe, user-facing language and must not invent rows, identifiers, or mutation evidence.
- Q: Where should revision, idempotency, and action defaults come from? -> A: (autopilot) Backend action metadata or generated client state supplies required defaults; production components must not hardcode fixed `qa0xx` values.
- Q: How should generated TypeScript contracts change? -> A: (autopilot) Regenerate contracts from Pydantic schemas so provenance, empty-state, and action metadata fields are typed, and ensure sample route contracts are absent or development-gated.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show Backend-Owned Provenance And Empty States (Priority: P1)

A platform operator or tenant administrator opens React admin pages and can tell whether the page is showing live persisted data, computed system metadata, an authorized empty state, a denied state, or an unavailable dependency state without the browser inventing sample rows or domain IDs.

**Why this priority**: Later live-data specs need a shared contract pattern so every page can communicate honest source status while fake rows are removed.

**Independent Test**: Exercise representative React JSON endpoints with empty and seeded QA databases and verify responses include backend-owned provenance and empty-state metadata with no fixed domain entities.

**Acceptance Scenarios**:

1. **Given** a React JSON endpoint has no persisted rows for the authorized scope, **When** the page contract is requested, **Then** the response identifies the missing live setup and returns an empty state rather than synthetic rows.
2. **Given** a React JSON endpoint reports computed metadata such as navigation, route inventory, generated contract status, or migration evidence, **When** the page contract is requested, **Then** the response names the computed source and does not present the metadata as persisted domain data.
3. **Given** a principal is denied access to a tenant-scoped page, **When** the page contract is requested, **Then** the response remains fail-closed and does not reveal unauthorized tenant labels, sample entities, or fixture identifiers.

---

### User Story 2 - Retire Production Sample Patterns Route (Priority: P2)

A production administrator cannot reach `/admin/app/patterns` as a sample data page. If the sample patterns route is retained at all, it is explicitly development-only and unavailable from production navigation and production JSON/API surfaces.

**Why this priority**: The sample patterns route was useful during React foundation work, but it is now a production mock-data risk and should not be reachable as a normal admin page.

**Independent Test**: Request `/admin/app/patterns` and related JSON/bootstrap surfaces in production-like configuration and verify the route is hidden, redirected, or unavailable without sample records; in development-only configuration, verify any retained route is clearly gated.

**Acceptance Scenarios**:

1. **Given** production configuration, **When** a platform admin opens `/admin/app/patterns`, **Then** the route does not show sample pattern data and is absent from admin navigation.
2. **Given** production configuration, **When** frontend bootstrap or navigation contracts are loaded, **Then** sample pattern destinations are not listed as authorized destinations.
3. **Given** an explicit development-only configuration, **When** the patterns route is intentionally enabled, **Then** tests prove the route is marked as sample/development-only and still does not enter production validation evidence.

---

### User Story 3 - Remove Frontend QA Defaults From Production Actions (Priority: P3)

A maintainer can review production frontend code and generated contracts and see that React components no longer supply fixed QA revision tokens, idempotency keys, request IDs, or fake success values for admin actions. Any required default comes from backend action metadata, generated client state, or a browser-generated non-domain value.

**Why this priority**: Action defaults can silently create fake mutation evidence even after route rows become live.

**Independent Test**: Run frontend tests, generated contract checks, and scanner checks that fail when production components hardcode `qa0xx` revision, idempotency, or action identifiers outside test-only fixtures.

**Acceptance Scenarios**:

1. **Given** a production React action needs a revision token, idempotency key, or request identifier, **When** the component prepares the action, **Then** the value comes from backend metadata or generated client state rather than a fixed QA string.
2. **Given** frontend tests need deterministic inputs, **When** those tests run, **Then** test-only fixtures remain under test paths and are not imported by production bundles.
3. **Given** generated TypeScript contracts are inspected, **When** contract generation runs, **Then** no sample route contract or production QA default marker is emitted unless it is explicitly test-only or development-gated.

### Edge Cases

- Empty live databases must produce sparse but useful page states, not generic failures and not synthetic records.
- Computed system metadata must be labeled as computed and must name its derivation source.
- Local-principal QA must still exercise authorization, tenant scoping, and browser rendering without relying on production sample pages.
- Development-only sample routes, if retained, must require an explicit configuration flag that is off in production and absent from production navigation.
- Existing component tests may retain fixture markers only under test-only paths.
- Scanner output and QA evidence must not expose raw secrets, raw prompts, raw payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: React page JSON contracts MUST expose backend-owned source provenance where the page can return persisted live data, computed system metadata, empty state, denied state, or unavailable state.
- **FR-002**: Empty-state metadata MUST describe the missing live setup or dependency in reviewer-safe language and MUST NOT invent workflows, users, providers, prompts, skill packages, usage rows, audit rows, link tokens, run IDs, or artifact references.
- **FR-003**: Shared React admin schemas MUST support provenance and empty-state metadata in a way that can be reused by later domain specs without moving authorization, tenant scoping, mutation approval, credential readiness, or redaction logic into the browser.
- **FR-004**: Generated TypeScript contracts MUST represent the backend-owned provenance and empty-state fields and MUST remain synchronized with the Pydantic schemas.
- **FR-005**: Production admin bootstrap and navigation MUST NOT advertise `/admin/app/patterns` or any sample patterns destination.
- **FR-006**: Production requests to `/admin/app/patterns` MUST NOT return sample pattern data; the route MUST be removed, redirected, denied, or development-gated with an explicit off-by-default setting.
- **FR-007**: If a development-only patterns route is retained, route tests MUST prove it is unavailable under production-like configuration and available only when the development setting is explicitly enabled.
- **FR-008**: Production frontend components MUST NOT provide fixed QA revision tokens, idempotency keys, request IDs, mutation success values, or sample action payloads outside generated client state or backend-provided action metadata.
- **FR-009**: Test fixtures and deterministic QA helpers MAY remain under test-only paths, but production frontend source, generated contracts, and built assets MUST NOT import or bundle those fixtures.
- **FR-010**: Backend tests MUST cover Auth0-shaped and local-principal behavior for provenance metadata, sample route retirement, route access, and redaction safety.
- **FR-011**: Validation MUST include empty-database and seeded-database checks for the affected route/bootstrap surfaces, plus scanner checks proving no production fixture markers were introduced.
- **FR-012**: QA docs, screenshots, route responses, logs, generated contracts, and reviewer notes MUST remain free of raw secrets, credential values, raw prompts, raw completions, memory contents, private messages, raw tool payloads, raw run payloads, stack traces, full external identifiers, local filesystem paths, and unauthorized tenant labels.

### Key Entities

- **Response Provenance**: Backend-owned metadata describing whether page data comes from durable repositories, computed system metadata, an empty live setup, an unavailable dependency, or an authorization denial.
- **Empty State Descriptor**: Reviewer-safe text and machine-readable reason codes for pages with no authorized persisted rows.
- **Sample Route Gate**: Configuration and route behavior that prevents sample patterns from being reachable in production.
- **Action Metadata**: Backend or generated-client metadata used to prepare mutations without fixed QA revision or idempotency defaults.
- **Contract Generation Evidence**: Validation output proving Pydantic schemas and generated TypeScript contracts agree on provenance, empty-state, and route-retirement fields.
- **Fixture Marker Finding**: Scanner evidence for fixed QA strings or sample data that must be absent from production source and bundles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Representative React JSON contracts include backend-owned provenance or empty-state metadata for empty and seeded QA database states.
- **SC-002**: `/admin/app/patterns` is absent from production navigation and cannot return sample pattern data under production-like configuration.
- **SC-003**: Generated TypeScript contracts pass synchronization checks after provenance and empty-state schema changes.
- **SC-004**: Production frontend source, generated contracts, and built assets contain zero unallowlisted fixed QA action defaults introduced by this spec.
- **SC-005**: Auth0-shaped backend tests and local-principal Playwright validation prove production users see honest live, empty, denied, or unavailable states without sample records.
- **SC-006**: QA document validation, Spec QA, Playwright UI validation, post-UI API/database verification, and the full curl walkthrough pass for `qa049`.

## Assumptions

- Spec 048 provides the live-data scanner, route inventory, and allowlist taxonomy used to detect new production fixture markers.
- Later Specs 050 through 057 will replace domain-specific mock projection builders; this spec establishes shared provenance and route-retirement conventions instead of removing every domain builder.
- Existing tests may keep deterministic fixture data as long as those fixtures remain under test-only paths and are not imported by production source.
- Development-only sample route access, if retained, is controlled by explicit configuration and is off in production-like QA.
- No destructive data migration is required for this feature.

## Testing Instructions

- Run focused backend tests for provenance schemas, admin bootstrap/navigation, sample route retirement, production/development route gating, and redaction safety.
- Run generated TypeScript contract checks and frontend tests for shared state, navigation, and action metadata handling.
- Run live-data scanner checks against production source, generated contracts, and built assets.
- Run QA document validation, Spec QA, Playwright UI validation through local-principal login, post-UI API/database verification, and the `multi-agent-curl-test` runner before marking the spec complete.

## PR Review Guidance

- Confirm provenance and empty-state metadata are backend-owned and reusable by later specs.
- Confirm sample patterns cannot appear in production navigation or route responses.
- Confirm frontend production code no longer supplies fixed QA revision, idempotency, or action defaults.
- Confirm test fixtures remain test-only and scanner evidence is redaction-safe.
- Confirm no later domain live-data replacement work has been pulled into this shared convention spec.

## Documentation Impact

- Add QA049 API guide, UI walkthrough, QA environment file, manual user guide, and reviewer notes.
- Update migration or live-data cleanup notes to describe shared provenance, honest empty states, and sample route retirement.
- Update README or quickstart references only if the sample route retirement changes documented local development workflows.
