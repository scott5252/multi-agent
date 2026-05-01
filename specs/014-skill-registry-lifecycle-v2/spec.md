# Feature Specification: Skill Registry Lifecycle Browser Workflows

**Feature Branch**: `014-skill-registry-lifecycle-v2`  
**Created**: 2026-04-30  
**Status**: Draft  
**Input**: User description: "Revise Spec 014 as 014-skill-registry-lifecycle-v2 to close the UI workflow gap. Every primary skill lifecycle action must be executable from the admin browser UI by a non-technical platform admin or tenant admin. Curl, SQL, and direct API calls may be used only for environment setup, diagnostics, or automated tests, not for the main QA walkthrough. Add browser UI user stories and acceptance criteria for package creation, manifest entry or upload, candidate validation, immutable publication, tenant grants, tenant discovery, tenant installation, credential reference configuration, readiness and smoke-test updates, binding eligibility preview, stale revision recovery, cross-tenant isolation, redaction, and screenshot-backed QA evidence."

## Clarifications

### Session 2026-04-30

- Q: When a platform admin removes a tenant availability grant for a package version, what happens to existing tenant installations? -> A: Grant removal affects future discovery/install only; existing tenant installations remain pinned and usable unless quarantined or withdrawn.
- Q: How should tenant admins configure credential references in the browser? -> A: Tenant admins select existing tenant-authorized credential references from a browser picker; delegated credentials use predefined safe metadata fields only.
- Q: How should browser smoke-test run or rerun actions execute? -> A: Browser run/rerun enqueues a smoke-test job, then shows queued/running/final status with refresh or polling.
- Q: How should unauthorized direct links behave for cross-tenant versus same-tenant access failures? -> A: Cross-tenant direct links show absent/not found; same-tenant unauthorized role access shows denied.
- Q: Which manifest formats should browser text entry and upload support? -> A: Browser text entry and uploads accept YAML or JSON manifests validated against the existing v1 manifest schema.

### Inherited From Spec 014

- Published skill package versions remain immutable and lock internal package, manifest, and safe documentation provenance.
- Unsafe package versions or tenant installations can be quarantined without deleting historical lifecycle evidence.
- This lifecycle continues to support declarative package manifests and references to existing approved integrations only.
- Mutable tenant installation readiness, credential configuration, smoke-test readiness promotion, and binding-related changes use optimistic revision checks so stale updates are rejected without state changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish Skill Versions From The Browser (Priority: P1)

A non-technical platform admin can use `/admin/skill-registry/ui/packages` to create a platform-approved skill package, enter or upload a declarative manifest candidate, validate it, review blocking and nonblocking findings inline, publish an immutable package version after validation passes, and grant that version to one or more tenants without using command-line helper actions.

**Why this priority**: The lifecycle is not usable by platform administrators unless the trusted package creation, validation, publication, and grant path is complete in the browser.

**Independent Test**: Starting from an empty local QA environment and a logged-in platform admin browser session, the reviewer creates a package, submits a manifest candidate, validates it, publishes the validated version, grants it to Acme, and captures screenshots for each major step without using curl, SQL, or direct API calls for those feature actions.

**Acceptance Scenarios**:

1. **Given** a platform admin with package publishing rights, **When** they open `/admin/skill-registry/ui/packages` and choose to create a package, **Then** the browser displays a package creation workflow with clear fields for slug, description, owner or steward, lifecycle intent, and safe documentation summary.
2. **Given** the package creation workflow, **When** the platform admin enters a valid package identity and saves it, **Then** the browser shows the created package detail page with the package state, next action to add a manifest candidate, and no raw package payloads.
3. **Given** a package detail page, **When** the platform admin enters or uploads a YAML or JSON declarative manifest candidate, **Then** the browser validates it against the existing v1 manifest schema and shows a safe manifest summary, candidate revision, validation readiness, and any parse, format, or schema problems without exposing unsafe payload contents.
4. **Given** a manifest candidate, **When** the platform admin runs validation from the browser, **Then** blocking findings, warnings, and informational findings appear inline with affected manifest areas, severity, recommended correction, and validation status.
5. **Given** validation has blocking findings, **When** the platform admin attempts to publish, **Then** publication is unavailable or refused in the browser and the admin sees which findings must be corrected.
6. **Given** validation has passed with no blocking findings, **When** the platform admin publishes the version from the browser, **Then** an immutable package version is created and the browser displays the pinned version, provenance summary, validation evidence, and available grant action.
7. **Given** a published package version, **When** the platform admin grants it to Acme or to multiple selected tenants from the browser, **Then** the browser confirms the grant, shows the selected tenant availability list, and makes the version discoverable only to those tenant admins.

