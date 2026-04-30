# Feature Specification: Skill Registry And Installation Lifecycle

**Feature Branch**: `014-skill-registry-lifecycle`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "Add a skill registry and installation lifecycle for agent skills. Platform admins must be able to create platform-approved skill packages, publish immutable skill package versions, and make them available to tenants. Tenant admins must be able to install authorized skill versions into their tenant, run declared smoke tests, configure required secret references or delegated credential requirements, and bind installed skills to agent profiles or workflow roles through existing skill-binding policies. Skill manifests must declare slug, semantic version, description, entrypoint type, tool declarations, action categories, network requirements, credential requirements, runtime permissions, test fixtures, compatibility metadata, and safe documentation. Installed skill versions must be immutable; upgrades require a new installation version and explicit rebinding or workflow publish. Raw package secrets and credential values must never be stored. Require sandboxed validation, tenant isolation, audit records, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## Clarifications

### Session 2026-04-29

- Q: What artifact/provenance should a published skill package version lock for future validation and tenant installation? → A: Internal artifact storage with pinned content, manifest, and documentation digests.
- Q: What should happen when a published package version or tenant installation is later found unsafe? → A: Quarantine affected package versions and installations, blocking new installs, new bindings, and runtime use until resolved.
- Q: What runtime entrypoint surface should v1 skill packages support? → A: Declarative package manifests, docs, fixtures, and references to existing approved tool/MCP integrations only.
- Q: How should concurrent tenant installation readiness, credential configuration, and binding changes be handled? → A: Optimistic concurrency tokens; stale writes are rejected, make no state change, and are audited.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish Approved Skill Versions (Priority: P1)

A platform admin can create a platform-approved skill package, validate its manifest and safe documentation, run required validation in an isolated environment, and publish an immutable package version that can be made available to selected tenants.

**Why this priority**: The registry must establish trusted, versioned skill packages before tenants can install or bind them safely.

**Independent Test**: A platform admin can submit a skill package with a complete manifest, safe documentation, declared fixtures, and declared permissions; validation accepts the package; publication creates an immutable version; and only authorized tenants can see it as available.

**Acceptance Scenarios**:

1. **Given** a platform admin with package publishing rights, **When** they submit a skill package with a valid manifest and safe documentation, **Then** the package is recorded as a platform-approved package candidate with validation status visible to the admin.
2. **Given** a package candidate with a complete manifest, declared tests, and valid compatibility metadata, **When** the platform admin runs validation, **Then** validation runs in isolation and reports pass, warning, or blocking findings without exposing package secrets or credential values.
3. **Given** a validated package candidate, **When** the platform admin publishes semantic version `X.Y.Z`, **Then** an immutable package version is created and later edits require publishing a new version.
4. **Given** a published package version, **When** the platform admin grants tenant availability, **Then** only the selected tenants can discover and request installation of that version.

---

### User Story 2 - Install And Validate Tenant Skills (Priority: P2)

A tenant admin can discover authorized skill package versions, install a selected immutable version into their tenant, configure required secret references or delegated credential requirements, and run the package-declared smoke tests before the skill is marked ready for binding.

**Why this priority**: Tenant admins need a controlled path from authorized package availability to a tenant-ready installation with proof that required credentials and smoke tests are satisfied.

**Independent Test**: A tenant admin installs an authorized package version, supplies only secret references or delegated credential approvals, runs declared smoke tests against safe fixtures, and sees the installation move to ready only when all required checks pass.

**Acceptance Scenarios**:

1. **Given** a tenant admin and an available package version, **When** they start installation, **Then** the installation captures the exact package version, tenant scope, manifest summary, required credential status, declared network requirements, runtime permissions, and initial readiness state.
2. **Given** a package manifest that requires credentials, **When** the tenant admin configures the installation, **Then** they can provide approved secret references or delegated credential requirements without entering or storing raw secret values.
3. **Given** an installed skill version with declared smoke tests, **When** the tenant admin runs smoke tests, **Then** tests execute in tenant isolation using declared safe fixtures and the installation records pass, fail, skipped, and last-run evidence.
4. **Given** an installation with missing credentials, failed smoke tests, or incompatible metadata, **When** the tenant admin attempts to mark it ready, **Then** readiness is blocked with actionable findings.

