# Feature Specification: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

**Feature Branch**: `codex/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Skill Registry and Tool Diagnostics Full React Parity and Jinja Removal. Spec 032 added the React skill lifecycle workspace, but full removal requires React parity for package create/list/detail, manifest candidate submission, validation findings, package version detail, tenant grants, quarantine/withdrawal, available versions, installation list/detail/configure, credential references, smoke-test history, readiness panels, binding eligibility, audit timeline, stale conflict recovery, and SkillExecutionGateway diagnostics. Old skill Jinja routes must be removed only after safe parity evidence."

## Clarifications

### Session 2026-05-06

- Q: If a package candidate includes both uploaded manifest content and pasted manifest content, which input wins? -> A: Uploaded manifest content takes precedence over pasted manifest content, with the selected source recorded in safe audit evidence. (autopilot)
- Q: Can raw manifest text be re-rendered after submission? -> A: No; after submission, browser responses and QA artifacts render only safe summaries, metadata, validation findings, fingerprints, revision tokens, and artifact references. (autopilot)
- Q: How should package version, tenant grant, installation configure, and diagnostics direct links behave after Jinja templates are deleted? -> A: Old routes redirect to React whenever safe while preserving package slugs, version ids, tenant ids, installation ids, conflict state, filters, and safe return intent. (autopilot)
- Q: How should smoke-test and connector diagnostic refresh actions behave? -> A: Refresh actions are explicit user actions, never background auto-refresh, and local/CI validation remains deterministic and mocked-safe. (autopilot)
- Q: How visible are quarantine and withdrawal states to tenant users? -> A: Tenant users see only authorized safe availability, readiness, and binding-eligibility summaries; platform-only state mutation controls remain hidden and denied. (autopilot)
- Q: How should process-local service limitations be represented? -> A: React shows safe readiness or unavailable states with remediation and rollback guidance, while backend policy remains authoritative. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Platform Skill Packages In React (Priority: P1)

Platform operators need every skill package and package-version browser workflow to be available in React before the package-management Jinja pages are removed, including package list, create, detail, manifest candidate submission, validation findings, publish readiness, version detail, tenant grants, quarantine, withdrawal, available versions, and stale conflict recovery.

**Why this priority**: Package publication and availability decisions govern which skills tenants can bind into workflows. These workflows must remain backend-owned, auditable, and safe before legacy package templates can disappear.

**Independent Test**: Exercise platform-admin package create/list/detail, candidate validation, publish, grant, quarantine/withdrawal, available-version, and direct-link flows through React contracts and old browser URLs; verify no skill package browser route renders Jinja.

**Acceptance Scenarios**:

1. **Given** a platform admin opens package list, package detail, candidate, version detail, grant, quarantine, withdrawal, or available-version legacy URLs, **When** the request is authenticated and safe to preserve, **Then** the system redirects to the equivalent React skill route with package, version, tenant, conflict, and filter intent intact.
2. **Given** a platform admin submits a manifest candidate from React or an old form route, **When** validation runs, **Then** the backend stores only safe manifest summaries and validation findings while React displays redacted readiness evidence.
3. **Given** a package version has stale revision or quarantine state, **When** the operator attempts publish, grant, withdraw, or quarantine actions, **Then** the backend blocks or applies the action with redaction-safe audit evidence and React shows the stale or status result without re-rendering raw manifests.

---

### User Story 2 - Manage Tenant Skill Installations In React (Priority: P2)

Tenant administrators need React parity for discovering available versions, creating installations, viewing installation detail, configuring credential references, reviewing readiness panels, running smoke tests, checking binding eligibility, and recovering from stale conflicts after installation mutations.

**Why this priority**: Tenant installation readiness determines whether workflows can safely bind skills. The React path must preserve tenant isolation, credential reference hygiene, and publish-gate evidence before installation templates are deleted.

**Independent Test**: Use tenant-admin local-principal and Auth0-shaped route tests to open installation list/detail/configure and submit credential, smoke-test, readiness, and binding-eligibility actions; verify tenant scope is enforced and old routes redirect or retire without Jinja.

**Acceptance Scenarios**:

1. **Given** a tenant admin opens the installation list or an installation detail URL, **When** the installation belongs to the active tenant, **Then** React shows the safe package/version summary, credential readiness, smoke history, binding eligibility, and audit timeline without raw credential values.
2. **Given** a tenant admin configures a credential reference, **When** the reference is saved or rejected, **Then** the backend owns validation, redaction, revision tokens, and audit records, and React renders only safe reference labels, fingerprints, and remediation.
3. **Given** a tenant admin requests another tenant's installation or a platform-only action, **When** the request is handled, **Then** the response denies access without exposing whether the package, installation, tenant, credential, or smoke-test artifact exists.

---

### User Story 3 - Diagnose SkillExecutionGateway Behavior In React (Priority: P3)

Operators and tenant admins need SkillExecutionGateway diagnostics in React, including connector readiness, policy checks, safe execution summaries, diagnostic refresh, explicit smoke-test refresh, and audit timeline evidence, while preserving mocked-safe validation and avoiding external side effects.

**Why this priority**: Diagnostics are the support path for skill execution readiness. They must be explicit, repeatable, redaction-safe, and governed before the diagnostics Jinja page is removed.

**Independent Test**: Run mocked diagnostic refresh and smoke-test actions through React and legacy direct links; verify backend-owned tool, outbound, credential, side-effect, and tenant policies are enforced and no raw tool payloads or secrets are rendered.

**Acceptance Scenarios**:

1. **Given** a reviewer opens skill diagnostics in React, **When** they refresh connector diagnostics, **Then** the backend performs only mocked or approved read-only checks and React displays normalized, redacted status evidence.
2. **Given** a smoke-test refresh is requested, **When** the backend evaluates readiness, **Then** React displays explicit action results, audit references, and artifact references without raw transcripts or tool payloads.
3. **Given** diagnostics are unavailable or blocked by policy, **When** the user opens the React route or old diagnostics URL, **Then** the system returns a safe React or non-Jinja problem state with rollback guidance and no unauthorized tenant labels.

### Edge Cases

- A package candidate is submitted with both uploaded manifest content and pasted manifest content.
- A manifest is invalid, oversized, stale, or includes raw secrets, private endpoint URLs, external payload examples, or credential material.
- A package slug, version id, installation id, tenant id, conflict token, saved filter, or query filter appears in a legacy direct link.
- A tenant-scoped principal attempts platform-only package creation, tenant grants, quarantine, withdrawal, or cross-tenant installation access.
- A credential reference is missing, stale, unauthorized, malformed, or points at a non-ready secret provider entry.
- A smoke-test or diagnostic refresh is retried, stale, or unavailable while process-local services are not warmed.
- A package version is quarantined or withdrawn while existing installations and workflow binding eligibility still need safe status summaries.
- React asset loading, bootstrap, or contract fetches fail during skill registry review.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide React routes and backend-owned contracts for skill package list, create, detail, candidate submission, validation findings, package version detail, tenant grant, quarantine, withdrawal, available versions, installation list, installation detail, installation configure, credential readiness, smoke-test history, binding eligibility, audit timeline, stale conflict recovery, and SkillExecutionGateway diagnostics.
- **FR-002**: The system MUST redirect old skill registry and skill diagnostics browser URLs to equivalent React routes when package, version, tenant, installation, conflict, filter, saved-filter, and return intent can be preserved safely.
- **FR-003**: Old skill browser routes that cannot safely redirect MUST return a non-Jinja safe problem or documented retirement response without revealing unauthorized resource existence.
- **FR-004**: Backend services MUST remain authoritative for authorization, tenant scope, manifest validation, credential-reference readiness, smoke-test execution, diagnostic refresh, quarantine and withdrawal state, tenant grants, revision tokens, stale conflict detection, redaction, audit capture, and side-effect policy decisions.
- **FR-005**: Manifest candidate handling MUST prefer uploaded content over pasted content when both are supplied, and MUST render only safe summaries, validation findings, fingerprints, package metadata, and audit references after submission.
- **FR-006**: React UI, route responses, logs, QA artifacts, exports, and screenshots MUST NOT expose raw manifests after submit, raw secrets, credential values, provider authorization headers, raw tool payloads, raw smoke-test transcripts, private channel messages, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-007**: Platform-admin-only workflows MUST include package creation, candidate validation and publication, tenant grants, quarantine, withdrawal, package version state changes, and platform-wide diagnostic visibility.
- **FR-008**: Tenant-admin workflows MUST include available version discovery, installation list/detail, credential reference configuration, explicit smoke-test refresh, readiness review, binding eligibility preview, and tenant-scoped diagnostics only for authorized tenant resources.
- **FR-009**: All diagnostic and smoke-test refresh actions MUST be explicit user actions and MUST use deterministic mocked-safe behavior in local and CI validation unless a spec explicitly approves a live probe path.
- **FR-010**: The implementation MUST retain JSON/API routes consumed by React while deleting or converting only browser-rendering Jinja routes and templates proven obsolete by Spec 042 parity evidence.
- **FR-011**: The migration dashboard or reviewer evidence MUST classify each Spec 042 skill registry and skill diagnostics template, component, static asset, and old browser route as deleted, redirected, converted to non-Jinja, retained with blocker, or outside active scope.
- **FR-012**: Auth0-shaped backend route tests and `AUTH_MODE=local_principal` Playwright flows MUST cover platform-admin, tenant-admin, unauthorized, stale conflict, denied, and direct-link behavior for changed skill routes.
- **FR-013**: QA artifacts MUST document deterministic setup, seed data, package and installation workflows, diagnostics, smoke-test refresh, stale conflict recovery, old route behavior, redaction checks, browser screenshots, and rollback guidance.
- **FR-014**: The system MUST NOT remove global Jinja dependencies, shared template infrastructure, or non-skill templates in Spec 042.

### Key Entities *(include if feature involves data)*

- **Skill Package**: A platform-owned package identity with slug, display summary, current lifecycle state, versions, candidate metadata, validation findings, tenant availability, and audit references.
- **Skill Package Version**: An immutable or lifecycle-governed version summary with manifest-derived safe metadata, readiness evidence, validation results, quarantine or withdrawal state, and tenant grants.
- **Manifest Candidate**: A proposed package manifest submitted through upload or paste, reduced after submit to safe summaries, fingerprints, validation findings, revision tokens, and audit evidence.
- **Tenant Skill Installation**: A tenant-scoped binding of an available package version with credential references, readiness state, smoke-test history, binding eligibility, stale conflict tokens, and audit timeline.
- **Skill Diagnostic Result**: A redacted backend-owned summary of SkillExecutionGateway connector readiness, policy decisions, credential status, smoke-test status, artifact references, and audit evidence.
- **Legacy Skill Route Mapping**: A reviewer-visible mapping from an old skill registry or diagnostics browser URL to a React destination, redirect behavior, non-Jinja problem response, or retained blocker.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Spec 042 skill registry and skill diagnostics inventory items are classified as deleted, redirected, converted to non-Jinja, retained with blocker, or outside active scope with evidence references.
- **SC-002**: 0 package, installation, credential configure, readiness, smoke-test, eligibility, audit timeline, available-version, or skill diagnostics browser routes in Spec 042 return TemplateResponse after implementation.
- **SC-003**: React workflows cover package creation, candidate submission, validation findings, version detail, tenant grants, quarantine/withdrawal, available versions, installation list/detail/configure, smoke-test history, readiness, binding eligibility, stale conflict recovery, and diagnostics.
- **SC-004**: Backend route tests prove platform-admin, tenant-admin, unauthorized, cross-tenant, stale conflict, and safe direct-link behavior for all changed skill routes.
- **SC-005**: Playwright validation proves local-principal users can reach and inspect the React skill registry and diagnostics surface with deterministic seed data and no real provider, connector, Telegram, Auth0, credential, or external tool calls.
- **SC-006**: Redaction sweeps over React responses, QA docs, screenshots, route outputs, diagnostic summaries, and reviewer notes find 0 raw secrets, raw credential values, raw manifests after submit, raw tool payloads, raw smoke-test transcripts, local filesystem paths, stack traces, or unauthorized tenant labels.
- **SC-007**: Reviewers can reproduce package, installation, diagnostics, direct-link redirect, stale conflict, and redaction evidence from QA docs within 15 minutes.

## Assumptions

- Spec 032 React skill lifecycle contracts and components are the baseline to extend or harden rather than replace wholesale.
- Existing skill registry services, SkillExecutionGateway policies, credential readiness helpers, smoke-test records, and audit records remain the source of truth.
- Manifest upload takes precedence over pasted manifest text when both are supplied, because it is easier to audit and avoids ambiguous dual-input behavior.
- Raw manifests may be accepted for validation, but after submit the browser and QA artifacts should show only safe summaries, metadata, findings, fingerprints, and artifact references.
- All smoke-test and connector diagnostic refresh actions are explicit user actions and are mocked-safe in local and CI validation.
- Old skill routes should redirect to React with ids and filters preserved whenever safe, and return non-Jinja problems when preservation or authorization is ambiguous.
- Process-local service limitations can be represented as safe readiness or unavailable states rather than bypassing backend policy.