---

### User Story 2 - Install And Configure Granted Skills From The Browser (Priority: P2)

A tenant admin can discover granted skill versions, install a granted immutable version, configure required credential references or delegated credential metadata without entering raw secret values, run or review declared smoke-test evidence, and watch readiness, findings, and binding eligibility update in the browser.

**Why this priority**: Tenant administrators must be able to move from platform grant to tenant-ready installation without technical assistance or secret exposure.

**Independent Test**: A logged-in Acme tenant admin discovers the package version granted by the platform admin, installs it, configures credential references using only safe reference metadata, runs or refreshes smoke-test evidence, reaches a clear ready or blocked state, previews binding eligibility, and captures screenshots for each major step without command-line feature actions.

**Acceptance Scenarios**:

1. **Given** Acme has been granted a published skill version, **When** the Acme tenant admin opens the browser skill registry discovery page, **Then** the granted version appears with safe manifest summary, version, grant status, credential requirements, smoke-test expectations, and install action.
2. **Given** a granted version in discovery, **When** the Acme tenant admin installs it from the browser, **Then** the browser creates a tenant-scoped installation and shows the exact package version, tenant scope, installation revision, readiness state, credential status, smoke-test status, findings, and next actions.
3. **Given** an installation with credential requirements, **When** the Acme tenant admin configures credentials from the browser, **Then** they can select tenant-authorized existing secret references from a picker or complete predefined delegated credential metadata fields and cannot type arbitrary reference identifiers, enter raw secret values, reveal provider tokens, or store credential payloads.
4. **Given** credential configuration is saved, **When** the browser refreshes the installation detail page, **Then** readiness findings update to show satisfied, missing, revoked, wrong-scope, or incompatible credential requirements with safe corrective guidance.
5. **Given** the installation declares smoke tests, **When** the Acme tenant admin runs, reruns, or refreshes smoke-test status from the browser, **Then** run and rerun actions enqueue smoke-test jobs and the browser shows pass, fail, skipped, queued, running, and last-run evidence using safe fixture summaries only through refresh or polling.
6. **Given** all required credentials, compatibility checks, policy checks, and required smoke tests satisfy policy, **When** the installation detail page updates, **Then** the browser shows the installation as ready for binding and records the safe readiness evidence.
7. **Given** readiness is blocked, **When** the Acme tenant admin views the installation, **Then** the browser identifies each blocking reason and the recovery action without requiring the admin to inspect logs or command output.

---

### User Story 3 - Preview Binding Eligibility From The Browser (Priority: P3)

A tenant admin can preview whether a ready installed skill version is eligible for selected agent profiles or workflow roles from the browser before attempting to bind or publish dependent workflow changes.

**Why this priority**: Skill installations only become operationally useful when administrators can understand whether they may be bound under existing policy.

**Independent Test**: From a tenant installation detail page, the reviewer selects available profile or workflow-role contexts, previews binding eligibility, sees allow or deny results with policy reasons, and captures screenshots showing the eligibility result and any remediation guidance.

**Acceptance Scenarios**:

1. **Given** a tenant skill installation, **When** the tenant admin opens binding eligibility preview, **Then** the browser lets them choose a relevant profile or workflow role context available to their tenant.
2. **Given** the selected context is eligible, **When** the tenant admin previews eligibility, **Then** the browser shows an allowed result with the exact installation version, package version, readiness state, and safe policy summary.
3. **Given** the selected context is denied by readiness, policy, tenant authorization, action category, credential readiness, quarantine, or compatibility, **When** the tenant admin previews eligibility, **Then** the browser shows a denied result with actionable, redacted reasons.
4. **Given** a newer package version is later installed, **When** the tenant admin previews eligibility for existing bindings or contexts, **Then** the browser makes clear that existing bindings stay pinned until an authorized admin explicitly changes them.

---

### User Story 4 - Recover From Browser Stale Revision Conflicts (Priority: P4)

