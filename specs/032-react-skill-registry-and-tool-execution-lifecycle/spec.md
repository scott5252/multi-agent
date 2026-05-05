# Feature Specification: React Skill Registry And Tool Execution Lifecycle

**Feature Branch**: `codex/032-react-skill-registry-and-tool-execution-lifecycle`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for a React Skill Registry and Tool Execution Lifecycle. Platform admins must be able to publish skill packages through a guided browser flow, and tenant admins must be able to discover, install, configure, test, preview binding eligibility, and inspect governed tool readiness for granted skills. The UI must cover package creation, manifest paste/upload, candidate validation, immutable publication, tenant grants, tenant discovery, tenant installation, credential reference configuration, smoke-test/readiness evidence, SkillExecutionGateway diagnostics, first-party calendar/Gmail/news/weather/commute connector readiness, mock or approved staging probe evidence, binding eligibility preview, stale conflict recovery, quarantine/withdrawal states, audit timeline, and redaction-safe evidence."

## Clarifications

### Session 2026-05-05

- Q: How should publication and installation flows be organized for non-technical administrators? A: Use guided wizards for platform publication and tenant installation, with backend-owned step metadata, readiness state, and authorized actions. (autopilot)
- Q: How should manifest paste and upload behave when both are present? A: Upload takes precedence over paste, and submitted raw manifest text is never echoed back after validation. (autopilot)
- Q: What gates immutable package publication? A: Publication requires package validation, required smoke-test evidence, tenant grant review, current revision token, and audit persistence. (autopilot)
- Q: How should credential reference configuration work? A: Credential references are selected only from backend-authorized options for the active tenant or platform scope. (autopilot)
- Q: How should smoke-test and connector diagnostic refresh work? A: Smoke tests and connector diagnostics are explicit queued actions with safe last-known status, not unbounded background polling. (autopilot)
- Q: How should binding eligibility context be selected? A: Binding previews use backend-owned workflow, profile, package, and tenant context choices and remain read-only. (autopilot)
- Q: How should stale revision conflicts be presented? A: Stale conflicts provide reload-latest and retry guidance without applying partial browser-side state. (autopilot)
- Q: How much manifest or tool output detail should be shown? A: React renders safe summaries, digests, findings, and evidence references only; raw manifests and tool outputs remain outside browser contracts. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish Skill Packages Safely (Priority: P1)

Platform administrators can create skill package candidates, submit manifests through a guided browser flow, validate package metadata, review tenant grant impact, publish immutable package versions, and see quarantine or withdrawal state without exposing raw package payloads, credential values, connector outputs, or unsafe smoke-test details.

**Why this priority**: Tenant installation and tool readiness depend on safe, platform-governed package publication. A package must be validated, auditable, and immutable before tenants can discover or install it.

**Independent Test**: Sign in as a platform administrator, open the React skill lifecycle route, submit a deterministic manifest fixture, review validation findings, publish an immutable package version, verify tenant grants and audit references, and confirm unsafe manifest text is summarized rather than echoed.

**Acceptance Scenarios**:

1. **Given** a platform administrator and a new package candidate, **When** they submit a manifest fixture, **Then** the page shows safe package metadata, validation readiness, tenant grant options, revision state, and candidate actions without showing raw manifest text after submit.
2. **Given** a candidate has validation errors, **When** the administrator reviews readiness, **Then** the page shows safe field-level findings, remediation guidance, and blocks immutable publication until required validation evidence is ready.
3. **Given** a candidate is valid, **When** the administrator publishes it, **Then** the system returns an immutable package version summary, audit reference, tenant grant summary, and publish evidence that can be reviewed without raw connector output.
4. **Given** a package is quarantined, withdrawn, or superseded, **When** the administrator opens its history, **Then** the page shows safe lifecycle state, actor summaries, affected tenant grants, and recovery guidance without leaking tenant-private configuration.

---

### User Story 2 - Install And Configure Granted Skills (Priority: P2)

Tenant administrators can discover granted skill packages, compare readiness summaries, install or upgrade package versions, configure credential references from authorized choices, run explicit readiness and smoke-test actions, and understand connector health for first-party calendar, Gmail, news, weather, and commute tools.