---

### User Story 3 - Bind Installed Skills To Runtime Use (Priority: P3)

A tenant or platform admin can bind a ready installed skill version to agent profiles or workflow roles through existing skill-binding policies, while upgrades require a new installation version and explicit rebinding or workflow publication.

**Why this priority**: Skills only become useful when they are connected to governed runtime roles, and immutable versioning must prevent accidental behavior changes.

**Independent Test**: An admin binds a ready tenant installation to an eligible agent profile and workflow role; a newer package version is installed separately; existing bindings remain on the original installation until the admin explicitly rebinds or publishes an updated workflow.

**Acceptance Scenarios**:

1. **Given** a ready tenant skill installation, **When** an authorized admin creates a binding, **Then** existing skill-binding policies determine whether the installation can be bound to the selected agent profile or workflow role.
2. **Given** an installed skill version that is not ready, unauthorized, or policy-incompatible, **When** an admin attempts to bind it, **Then** the binding is refused and the reason is recorded.
3. **Given** an installed skill version is already bound to a profile or workflow role, **When** a newer package version becomes available, **Then** existing bindings continue to reference the original immutable installation version.
4. **Given** an admin installs an upgraded skill version, **When** they want runtime use to move to that version, **Then** they must explicitly create a new binding, update the profile, or publish a workflow that references the new installation version.

---

### User Story 4 - Review Lifecycle Evidence And Audit Trail (Priority: P4)

Platform and tenant admins can review package history, installation history, smoke test evidence, credential readiness, bindings, upgrade lineage, and audit records without exposing raw secrets, unsafe package contents, or cross-tenant data.

**Why this priority**: Skill governance requires traceability across platform approval, tenant installation, readiness, binding, and upgrades.

**Independent Test**: After creating a package, publishing a version, granting tenant access, installing it, running smoke tests, binding it, and installing an upgrade, authorized admins can review safe history and audit records for each lifecycle event while unauthorized users and other tenants cannot see restricted data.

**Acceptance Scenarios**:

1. **Given** a platform admin, **When** they inspect a skill package lineage, **Then** they can see package versions, manifest summaries, validation outcomes, tenant availability grants, publication events, and safe documentation status.
2. **Given** a tenant admin, **When** they inspect an installed skill, **Then** they can see package version, installation version, readiness state, credential-reference status, smoke test evidence, bindings, upgrade lineage, and safe audit summaries for their tenant only.
3. **Given** an unauthorized user or an admin outside the tenant scope, **When** they attempt to view package availability, installation, smoke test, binding, or audit details, **Then** access is denied and the attempt is recorded.
4. **Given** any lifecycle record that references credentials or package-provided test data, **When** it is displayed or exported, **Then** raw secret values, raw credential values, and unsafe package content are omitted or redacted.

### Edge Cases