Platform and tenant admins receive clear in-browser conflict messages when another admin changes the same candidate, grant, credential configuration, readiness state, or binding-related projection before their pending form is submitted.

**Why this priority**: Optimistic revision checks protect lifecycle state, but non-technical admins need a clear recovery path when conflicts happen.

**Independent Test**: Two browser sessions open the same mutable workflow. One session saves a change. The second session submits an older revision and sees an in-browser stale revision conflict with no state change, a safe explanation, a refresh or compare path, and screenshot evidence.

**Acceptance Scenarios**:

1. **Given** two platform admins are editing the same manifest candidate or tenant grant list, **When** one admin saves first and the second submits a stale revision, **Then** the second admin sees a clear conflict message and no stale change is applied.
2. **Given** two tenant admins are editing the same credential reference configuration, readiness action, smoke-test promotion, or binding eligibility context, **When** one admin saves first and the second submits a stale revision, **Then** the second admin sees a clear conflict message and no stale change is applied.
3. **Given** a stale revision conflict occurs, **When** the admin follows the recovery path, **Then** the browser reloads the latest safe state and allows the admin to retry with the current revision.
4. **Given** a stale write is rejected, **When** an authorized admin reviews lifecycle evidence, **Then** a safe audit record exists for the rejected action without raw payloads, secrets, or cross-tenant data.

---

### User Story 5 - Preserve Tenant Isolation And Redaction In Every UI Page (Priority: P5)

Platform and tenant admins can review only the lifecycle data they are authorized to see, and every browser page preserves redaction guarantees for package contents, credentials, provider tokens, unsafe documentation, and cross-tenant data.

**Why this priority**: A browser-first lifecycle increases exposure risk unless every action and review page enforces tenant isolation and safe display rules.

**Independent Test**: Acme receives a package grant and creates an installation. Globex signs in through the browser and cannot discover, install, inspect, or infer Acme-only package versions, grants, installations, credentials, smoke-test evidence, or audit records. Screenshots show both Acme visibility and Globex denial or absence.

**Acceptance Scenarios**:

1. **Given** a package version is granted only to Acme, **When** Globex searches or browses granted skill versions, **Then** Globex cannot discover or install that package version.
2. **Given** Acme has an installation, credential readiness, smoke-test evidence, findings, binding eligibility previews, or audit records, **When** Globex attempts to inspect them through any browser page or direct link, **Then** the record appears absent or not found, no existence hint is exposed, and the attempt is safely recorded.
3. **Given** a same-tenant admin without the required role attempts to inspect protected skill lifecycle data through a browser page or direct link, **When** authorization fails, **Then** the browser shows an access-denied state without raw payloads, secrets, or cross-tenant data.
4. **Given** a platform admin views cross-tenant grant or installation summaries, **When** the page includes tenant-specific evidence, **Then** the browser shows only authorized safe summaries and never raw tenant credential data.
5. **Given** any UI page renders package, manifest, credential, fixture, validation, smoke-test, audit, export, or documentation information, **When** the page is displayed or screenshotted, **Then** it omits raw package payloads, raw credential values, provider tokens, unsafe docs, unsafe fixtures, and cross-tenant data.

---

### User Story 6 - Complete QA Walkthrough With Browser Actions (Priority: P6)

A reviewer can complete the QA UI guide using the browser for all feature actions, with terminal commands limited to environment setup, server startup, diagnostics, and automated evidence collection.

**Why this priority**: The definition of done depends on proving that the primary lifecycle is usable in the browser rather than through command-line helper actions.

**Independent Test**: The QA UI guide contains no curl, SQL, or direct API commands for creating packages, submitting manifests, validating candidates, publishing versions, granting tenants, installing skills, configuring credential references, running smoke tests, previewing binding eligibility, resolving stale revision conflicts, or demonstrating tenant isolation. Browser screenshots exist for every major lifecycle step.

**Acceptance Scenarios**:

1. **Given** a reviewer follows the QA UI guide, **When** they perform feature actions, **Then** every primary package, version, grant, installation, credential, smoke-test, readiness, eligibility, conflict, isolation, and redaction action is completed from the browser.
2. **Given** the QA UI guide includes terminal commands, **When** the reviewer reviews their purpose, **Then** those commands are limited to environment setup, server startup, diagnostics, or automated evidence commands.
3. **Given** the reviewer completes the guide, **When** they inspect the screenshot evidence directory, **Then** screenshots exist for package creation, manifest entry or upload, validation findings, publication, tenant grants, tenant discovery, tenant installation, credential reference configuration, readiness and smoke-test status, binding eligibility preview, stale revision conflict recovery, Acme visibility, Globex denial or absence, and redaction checks.

### Edge Cases

- A platform admin enters malformed YAML or JSON manifest text, uploads an unreadable file, uploads the wrong file type, uploads content that fails the existing v1 manifest schema, or uploads a manifest whose slug or version does not match the package being edited.
- A manifest candidate contains blocking findings and nonblocking warnings at the same time.
- A platform admin tries to publish a candidate that was not validated, failed validation, has stale validation results, or duplicates an existing semantic version.
- A platform admin grants a package version to multiple tenants, removes a tenant from future availability without disabling existing pinned installations, or submits an out-of-date tenant grant form.
- A tenant admin attempts to install a version that is not granted to their tenant, has been withdrawn from new installation, is quarantined, or has become incompatible with tenant policy.
- A tenant admin configures a credential reference that is missing, revoked, unauthorized, wrong-scope, incompatible, unavailable from the picker, or already removed outside the current browser session.
- A smoke test enqueue request is accepted, duplicated, rejected by policy, queued, running, failed, skipped, timed out, or blocked by credential readiness.
- Two admins submit changes to the same candidate, grant list, installation credential state, readiness state, smoke-test promotion, or binding-related preview using stale revisions.
- A browser back button, refresh, duplicate submit, or expired session occurs during a multi-step lifecycle action.
- Globex or any ungranted tenant follows a copied Acme package version, installation, smoke-test, credential, binding eligibility, or audit link and must see an absent or not-found state without existence hints.
- A same-tenant admin follows a protected lifecycle link without the required role and must see an access-denied state.
- Safe documentation, fixture summaries, or validation evidence later becomes restricted and must be redacted from existing browser pages and screenshots.
- A page has no records yet, no authorized grants, no eligible binding contexts, or no smoke-test history and must still provide a clear empty state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The admin browser UI MUST provide a platform admin entry point at `/admin/skill-registry/ui/packages` for creating and managing skill packages, candidates, package versions, and tenant grants.
- **FR-002**: Platform admins MUST be able to create a platform-approved skill package from the browser with stable package identity, description, stewardship, lifecycle state, and safe documentation summary.
- **FR-003**: Platform admins MUST be able to enter or upload a YAML or JSON declarative manifest candidate from the browser for a created skill package.
- **FR-004**: The browser UI MUST validate entered or uploaded manifests against the existing v1 manifest schema and show a safe manifest candidate summary, candidate revision, validation state, parse issues, schema issues, and next actions after manifest entry or upload.
- **FR-005**: Platform admins MUST be able to validate a manifest candidate from the browser.
- **FR-006**: The browser UI MUST display validation findings inline, separated into blocking, nonblocking warning, and informational categories with affected area, safe explanation, and suggested recovery.
- **FR-007**: The browser UI MUST prevent or refuse publication while a candidate has blocking findings, missing required validation, stale validation, duplicate version identity, or disallowed lifecycle state.
- **FR-008**: Platform admins MUST be able to publish an immutable skill package version from the browser only after validation passes.
- **FR-009**: Published package version pages MUST show immutable version identity, safe manifest summary, validation evidence, provenance summary, lifecycle state, and tenant grant options without exposing raw package payloads.
- **FR-010**: Platform admins MUST be able to grant a published package version to one or more tenants from the browser and review the current authorized tenant list; removing a tenant availability grant MUST affect future discovery and installation only and MUST NOT disable existing pinned installations unless a separate quarantine or withdrawal rule applies.
- **FR-011**: Tenant admins MUST be able to discover granted skill versions from the browser and MUST see only versions authorized for their tenant.
- **FR-012**: Tenant discovery pages MUST show safe package summaries, version, grant status, credential requirements, smoke-test expectations, compatibility summary, and install action for authorized versions.
- **FR-013**: Tenant admins MUST be able to install a granted skill version from the browser as a tenant-scoped immutable installation version.
- **FR-014**: Tenant installation pages MUST show exact package version, tenant scope, installation revision, readiness state, credential-reference status, smoke-test status, findings, compatibility, quarantine state, and binding eligibility entry points.
- **FR-015**: Tenant admins MUST be able to configure credential references from a browser picker containing existing tenant-authorized references and configure delegated credential metadata through predefined safe fields only; the UI MUST NOT allow arbitrary reference identifier entry, raw secret values, provider tokens, or credential payloads.
- **FR-016**: Credential configuration pages MUST show per-requirement readiness as satisfied, missing, revoked, unauthorized, wrong-scope, incompatible, or blocked, with safe corrective guidance.
- **FR-017**: Tenant admins MUST be able to run, rerun, or refresh declared smoke-test status from the browser when policy allows; run and rerun actions MUST enqueue smoke-test jobs instead of waiting synchronously for completion.
- **FR-018**: Smoke-test browser views MUST show queued, running, passed, failed, skipped, blocked, timeout, last-run time, safe fixture identity, safe evidence summary, and failure reasons without raw secret or unsafe fixture data, and MUST expose refresh or polling behavior for queued and running jobs.
- **FR-019**: Tenant installation readiness, smoke-test status, findings, credential readiness, and binding eligibility previews MUST update in the browser after relevant lifecycle actions.
- **FR-020**: Tenant admins MUST be able to preview binding eligibility from the browser for selected authorized profile or workflow-role contexts.
- **FR-021**: Binding eligibility previews MUST show allowed or denied status, exact installation version, safe policy reasons, readiness reasons, credential reasons, compatibility reasons, quarantine reasons, and recommended recovery where applicable.
- **FR-022**: The browser UI MUST make clear that installed versions and existing bindings are pinned and do not automatically move to newer package or installation versions.
- **FR-023**: Candidate edits, tenant grant changes, credential configuration, readiness actions, smoke-test readiness promotion, and binding-related mutable actions MUST use revision checks so stale browser submissions are rejected without state changes.
- **FR-024**: Stale revision conflicts MUST be shown in-browser with a plain-language explanation, no applied stale changes, a way to reload the latest safe state, and a path to retry the intended action.
- **FR-025**: Globex or any ungranted tenant MUST NOT be able to discover, install, inspect, preview binding eligibility for, or view audit evidence for Acme-only skill versions or installations from the browser; cross-tenant direct links MUST render absent or not found without existence hints, while same-tenant role failures MUST render an access-denied state.
- **FR-026**: All browser pages MUST preserve redaction guarantees by omitting raw package payloads, raw credential values, provider tokens, unsafe docs, unsafe fixtures, and cross-tenant data.
- **FR-027**: Browser pages MUST provide clear empty, blocked, denied, validation-failed, smoke-test-failed, quarantined, withdrawn, stale-conflict, and success states for non-technical admins.
- **FR-028**: Browser lifecycle actions MUST produce safe audit evidence for package creation, manifest submission, validation, publication, tenant grant changes, tenant discovery where audited, installation, credential configuration, smoke-test actions, readiness changes, binding eligibility previews, stale conflict rejection, authorization denial, and redaction events.
- **FR-029**: The QA UI guide MUST be completable with the browser for all feature actions; terminal commands in that guide MUST be limited to environment setup, server startup, diagnostics, or automated evidence collection.
- **FR-030**: Browser screenshot evidence MUST exist for every major lifecycle step: package creation, manifest entry or upload, validation findings, publication, tenant grants, tenant discovery, tenant installation, credential reference configuration, readiness and smoke-test status, binding eligibility preview, stale revision conflict recovery, authorized tenant visibility, unauthorized tenant denial or absence, and redaction checks.