**Why this priority**: Tenant administrators need an understandable lifecycle for using approved skills without learning package internals or touching raw credentials.

**Independent Test**: Sign in as an Acme tenant administrator, discover a granted Daily Briefing package, install it, select deterministic credential references, run explicit mocked readiness checks, and verify first-party connector readiness summaries and audit evidence are tenant-scoped and redacted.

**Acceptance Scenarios**:

1. **Given** a tenant administrator has package grants, **When** they open skill discovery, **Then** they see only granted packages, safe version metadata, install readiness, credential requirements, smoke-test readiness, and authorized actions for the active tenant.
2. **Given** a tenant administrator installs or upgrades a package, **When** they submit the action, **Then** the system returns safe mutation feedback, revision tokens, audit references, and stale conflict recovery options.
3. **Given** credential references are required, **When** the administrator configures credentials, **Then** only authorized references are selectable and the page never renders resolved values, authorization headers, provider tokens, private messages, or connector payloads.
4. **Given** readiness or smoke-test checks run, **When** results are displayed, **Then** calendar, Gmail, news, weather, and commute connector readiness is summarized with safe diagnostics, mock or approved staging evidence, and no external side effects in local or CI validation.

---

### User Story 3 - Preview Binding Eligibility And Tool Execution Readiness (Priority: P3)

Administrators can preview whether installed skills are eligible for workflow or agent runtime bindings, inspect governed tool execution diagnostics, understand policy decisions from the SkillExecutionGateway, and review audit timeline evidence for package, installation, credential, smoke-test, and execution readiness changes.

**Why this priority**: Binding decisions and tool execution readiness must be explainable before workflows can safely depend on installed skills.

**Independent Test**: Run a deterministic binding eligibility preview for a granted package, inspect SkillExecutionGateway diagnostics, filter lifecycle audit timeline entries, and verify every result is tenant-scoped, redacted, bounded, and consistent with governed read-only connector execution.

**Acceptance Scenarios**:

1. **Given** an installed skill package, **When** an administrator previews binding eligibility for a workflow context, **Then** the page shows policy reasons, missing requirements, eligible tool bindings, and remediation steps without invoking external tools.
2. **Given** governed tool execution diagnostics exist, **When** an administrator opens diagnostics, **Then** the page shows SkillExecutionGateway policy decisions, connector readiness, side-effect posture, credential readiness, and safe attempt summaries.
3. **Given** lifecycle history exists, **When** an administrator filters by package, tenant, actor, action, status, or time window, **Then** the page shows bounded audit timeline results with safe diff summaries and authorized cross-links.
4. **Given** cross-tenant, unauthorized package, unauthorized credential, or unapproved staging-probe access is attempted, **When** the backend cannot prove authorization, tenant scope, or audit persistence, **Then** it fails closed with a safe problem response and no lifecycle details.

### Edge Cases

