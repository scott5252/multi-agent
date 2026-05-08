# Feature Specification: Governance React Live Data

**Feature Branch**: `codex/051-governance-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Governance React Live Data. Replace deterministic governance builders with live data from model provider, credential-reference, prompt library, runtime profile, model-skill routing, policy history, gateway diagnostics, and run provenance services. The UI must show real provider connections, health snapshots, credential readiness, prompt lineages/drafts/versions/render tests, profile drafts/versions, routing history/previews, policy records, and run provenance. Empty states must be truthful when no providers, prompts, profiles, or runs exist."

## Clarifications

### Session 2026-05-07

- Q: How should prompt previews and render-test evidence appear in governance UI? -> A: Safe summaries only; raw prompt content, raw completions, protected variables, and test transcripts never render in React or QA evidence. (autopilot)
- Q: How fresh must provider health and credential readiness be? -> A: Show the latest persisted health/readiness snapshot with timestamps and unavailable/stale states when no current safe evidence exists. (autopilot)
- Q: Which provider probes are allowed during local QA? -> A: Use explicitly mocked or local allowlisted diagnostics only; production provider, credential, and outbound calls stay disabled unless an artifact explicitly approves a live probe. (autopilot)
- Q: How should routing previews and profile resolution be scoped? -> A: Resolve previews through existing authorized provider, prompt, profile, model-skill routing, and policy repositories for the active platform or tenant scope. (autopilot)
- Q: How should run provenance lookup behave when evidence is missing or denied? -> A: Return live safe provenance when authorized, denied states when unauthorized, and unavailable states when no redaction-safe evidence exists; never synthesize pass evidence. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Governance State (Priority: P1)

A platform administrator or tenant administrator opens the governance workspace and sees only authorized live governance records for the selected scope, including provider connections, credential readiness, prompt library state, runtime profiles, routing previews, policy history, gateway diagnostics, and run provenance.

**Why this priority**: This is the core product value: the governance workspace must stop presenting deterministic demo rows as if they were operational evidence.

**Independent Test**: Can be fully tested by opening the governance workspace in an empty live database and a seeded live database, then confirming the page shows truthful empty states or the exact records created through governed setup flows.

**Acceptance Scenarios**:

1. **Given** a fresh authorized tenant scope with no governance records, **When** the administrator opens the governance workspace, **Then** every panel shows an honest empty or unavailable state and no fixed provider, prompt, profile, route, policy, diagnostic, or provenance row.
2. **Given** an authorized tenant scope with live governance records, **When** the administrator opens the workspace, **Then** the records match the persisted provider, prompt, profile, routing, policy, diagnostic, and provenance state for that scope.
3. **Given** a principal without permission for another tenant's governance data, **When** they request the workspace or supporting JSON, **Then** they receive a denied state or authorization failure without unauthorized labels or details.

---

### User Story 2 - Verify Safe Governance Details (Priority: P2)

An administrator drills into provider readiness, credential references, prompt and profile revisions, route previews, policy history, and run provenance while seeing only redaction-safe summaries.

**Why this priority**: Governance details are security-sensitive and must prove live behavior without exposing secrets, raw prompts, raw completions, or private run payloads.

**Independent Test**: Can be tested by seeding governance records with credential references, prompt/profile versions, route previews, policy records, diagnostics, and provenance, then checking that detail panels show safe summaries and redact prohibited values.

**Acceptance Scenarios**:

1. **Given** provider and credential records with readiness outcomes, **When** the administrator views provider diagnostics, **Then** the UI shows live health and readiness evidence without credential values or authorization headers.
2. **Given** prompt and profile records with drafts, versions, render tests, and activation history, **When** the administrator views governance details, **Then** the UI shows revision metadata and safe previews without raw protected content.
3. **Given** run provenance evidence linked to governance configuration, **When** the administrator opens provenance, **Then** the UI shows safe identifiers, policy/config references, and redaction notices without raw run payloads.

---

### User Story 3 - Exercise Durable Governance Actions (Priority: P3)

An authorized administrator performs a safe governance action that writes through the backend-owned governance services, then sees the updated live state reflected in the workspace.

**Why this priority**: The browser must not fake mutation success; at least one safe action must prove the route can write and then re-read durable governance state.

**Independent Test**: Can be tested by creating or updating a safe governance record through the UI, then verifying the same state through the backing API or redaction-safe database evidence.

**Acceptance Scenarios**:

1. **Given** an authorized administrator and a safe governance setup action, **When** they submit the action, **Then** the backend persists the result and returns a success state with a live record identifier.
2. **Given** the action has completed, **When** the administrator refreshes the workspace or opens the related detail, **Then** the updated state is read back from durable governance records rather than a browser default.
3. **Given** an invalid, stale, or unauthorized action, **When** the administrator submits it, **Then** the UI shows the backend-owned error state without inventing success evidence.

---

### Edge Cases

- Empty governance scopes must not display fixed provider, prompt, profile, routing, policy, diagnostic, or provenance rows.
- Tenant-scoped principals must not see platform-only provider, credential, policy, or provenance details unless explicitly authorized.
- Platform administrators viewing tenant-specific records must see the selected scope clearly and must not leak unrelated tenant labels.
- Missing provider health, credential readiness, prompt tests, route previews, or run provenance must render as unavailable or not yet evaluated, not as synthetic passing evidence.
- Stale revision tokens, withdrawn providers, retired prompt/profile versions, inactive routes, failed diagnostics, and denied policy actions must preserve their real state.
- QA evidence, screenshots, exports, logs, and docs must not include raw secrets, credential values, provider authorization headers, raw prompts, raw completions, private run payloads, local filesystem paths, or stack traces.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The governance workspace MUST project provider connections, provider health snapshots, and provider diagnostics from authorized live records or show an honest empty/unavailable state.
- **FR-002**: The workspace MUST project credential-reference readiness and credential diagnostics from safe metadata only, never from raw credential values or provider authorization headers.
- **FR-003**: The workspace MUST project prompt lineages, drafts, versions, render tests, grants, and preview metadata from live prompt library state or show truthful empty/unavailable states.
- **FR-004**: The workspace MUST project runtime profile drafts, versions, activation state, grants, and validation results from live runtime profile state or show truthful empty/unavailable states.
- **FR-005**: The workspace MUST project model routing history, model-skill routing previews, tool/outbound/credential policies, policy records, and rollback history from live governance configuration state.
- **FR-006**: The workspace MUST project gateway diagnostics and run provenance from live gateway, configuration, and run evidence using safe summaries and redaction notices.
- **FR-007**: Every governance JSON response MUST include enough provenance or empty-state metadata for reviewers to distinguish live repository data, computed system metadata, denied state, unavailable state, and empty state.
- **FR-008**: Production governance routes MUST NOT return deterministic provider rows, prompt rows, profile rows, route previews, policy records, diagnostic records, run provenance, fake IDs, fake audit references, fake artifact references, or fake mutation success.
- **FR-009**: Governance UI actions that are available in production MUST use backend-owned action metadata and persist through the existing governed services; browser-only default IDs or fake success responses are prohibited.
- **FR-010**: The feature MUST validate authorized platform, authorized tenant, unauthorized tenant, empty live database, and seeded live database behavior for the governance routes.
- **FR-011**: Generated browser contracts MUST remain backend-owned and must expose nullable or empty governance states without requiring frontend fixture data.
- **FR-012**: QA guides and validation evidence MUST document how live governance seed data is created and how post-UI persistence is verified.

### Key Entities *(include if feature involves data)*

- **Provider Connection**: An authorized model provider configuration with display metadata, status, health, diagnostics, and safe credential-reference readiness.
- **Credential Reference**: A safe reference to a secret or credential dependency, represented only by readiness, fingerprints, labels, or policy-safe metadata.
- **Prompt Lineage And Version**: Prompt authoring records, drafts, immutable versions, grants, render tests, and preview summaries.
- **Runtime Profile And Version**: Agent runtime profile authoring records, validation state, active versions, grants, and rollback history.
- **Routing And Policy Record**: Model routing versions, model-skill route previews, tool/outbound/credential policies, and policy history.
- **Gateway Diagnostic**: Provider probe, gateway attempt, health, and failure metadata that is safe to render.
- **Run Provenance Evidence**: Redaction-safe references showing which provider, prompt, profile, route, policy, and gateway evidence shaped a run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an empty live governance database, all governance workspace panels render empty or unavailable states with zero deterministic provider, prompt, profile, routing, policy, diagnostic, or provenance rows.
- **SC-002**: In a seeded live governance database, every rendered governance row can be matched to a persisted or computed authorized source through API or database evidence.
- **SC-003**: Unauthorized tenant access attempts fail closed or render denied states without unauthorized tenant labels, raw details, or synthetic data.
- **SC-004**: At least one safe governance UI action writes durable state and is verified after Playwright through a backend API or redaction-safe QA database query.
- **SC-005**: Automated validation passes QA document checks, backend quality gates, generated contract checks, frontend checks, Playwright UI validation, post-UI persistence verification, and the multi-agent curl test before the next spec starts.
- **SC-006**: Scanner and test coverage identify the former deterministic governance sources as remediated and block new production governance fixture data.

## Assumptions

- Existing authorization, tenant scoping, provider, prompt, runtime profile, routing, policy, gateway, and provenance services remain the authoritative sources for governance state.
- QA seed data may be created through documented setup flows, domain services, repositories, migrations intended for QA, or public/admin APIs, but production route handlers cannot depend on test fixture modules.
- Empty or unavailable states are acceptable user-visible outcomes when live governance records do not exist or when diagnostics have not been evaluated.
- Existing redaction, safe-summary, fingerprinting, and audit helpers are reused for any security-sensitive governance evidence.
- The feature scope is limited to the governance React admin production surface and its supporting JSON contracts; unrelated domains remain for later specs.