### Key Entities

- **Skill Package**: A platform-approved skill identity with stable slug, description, steward, lifecycle state, safe documentation summary, and package version lineage.
- **Manifest Candidate**: A browser-submitted or uploaded YAML or JSON declarative manifest draft for a skill package, validated against the existing v1 manifest schema, with candidate revision, validation state, safe summary, and findings.
- **Validation Finding**: A safe browser-visible result from candidate validation with severity, affected area, explanation, and recovery guidance.
- **Skill Package Version**: An immutable published version of a skill package with semantic version, safe manifest summary, provenance summary, validation evidence, lifecycle state, and tenant availability controls.
- **Tenant Availability Grant**: A platform admin decision that makes a published package version discoverable and installable by selected tenants.
- **Tenant Skill Installation**: A tenant-scoped immutable installation version that pins an exact package version and tracks readiness, credentials, smoke tests, compatibility, quarantine, findings, and binding eligibility.
- **Credential Reference Configuration**: Tenant-selected existing authorized safe reference or predefined delegated credential metadata that satisfies package credential requirements without arbitrary reference identifiers or raw secret values.
- **Smoke-Test Evidence**: Tenant-scoped safe evidence for declared tests, including status, last-run time, safe fixture identity, outcome, and failure reasons.
- **Binding Eligibility Preview**: A browser-visible allow or deny result for using an installed skill version with a selected profile or workflow role context.
- **Revision Conflict**: A rejected stale browser submission caused by another change to the same mutable lifecycle state.
- **Redaction Boundary**: The rule set that prevents raw package payloads, credentials, provider tokens, unsafe docs, unsafe fixtures, and cross-tenant data from appearing in lifecycle pages or evidence.
- **Audit Record**: A safe lifecycle record for browser actions, outcomes, denials, stale conflicts, and redactions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of primary skill lifecycle actions in the QA UI walkthrough are completed through browser pages, including package creation, manifest submission, validation, publication, tenant grants, tenant discovery, installation, credential configuration, smoke-test actions, readiness review, binding eligibility preview, stale conflict recovery, tenant isolation checks, and redaction checks.
- **SC-002**: The QA UI guide contains zero curl, SQL, or direct API commands for primary feature actions; any terminal commands are limited to environment setup, server startup, diagnostics, or automated evidence collection.
- **SC-003**: Browser screenshot evidence exists for 100 percent of the major lifecycle steps named in the definition of done.
- **SC-004**: At least 90 percent of platform admins in acceptance testing can create a package, submit or upload a manifest, validate it, publish a version, and grant it to a tenant from the browser in under 20 minutes.
- **SC-005**: At least 90 percent of tenant admins in acceptance testing can discover, install, configure credentials, review or run smoke tests, identify readiness, and preview binding eligibility from the browser in under 15 minutes.
- **SC-006**: 100 percent of tested blocking validation findings prevent browser publication until corrected, while nonblocking findings remain visible and do not prevent publication when policy allows.
- **SC-007**: 100 percent of tested browser smoke-test run or rerun actions return a queued or running status page without waiting synchronously for final execution, and later display the final safe result through refresh or polling.
- **SC-008**: 100 percent of tested stale browser submissions are rejected without state changes and show a recovery path that lets the admin reload current state and retry.
- **SC-009**: 100 percent of tested Globex or ungranted-tenant scenarios prevent discovery, installation, inspection, binding eligibility preview, smoke-test evidence review, credential review, and audit review for Acme-only package versions or installations, and cross-tenant direct-link attempts show absent or not-found states without existence hints.
- **SC-010**: 100 percent of tested browser pages and screenshot evidence omit raw package payloads, raw credential values, provider tokens, unsafe documentation, unsafe fixtures, and cross-tenant data.
- **SC-011**: At least 95 percent of admins in acceptance testing can identify the next corrective action for validation failure, credential readiness failure, smoke-test failure, binding eligibility denial, quarantine, withdrawal, or stale conflict within 2 minutes from the browser.

## Assumptions

- Existing Spec 014 backend lifecycle capabilities remain available and authoritative for package candidates, validation, immutable publication, tenant grants, installation, credential readiness, smoke-test evidence, binding eligibility, stale revision rejection, audit, redaction, and tenant isolation.
- Existing platform admin and tenant admin authorization rules remain authoritative for which browser pages and actions each user can access.
- Existing secret management supports safe secret references and delegated credential metadata; V2 exposes browser configuration for references and metadata, not raw credential values.
- Existing package validation, smoke testing, binding eligibility, quarantine, audit, and redaction policies remain authoritative; V2 focuses on making those outcomes actionable and understandable in the browser.
- The browser UI is intended for non-technical administrators on desktop-sized admin workstations; responsive behavior should remain usable, but mobile-first lifecycle execution is not the primary acceptance target.
- Browser screenshots are reviewer evidence artifacts and must themselves obey the same redaction and tenant isolation guarantees as the pages they capture.