- A submitted manifest is malformed, too large, unsupported, missing required fields, or names tools that violate tenant or side-effect policy.
- Paste and upload are both attempted for a package candidate in the same editing session.
- A package candidate validates successfully but required smoke-test evidence is stale or unavailable.
- A published package version is superseded, quarantined, withdrawn, or unavailable after tenants have installed it.
- A tenant administrator attempts to discover, install, upgrade, or configure a package without an active grant.
- A tenant administrator attempts to use credential references from another tenant or an unauthorized credential source.
- A smoke test, connector diagnostic, or staging probe fails, times out, is breaker-blocked, or would require an unapproved external call.
- A stale revision token is submitted during package publication, tenant installation, credential configuration, or readiness refresh.
- Binding eligibility preview requests live tool execution, credential resolution, Telegram delivery, model calls, or side-effectful connector actions in local or CI validation.
- Audit persistence fails or redaction cannot prove that manifests, connector outputs, private messages, credential values, stack traces, local paths, and tenant labels are safe.
- JavaScript is unavailable; existing Jinja skill registry and skill execution diagnostic routes remain available during migration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a protected additive React skill lifecycle route while preserving existing Jinja skill registry, installation, and tool execution diagnostic routes as fallbacks until migration hardening retires them.
- **FR-002**: System MUST expose backend-owned JSON contracts for package publication, candidate validation, tenant grants, package discovery, installation, upgrade, credential reference configuration, smoke-test readiness, connector diagnostics, binding eligibility preview, lifecycle audit timeline, safe mutation results, and denied states.
- **FR-003**: System MUST generate TypeScript contracts from backend schemas and React MUST consume generated contracts rather than hand-maintained browser models for protected skill lifecycle data.
- **FR-004**: System MUST support local-principal and Auth0-shaped principal validation for React skill lifecycle routes and protected actions.
- **FR-005**: System MUST fail closed when authorization, tenant scope, package grant, credential policy, side-effect policy, connector policy, staging-probe approval, or audit persistence cannot be proven.
- **FR-006**: System MUST provide guided platform-admin publication and tenant installation flows with backend-owned step metadata, readiness state, authorized actions, package candidate creation, manifest submission, validation review, immutable publication, tenant grant review, quarantine, withdrawal, and revision conflict recovery.
- **FR-007**: System MUST restrict package creation, publication, tenant grant mutation, quarantine, withdrawal, staging-probe approval, and package-level lifecycle changes to platform administrators.
- **FR-008**: System MUST allow tenant administrators to discover, install, configure, test, upgrade, and inspect only packages granted to their active tenant scope.
- **FR-009**: System MUST accept deterministic manifest paste and upload workflows, MUST make upload take precedence when both are submitted, and MUST ensure raw manifest text is not echoed back after submit and unsafe manifest fields are summarized before rendering.
- **FR-010**: System MUST display candidate validation findings, required smoke-test evidence, package version status, tenant grant status, current revision token readiness, audit persistence readiness, and publish readiness through safe summaries and explicit blocking states.
- **FR-011**: System MUST provide tenant installation and upgrade actions with idempotency keys, revision tokens, stale conflict recovery guidance, audit references, and safe confirmation states.
- **FR-012**: System MUST provide credential reference configuration from authorized choices only and MUST never render resolved credential values, provider tokens, authorization headers, secret provider payloads, or private connector payloads.
- **FR-013**: System MUST provide explicit queued readiness, smoke-test, connector diagnostic, and approved staging-probe refresh actions with safe last-known status and MUST avoid unbounded background polling.
- **FR-014**: System MUST render first-party calendar, Gmail, news, weather, and commute connector readiness with safe policy decisions, credential readiness, mock or approved staging evidence, and remediation guidance.
- **FR-015**: System MUST make local and CI validation use deterministic mocks or fixtures for smoke tests, connector diagnostics, staging probes, and SkillExecutionGateway evidence unless a spec explicitly marks an approved live probe path.
- **FR-016**: System MUST provide binding eligibility previews from backend-owned workflow, profile, package, and tenant context choices that evaluate context without invoking live tools, live credentials, Telegram, model providers, or side-effectful connector actions.
- **FR-017**: System MUST provide SkillExecutionGateway diagnostics that show governed tool policy decisions, side-effect posture, credential readiness, outbound policy status, and safe attempt summaries.
- **FR-018**: System MUST provide lifecycle audit timeline views with bounded filters, safe diff categories, actor summaries, tenant scope, package/version references, installation references, smoke-test evidence, and authorized cross-links.
- **FR-019**: System MUST show loading, empty, denied, partial, stale, conflict, reload-latest, retry, validation-blocked, credential-unavailable, smoke-test-failed, connector-degraded, quarantine, withdrawal, audit-unavailable, and mutation confirmation states.
- **FR-020**: System MUST redact raw secrets, resolved credential values, authorization headers, provider tokens, raw manifests, private channel messages, memory contents, connector request/response payloads, raw tool outputs, stack traces, local paths, and unauthorized tenant labels before rendering, logging, exporting, or storing QA artifacts.
- **FR-021**: System MUST cross-link to existing workflow builder, governance, operations, usage, audit/debugging, skill registry, tool execution diagnostics, and test-bench destinations only when URLs are authorized for the active principal.
- **FR-022**: System MUST produce QA documents, Playwright screenshots, backend tests, frontend tests, generated contract checks, and full Spec QA evidence before advancing to the next spec.

### Key Entities *(include if feature involves data)*