- A platform admin attempts to publish a package version with a semantic version that already exists for the same package slug.
- A manifest omits required fields, declares malformed semantic versions, includes unsafe documentation, or requests permissions that policy does not allow.
- A manifest declares arbitrary executable package code, a standalone external HTTP service entrypoint, or an unapproved tool/MCP integration reference.
- Validation, package inspection, or smoke tests attempt network access that was not declared or approved.
- A package declares credential requirements but the tenant provides missing, revoked, unauthorized, or wrong-scope secret references.
- A tenant attempts to install a package version that is not available to that tenant, has been withdrawn from new installs, or is incompatible with tenant policy.
- Smoke tests pass for one tenant but fail for another because of tenant-specific credential readiness, policy, or fixture configuration.
- An installed version is bound to a profile or workflow role and later the platform withdraws availability for new installations.
- A package version, package artifact, documentation, fixture, or tenant installation is later found unsafe and must be quarantined without deleting immutable history.
- A package version has a newer compatible version available, but existing bindings remain pinned to the older installed version until explicit rebinding or workflow publication occurs.
- Two admins attempt to change the same tenant installation readiness, credential configuration, or binding at the same time, and stale writes must be rejected without state changes.
- Audit records or lifecycle views must remain useful when package-provided documentation or fixtures are later found unsafe and restricted from display.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The registry MUST allow platform admins to create skill package records with a stable slug, description, approval status, owner, lifecycle state, and safe documentation summary.
- **FR-002**: The registry MUST require each skill package version manifest to declare slug, semantic version, description, entrypoint type, tool declarations, action categories, network requirements, credential requirements, runtime permissions, test fixtures, compatibility metadata, and safe documentation.
- **FR-002a**: For this feature version, skill package manifests MUST be declarative and may only reference existing approved tool/MCP integrations as runtime entrypoints; arbitrary executable package code and standalone external HTTP service entrypoints are out of scope and MUST be rejected during validation.
- **FR-003**: The registry MUST reject package candidates whose manifest is incomplete, internally inconsistent, duplicates an existing package version, or requests disallowed capabilities.
- **FR-004**: Package validation MUST inspect manifests, documentation, test fixtures, requested network access, requested runtime permissions, credential requirements, compatibility metadata, and declared tool behavior before publication.
- **FR-005**: Package validation and smoke testing MUST run in an isolated environment that prevents undeclared network access, cross-tenant data access, raw credential exposure, and persistent side effects outside the declared validation scope.
- **FR-006**: Platform admins MUST be able to publish a validated skill package as an immutable package version identified by package slug and semantic version.
- **FR-007**: Published package versions MUST remain immutable; any change to manifest content, documentation, fixtures, compatibility metadata, entrypoint behavior, permissions, or declarations MUST require a new package version.
- **FR-007a**: Each published package version MUST store the approved package artifact in controlled internal artifact storage and pin content, manifest, and documentation digests as immutable provenance for validation, installation, audit, and future readiness checks.
- **FR-008**: Platform admins MUST be able to make selected published package versions available to selected tenants, all tenants, or no additional tenants while preserving historical availability evidence.
- **FR-009**: Tenant admins MUST be able to discover only package versions they are authorized to install for their tenant.
- **FR-010**: Tenant admins MUST be able to install an authorized package version into their tenant as an immutable tenant installation version.
- **FR-011**: Installed skill versions MUST record the exact package slug, package semantic version, tenant scope, installation version, manifest summary, readiness state, compatibility status, smoke test status, credential-reference status, and binding eligibility.
- **FR-012**: Tenant installations MUST NOT store raw package secrets, raw credential values, or package-provided unsafe secret material.
- **FR-013**: Tenant admins MUST be able to satisfy package credential requirements using approved secret references or delegated credential requirements, with readiness shown per requirement.
- **FR-014**: The lifecycle MUST detect and block use of missing, revoked, unauthorized, wrong-scope, or incompatible secret references and delegated credential requirements.
- **FR-015**: Tenant admins MUST be able to run package-declared smoke tests for an installed skill version using declared safe fixtures and tenant-scoped configuration.
- **FR-016**: Smoke test results MUST record installation version, package version, tenant scope, fixture identity, credential-readiness summary, outcome, failure reasons, and last-run time without storing raw secret or credential values.
- **FR-017**: An installed skill version MUST be marked ready for binding only when required credential readiness, compatibility checks, permissions checks, and required smoke tests satisfy policy.
- **FR-018**: Tenant admins and platform admins MUST be able to view actionable readiness findings for installations that are blocked by validation, credentials, permissions, compatibility, smoke tests, or tenant authorization.
- **FR-019**: Existing skill-binding policies MUST determine whether a ready installed skill version can be bound to an agent profile or workflow role.
- **FR-020**: Binding attempts MUST be refused when the installed skill version is not ready, is unauthorized for the tenant, violates policy, has incompatible action categories, lacks required credential readiness, or does not satisfy profile or workflow role constraints.
- **FR-021**: Successful bindings MUST record the exact installed skill version and MUST NOT automatically move to newer package or installation versions.
- **FR-022**: Upgrades MUST require installing a new package version as a new tenant installation version and explicitly rebinding the agent profile or publishing a workflow that references the new installation version.
- **FR-023**: Existing bindings MUST remain effective for their pinned installed skill version unless an authorized admin explicitly changes the binding, retires the binding, or publishes a workflow that references a different installation version.
- **FR-023a**: Mutable tenant installation readiness, credential configuration, smoke test readiness promotion, and skill binding changes MUST require an optimistic concurrency token; stale mutation requests MUST be rejected without state changes and MUST produce safe audit records.
- **FR-024**: The lifecycle MUST preserve tenant isolation for discovery, installation, validation evidence, smoke test evidence, credential readiness, binding, audit review, and exported lifecycle summaries.
- **FR-025**: The lifecycle MUST record audit events for package creation, package validation, validation failures, publication, tenant availability changes, tenant installation, credential-reference configuration, smoke test execution, readiness changes, binding attempts, binding changes, upgrade installation, authorization denials, and restricted-content redactions.
- **FR-026**: Audit records MUST include actor, time, scope, tenant when applicable, package slug, package version, installation version when applicable, affected binding when applicable, outcome, and safe summaries without raw secrets, raw credential values, or unsafe package payloads.
- **FR-027**: Admins MUST be able to review package lineages, package versions, tenant availability, tenant installations, readiness evidence, smoke test history, binding history, upgrade lineage, and audit summaries according to their authorization scope.
- **FR-028**: The system MUST support withdrawing a package version from new tenant installations while preserving existing installations, existing bindings, and historical audit evidence unless policy explicitly blocks future runtime use.
- **FR-028a**: Platform admins MUST be able to quarantine affected package versions and tenant installations when package artifacts, documentation, fixtures, or installed versions are later found unsafe; quarantine MUST block new tenant installations, readiness promotion, new bindings, and runtime use for affected installed versions until an authorized resolution removes the quarantine, while preserving immutable records and audit evidence.
- **FR-029**: Lifecycle views and exports MUST redact or omit raw secrets, raw credential values, unsafe package contents, and cross-tenant information.
- **FR-030**: Delivery MUST include user-facing documentation, README updates, reviewer testing instructions, PR notes, and automated test evidence showing at least 90 percent coverage for submitted code.

