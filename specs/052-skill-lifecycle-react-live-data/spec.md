# Feature Specification: Skill Lifecycle React Live Data

**Feature Branch**: `codex/052-skill-lifecycle-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Skill Lifecycle React Live Data. Replace deterministic skill lifecycle builders with live projections from skill package, version, tenant grant, installation, credential, readiness, smoke-test, quarantine, audit, governed connector, and SkillExecutionGateway services. React must display only real packages, versions, installations, credential reference readiness, smoke-test evidence, binding eligibility, connector diagnostics, quarantine decisions, withdrawal state, and audit records."

## Clarifications

### Session 2026-05-07

- Q: What manifest and validation content may React and QA evidence display? → A: Safe summaries only; raw manifests, raw validation transcripts, raw connector payloads, raw tool payloads, and local paths never render in React or QA evidence. (autopilot)
- Q: Which smoke-test and connector diagnostic execution modes are allowed in local QA? → A: Use mocked-safe or local allowlisted diagnostic execution only; no real external connector, provider, credential, or outbound calls run unless an explicit approved artifact marks a live probe path. (autopilot)
- Q: How should package availability and installability be determined? → A: Resolve availability through persisted package version state, tenant grants, installation state, quarantine or withdrawal state, credential readiness, and policy records for the active scope; never synthesize installable or bindable evidence. (autopilot)
- Q: What lifecycle actions must return when state is stale, unauthorized, or unavailable? → A: Return durable accepted evidence for persisted changes, stale conflict for revision mismatches, denied for unauthorized requests, and unavailable or blocked when required live records are absent. (autopilot)
- Q: How should binding eligibility and diagnostics handle missing or sensitive evidence? → A: Use existing governed skill services, connector diagnostics, SkillExecutionGateway summaries, and audit records; show safe blocked or unavailable reasons when inputs are missing and summarize sensitive evidence before it reaches React. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Skill Lifecycle State (Priority: P1)

A platform operator or tenant administrator opens the skill lifecycle workspace and sees only authorized live skill package, version, grant, discovery, installation, credential readiness, smoke-test, diagnostic, eligibility, quarantine, withdrawal, and audit records for the active scope. If the active database has no relevant records, each panel presents a truthful empty, denied, or unavailable state instead of deterministic demonstration rows.

**Why this priority**: This is the core live-data migration outcome. Reviewers need to trust that the skill lifecycle workspace reflects durable governance state and does not invent packages, installations, credentials, smoke tests, or audit entries.

**Independent Test**: Can be tested by loading the skill lifecycle workspace with an empty QA database and with QA-seeded live records, then comparing the browser and JSON responses to the persisted skill lifecycle state.

**Acceptance Scenarios**:

1. **Given** an authorized platform operator and an empty live database, **When** the operator opens the skill lifecycle workspace, **Then** package, candidate, tenant grant, installation, credential, readiness, diagnostic, eligibility, quarantine, withdrawal, and audit panels show truthful empty or unavailable states with safe setup guidance.
2. **Given** an authorized platform operator and persisted QA skill package records, **When** the operator opens the skill lifecycle workspace, **Then** the package list, package version detail, candidate workspace, tenant grant summary, discovery projection, audit timeline, and lifecycle action availability match only persisted records.
3. **Given** an authorized tenant administrator and persisted tenant installation records, **When** the administrator opens tenant-scoped skill lifecycle views, **Then** discovery, installation, credential readiness, smoke-test history, connector readiness, binding eligibility, and diagnostics show only records authorized for that tenant.
4. **Given** an unauthorized or cross-tenant principal, **When** the principal requests skill lifecycle data, **Then** the response is denied or redacted without exposing package names, tenant labels, installation ids, credential references, connector payloads, or audit details from another tenant.

---

### User Story 2 - Inspect Redaction-Safe Skill Details (Priority: P2)

An authorized reviewer opens package, installation, credential readiness, smoke-test, connector diagnostic, binding eligibility, quarantine, withdrawal, and audit details and receives enough evidence to understand state without seeing raw manifests, raw connector payloads, credential values, external tool payloads, private tenant labels, local paths, or stack traces.

**Why this priority**: Skill lifecycle records include sensitive-adjacent metadata. The workspace must be useful for governance while preserving secret hygiene, tenant isolation, and connector safety.

**Independent Test**: Can be tested by seeding package manifests, credential references, smoke-test outcomes, diagnostic summaries, eligibility decisions, quarantine decisions, and audit rows containing sensitive-adjacent source values, then verifying that React and JSON responses contain only safe summaries and artifact references.

**Acceptance Scenarios**:

1. **Given** a package version with a persisted manifest summary and validation evidence, **When** an authorized reviewer views package detail, **Then** the UI shows package identity, version state, validation status, artifact references, safe manifest summary, tenant grant status, and lifecycle actions without raw manifest content.
2. **Given** an installation with credential reference metadata, **When** a tenant administrator views credential readiness, **Then** the UI shows readiness, masked reference metadata, safe remediation guidance, and latest check time without credential values or provider authorization headers.
3. **Given** persisted smoke-test and connector diagnostic results, **When** a reviewer opens diagnostics, **Then** the UI shows safe outcome summaries, timestamps, audit references, and artifact references without raw connector request or response payloads.
4. **Given** a package quarantine, withdrawal, or denied eligibility decision, **When** a reviewer inspects lifecycle evidence, **Then** the UI explains the persisted decision and safe reason without exposing unauthorized tenant data or raw validation transcripts.

---

### User Story 3 - Exercise Durable Skill Lifecycle Actions (Priority: P3)

An authorized user performs at least one safe visible lifecycle action from the skill lifecycle workspace, and the result persists through backend services. Examples include validating a candidate, publishing a package version, granting tenant availability, configuring credential references, running a mocked-safe smoke test, previewing binding eligibility, quarantining or withdrawing a package, or running governed connector diagnostics.

**Why this priority**: The live-data migration must prove mutations are durable service outcomes, not browser-only or backend-fixed success messages.

**Independent Test**: Can be tested by performing a user-visible lifecycle action in Playwright, then verifying the persisted result through a backend API first and a redaction-safe QA database query when the API cannot expose the needed evidence.

**Acceptance Scenarios**:

1. **Given** a seeded package candidate and an authorized platform operator, **When** the operator runs package validation or publication, **Then** the mutation returns persisted validation or package version evidence and the refreshed workspace shows the updated state.
2. **Given** a seeded tenant installation and an authorized tenant administrator, **When** the administrator saves credential reference metadata or runs a mocked-safe smoke test, **Then** the mutation persists readiness or smoke-test evidence and the refreshed workspace shows the latest safe result.
3. **Given** a seeded skill binding context and an authorized reviewer, **When** the reviewer previews binding eligibility or runs governed connector diagnostics, **Then** the response is based on persisted policy, credential, installation, and diagnostic records and avoids raw connector payloads.
4. **Given** a stale or unauthorized lifecycle action, **When** the user submits it, **Then** the system returns a safe conflict, denied, or unavailable result without creating fake successful evidence.

---

### Edge Cases

- Empty platform package catalog, empty tenant discovery list, empty tenant installation list, and empty audit timeline all return truthful empty states.
- Package candidates without validation evidence show unavailable validation state and cannot appear as valid published packages.
- Package versions with missing artifact metadata show unavailable artifact evidence, not synthetic artifact references.
- Tenant grants revoked or withdrawn after initial page load are reflected after refresh and cannot remain available due to frontend state alone.
- Credential readiness with missing secret references shows safe remediation guidance and never prints a credential value.
- Smoke-test requests in local QA use mocked-safe or local allowlisted execution only and never call real external tools.
- Connector diagnostics with raw request or response payloads are summarized before reaching React.
- Binding eligibility previews with missing profile, skill, installation, credential, or policy records return unavailable or blocked states.
- Quarantined packages cannot be presented as installable or bindable for tenant users.
- Withdrawn packages and versions remain visible only as historical or audit-safe records where authorized.
- Cross-tenant package, installation, credential, and audit identifiers fail closed.
- Auth0-shaped principals and local-principal QA identities produce the same authorization outcomes for equivalent roles.
- Generated TypeScript contracts reject malformed lifecycle responses and accept empty-state envelopes.
- QA screenshots, docs, and artifacts do not include raw manifests, credentials, connector payloads, test transcripts, local filesystem paths, stack traces, or unauthorized tenant labels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace deterministic production skill lifecycle data with authorized live projections from durable package, version, tenant grant, discovery, installation, credential readiness, smoke-test, connector diagnostic, binding eligibility, quarantine, withdrawal, and audit records.
- **FR-002**: The system MUST return truthful empty, denied, or unavailable states when no live authorized records exist for a package, tenant, installation, readiness, diagnostic, eligibility, or audit panel.
- **FR-003**: The system MUST preserve role and tenant authorization for platform package publication, tenant discovery, tenant installation, credential configuration, diagnostics, eligibility, quarantine, withdrawal, and audit surfaces.
- **FR-004**: The system MUST expose package lists and package version details only from persisted package and version records, including lifecycle state, validation state, tenant availability, artifact reference summaries, quarantine state, withdrawal state, and audit references.
- **FR-005**: The system MUST expose package candidate workspace data only from persisted candidate or validation records, including safe manifest summaries and validation evidence.
- **FR-006**: The system MUST expose tenant grant, discovery, installation, and credential readiness views only from persisted tenant availability, installation, credential reference, readiness, smoke-test, and audit records.
- **FR-007**: The system MUST expose SkillExecutionGateway and governed connector diagnostics only as redaction-safe summaries, timestamps, policy outcomes, artifact references, and audit references.
- **FR-008**: The system MUST expose binding eligibility previews from authorized package, installation, credential, runtime policy, and connector readiness records, and MUST not fabricate passing eligibility evidence.
- **FR-009**: The system MUST keep raw manifests, credential values, provider authorization headers, raw connector payloads, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, and unauthorized tenant labels out of React contracts, redirects, exports, screenshots, QA artifacts, logs, and docs.
- **FR-010**: The system MUST provide durable safe lifecycle mutations for at least one user-visible action and return persisted result evidence, safe conflicts, denied states, or unavailable states as appropriate.
- **FR-011**: The system MUST validate at least one safe lifecycle mutation through Playwright and post-UI API or redaction-safe database verification before the spec is marked complete.
- **FR-012**: The system MUST update generated React TypeScript contracts so frontend code accepts live empty-state lifecycle envelopes and rejects malformed or unsafe lifecycle payloads.
- **FR-013**: The system MUST validate both Auth0-shaped backend route behavior and local-principal browser behavior for platform and tenant skill lifecycle surfaces.
- **FR-014**: The system MUST update live-data scanner guardrails so former Spec 032 deterministic skill package, installation, credential, diagnostic, and audit markers fail when found in production lifecycle builders or React routes while remaining allowed in test-only and historical spec artifacts.
- **FR-015**: The system MUST produce QA environment, QA guide, UI walkthrough, manual QA user guide, reviewer notes, Playwright evidence, post-UI persistence evidence, and curl regression evidence for qa052.

### Key Entities *(include if feature involves data)*

- **Skill Package**: Governed package identity with slug, display name, lifecycle state, latest version, publication state, withdrawal state, quarantine state, tenant availability, validation evidence, and audit references.
- **Skill Package Version**: Immutable package version with semantic version, manifest summary, artifact references, validation evidence, smoke-test evidence, lifecycle state, and publish or withdrawal metadata.
- **Package Candidate**: Pre-publication package candidate with safe manifest summary, validation status, artifact references, submitter, revision token, and publication eligibility.
- **Tenant Grant**: Tenant availability record that determines whether a package version is discoverable, installable, or bindable by a tenant.
- **Skill Installation**: Tenant-scoped installation with package version reference, lifecycle state, credential readiness, smoke-test history, connector readiness, binding eligibility, and audit references.
- **Credential Readiness**: Safe reference metadata, readiness state, latest check timestamp, remediation guidance, and policy reason for a tenant installation.
- **Smoke-Test Evidence**: Persisted safe result summary, execution mode, status, artifact references, audit references, and timestamps for package or installation checks.
- **Connector Diagnostic**: Governed connector or SkillExecutionGateway diagnostic result with policy outcome, safe summary, artifact references, and audit reference.
- **Binding Eligibility Decision**: Redaction-safe decision showing whether a skill can be bound in a workflow context based on package, installation, credential, connector, policy, and tenant scope state.
- **Lifecycle Audit Record**: Append-only safe event describing package, version, grant, installation, credential, smoke-test, diagnostic, quarantine, withdrawal, or eligibility changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an empty qa052 database, every skill lifecycle JSON route and browser panel returns a truthful empty, denied, or unavailable state with zero deterministic skill package, installation, diagnostic, credential, or audit rows.
- **SC-002**: In a seeded qa052 database, skill lifecycle JSON routes and browser panels return only persisted records authorized for the active platform or tenant scope.
- **SC-003**: A Playwright flow performs at least one user-visible skill lifecycle action and a post-UI API or QA database check proves the resulting state persisted.
- **SC-004**: Auth0-shaped backend tests and local-principal Playwright tests cover platform, tenant, and cross-tenant skill lifecycle access.
- **SC-005**: Redaction tests confirm raw manifests, credentials, connector payloads, test transcripts, local paths, stack traces, and unauthorized tenant labels are absent from React responses, screenshots, QA docs, and artifacts.
- **SC-006**: Generated TypeScript contract checks, focused backend tests, focused frontend tests, scanner tests, QA document validation, Spec QA, Playwright validation, and multi-agent curl validation all pass before the queue advances.

## Assumptions

- Existing skill registry, skill lifecycle, credential readiness, smoke-test, connector diagnostic, SkillExecutionGateway, audit, and authorization services remain the authoritative source for live skill lifecycle state.
- QA seed data may create real package, version, grant, installation, credential reference, smoke-test, diagnostic, eligibility, and audit records through documented setup flows, services, repositories, or safe scripts.
- Local QA smoke tests and connector diagnostics use mocked-safe or local allowlisted execution modes unless an explicit artifact approves a live probe path.
- Test fixtures with former qa032 markers may remain under test-only or historical spec paths but must not be imported by production routes or production projection builders.
- This spec does not remove historical specs, test fixtures, or docs solely because they contain old deterministic markers.
- The dirty worktree is intentionally preserved across specs, and no Git commit is required before or after this spec while the autopilot continues.