- **SkillLifecycleDashboard**: Authorized route envelope, active scope, lifecycle sections, feature flags, status summaries, safe callouts, and authorized actions.
- **SkillPackageCandidate**: Draft package candidate with safe manifest summary, validation state, package metadata, revision token, publish readiness, and candidate actions.
- **SkillPackageVersionSummary**: Immutable package version with package identity, version label, lifecycle state, manifest digest, tenant grant summary, validation evidence, smoke-test evidence, quarantine or withdrawal state, and audit references.
- **TenantSkillGrantSummary**: Tenant-scoped package availability with grant status, allowed versions, install eligibility, restrictions, and authorized tenant actions.
- **TenantSkillInstallationSummary**: Tenant installation record with installed version, upgrade path, credential readiness, smoke-test readiness, binding readiness, revision token, and audit references.
- **CredentialReferenceOption**: Authorized safe credential reference metadata, readiness status, fingerprint, policy reason, and remediation hint without resolved values.
- **ConnectorReadinessSummary**: Calendar, Gmail, news, weather, or commute connector readiness with policy state, credential state, smoke-test state, staging evidence, and safe remediation.
- **SkillExecutionDiagnosticSummary**: SkillExecutionGateway diagnostic summary with governed tool, side-effect posture, outbound policy, credential policy, attempt evidence, and safe redaction summary.
- **BindingEligibilityPreview**: Read-only eligibility evaluation for workflow/profile context with eligible tools, blocked tools, policy reasons, missing requirements, and remediation guidance.
- **SkillLifecycleAuditRecord**: Bounded history item with package, version, tenant scope, actor summary, timestamp, lifecycle action, outcome, safe diff summary, and audit reference.
- **SkillLifecycleMutationResult**: Publication, grant, install, upgrade, credential, smoke-test, diagnostic, preview, quarantine, withdrawal, and recovery action response with status, toast, revision token, warnings, audit reference, and safe redirect links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A platform administrator can submit a deterministic package manifest fixture, review validation evidence, publish an immutable package version, and see tenant grant impact without raw manifest or connector payload exposure.
- **SC-002**: A tenant administrator can discover only granted packages, install a deterministic package, configure authorized credential references, and run explicit mocked readiness checks without seeing resolved credential values.
- **SC-003**: A tenant administrator can review first-party calendar, Gmail, news, weather, and commute connector readiness with safe diagnostics, evidence references, and remediation guidance.
- **SC-004**: An administrator can run binding eligibility preview and SkillExecutionGateway diagnostic review without live tool execution, live credentials, Telegram delivery, model provider calls, or side-effectful connector actions.
- **SC-005**: Platform and tenant users can understand quarantine, withdrawal, stale conflict, smoke-test failure, connector degradation, credential unavailable, and validation-blocked states through actionable safe summaries.
- **SC-006**: Local-principal and Auth0-shaped route tests cover authorized, denied, platform-only mutation, tenant-scoped discovery/install/configuration, and cross-tenant behavior.
- **SC-007**: Playwright validation captures denied, platform publication, tenant discovery/install, credential configuration, smoke-test/readiness, binding preview, gateway diagnostics, and audit/quarantine evidence without unsafe text.
- **SC-008**: Full Spec QA passes with Ruff, format, mypy, coverage at or above 90 percent, generated TypeScript drift checks, frontend typecheck/tests/build, QA docs, and Playwright validation.

## Assumptions

- Existing skill registry services, package lifecycle models, tenant availability, installation state, credential readiness, validation evidence, smoke-test evidence, quarantine decisions, upgrade lineage, binding eligibility projections, revision tokens, SkillExecutionGateway diagnostics, audit helpers, and redaction helpers remain authoritative.
- The React skill lifecycle experience is additive; existing Jinja/admin API skill registry and skill execution diagnostic routes remain available during migration.
- Local QA uses deterministic mocks and fixtures and does not require real Auth0, Telegram, provider, credential, Gmail, calendar, news, weather, commute, or connector calls.
- Manifest and tool diagnostic screens prioritize safe summaries, evidence references, and authorized links over raw JSON, raw manifests, raw connector outputs, or implementation-specific payloads.