### Key Entities

- **Skill Package**: A platform-approved skill identity with a stable slug, description, owner, lifecycle state, and version lineage.
- **Skill Package Version**: An immutable published version of a skill package with a semantic version, manifest, safe documentation, validation evidence, and tenant availability rules.
- **Skill Package Artifact**: The internally stored immutable package payload for a published version, identified by pinned content, manifest, and documentation digests and used as provenance for validation, installation, audit, and readiness checks.
- **Skill Manifest**: The declared package metadata covering slug, semantic version, description, entrypoint type, tools, action categories, network requirements, credential requirements, runtime permissions, test fixtures, compatibility metadata, and safe documentation.
- **Tool Declaration**: A manifest item that describes a tool made available by the skill, including purpose, safe usage expectations, and action categories.
- **Approved Tool/MCP Integration Reference**: A manifest reference to an existing platform-approved tool or MCP integration that the skill may use as its runtime entrypoint under policy.
- **Credential Requirement**: A package-declared need for a secret reference or delegated credential requirement without storing raw secret or credential values.
- **Runtime Permission**: A declared permission the skill requires at runtime, including allowed network, data, or tool access expectations.
- **Test Fixture**: Safe package-declared input or setup information used for validation or tenant smoke tests.
- **Compatibility Metadata**: Declared constraints that determine whether a package version can be installed, bound, or used with tenant policy, agent profiles, workflow roles, or platform capabilities.
- **Tenant Availability Grant**: A platform-controlled decision that makes a package version discoverable and installable by one or more tenants.
- **Tenant Skill Installation**: A tenant-scoped immutable installation version that pins an exact skill package version and tracks readiness, credential references, smoke tests, compatibility, and bindings.
- **Smoke Test Result**: Tenant-scoped evidence from running package-declared tests against safe fixtures and configured credential references.
- **Skill Binding**: A governed relationship between an installed skill version and an agent profile or workflow role under existing skill-binding policies.
- **Optimistic Concurrency Token**: A revision identifier supplied with mutable installation, credential, readiness, and binding changes so stale admin updates can be rejected without changing lifecycle state.
- **Upgrade Lineage**: The relationship between older and newer tenant installation versions for the same package slug.
- **Quarantine Decision**: A platform-scoped safety action that blocks new installations, readiness promotion, new bindings, and runtime use for affected package versions or tenant installations until an authorized resolution is recorded.
- **Audit Record**: A safe lifecycle record for package, publication, availability, installation, credential, test, binding, upgrade, authorization, and redaction events.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of package publication attempts with missing manifest fields, duplicate semantic versions, unsafe documentation, disallowed permissions, or failed validation are blocked before a package version becomes available to tenants.
- **SC-002**: At least 90 percent of platform admins in acceptance testing can create, validate, publish, and grant tenant availability for a valid skill package version in under 20 minutes.
- **SC-003**: At least 90 percent of tenant admins in acceptance testing can discover an authorized skill version, install it, configure required credential references, run smoke tests, and reach a clear ready or blocked state in under 15 minutes.
- **SC-004**: 100 percent of tested tenant isolation scenarios prevent unauthorized tenants from discovering, installing, viewing smoke test evidence for, or binding skill versions outside their authorization scope.
- **SC-005**: 100 percent of tested raw package secrets and raw credential values are absent from package records, installation records, smoke test evidence, audit records, lifecycle views, and exported summaries.
- **SC-006**: 100 percent of tested upgrade scenarios keep existing bindings pinned to their original installed skill version until an authorized admin explicitly rebinds or publishes a workflow that references the new installation version.
- **SC-006a**: 100 percent of tested quarantine scenarios block new installations, readiness promotion, new bindings, and runtime use for affected installed versions while retaining safe lifecycle and audit history.
- **SC-006b**: 100 percent of tested stale readiness, credential configuration, smoke test readiness promotion, and binding mutation requests are rejected without state changes and produce safe audit evidence.
- **SC-007**: At least 95 percent of admins in acceptance testing can identify the blocking reason and corrective action for a failed validation, failed smoke test, missing credential reference, or denied binding within 2 minutes.
- **SC-008**: 100 percent of package creation, validation, publication, tenant availability, installation, credential configuration, smoke test, readiness, binding, upgrade, authorization denial, and redaction events produce safe audit records.
- **SC-009**: Reviewer evidence includes passing required tests, at least 90 percent automated coverage for submitted code, README updates, user-facing documentation, PR notes, and testing instructions.

## Assumptions

- Existing platform and tenant admin authorization rules remain authoritative for who can create packages, publish versions, grant availability, install skills, configure credential references, and bind skills.
- Existing skill-binding policies remain the authority for binding installed skills to agent profiles and workflow roles; this feature supplies registry, installation, readiness, and version evidence for those policies.
- Existing approved tool/MCP integrations remain the only runtime entrypoint surface for v1 skill packages; executable package runtimes and standalone external service entrypoints are deferred.
- Secret management already supports safe references and delegated credential requirements; this feature records references and readiness, not raw secret or credential values.
- Package documentation and fixtures are considered safe only after validation and may be restricted or redacted later if they are found unsafe.
- Withdrawing a package version from new installations does not automatically remove existing tenant installations or bindings unless a separate policy action blocks future runtime use.
- Semantic versioning is the required version format for published skill package versions.
- Tenant smoke tests are intended to prove installation readiness with safe fixtures and declared credential references, not to certify every possible runtime behavior.
