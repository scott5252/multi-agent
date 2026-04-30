# Contract: Admin Skill Registry Browser UI V2

This contract replaces the primary curl/API helper path in the Spec 014 UI QA
walkthrough with server-rendered admin browser flows. Existing JSON API
endpoints under `/admin/skill-registry` remain available for automation,
diagnostics, integrations, and tests, but they are no longer the primary QA
path for non-technical users.

All pages use the existing shared admin shell, Auth0/local-principal
authorization, tenant-scope handling, breadcrumbs/navigation, safe empty/error
states, template styles, audit helpers, and redaction helpers.

## Global UI Requirements

- All mutation forms must work with standard browser POST submits.
- All POST handlers must call existing skill registry service/repository
  operations where possible.
- All forms must include CSRF/session protections where the admin shell
  provides them.
- All mutable actions must include the relevant revision token when one exists.
- All rendered pages must include the standard redaction notice.
- Raw package payloads, raw credential values, provider tokens, unsafe docs,
  unsafe fixtures, raw validation input, raw smoke-test logs, and cross-tenant
  data must never render in HTML, page source, error pages, exports, or
  screenshot evidence.
- Success actions may redirect with flash messages or render the updated safe
  state. Validation failures should render the same form with field-level and
  page-level errors.

## Platform Package List

**GET** `/admin/skill-registry/ui/packages`

Lists platform packages visible to the signed-in principal.

**Required controls**:

- Create package action for platform admins.
- Filters for slug, steward/owner, lifecycle state, validation state, tenant
  availability, withdrawal, quarantine, and latest version where supported.
- Links to package detail and version detail when authorized.

**Required states**:

- Empty state: no packages visible.
- Denied state: same-tenant or role failure without raw data.
- Redaction state: visible notice and omitted raw data.

## Create Package

**GET** `/admin/skill-registry/ui/packages/new`
**POST** `/admin/skill-registry/ui/packages`

Creates a platform-approved package lineage root.

**Fields**:

- `slug`
- `display_name`
- `description`
- `steward_principal_id` or owner
- `lifecycle_intent`
- `safe_documentation_summary`
- `idempotency_key`

**POST behavior**:

- Requires platform admin role.
- Validates slug/required fields and duplicate package state.
- Delegates to existing package creation service.
- Redirects to `/admin/skill-registry/ui/packages/{slug}` on success.
- Renders field errors or duplicate conflict on failure.

## Package Detail

**GET** `/admin/skill-registry/ui/packages/{slug}`

Shows safe package metadata, candidate status, version lineage, current tenant
grants, and audit timeline.

**Required controls**:

- Add or edit manifest candidate.
- Validate candidate if a candidate exists.
- Publish candidate only when validation is current and nonblocking.
- Open tenant grant form for published versions.

**Required states**:

- No candidate yet.
- Candidate has parse/schema errors.
- Candidate validation has blocking findings.
- Candidate is publishable.
- Stale conflict banner after stale POST redirect.

## Manifest Candidate Entry And Upload

**GET** `/admin/skill-registry/ui/packages/{slug}/candidate`
**POST** `/admin/skill-registry/ui/packages/{slug}/candidate`

Allows platform admins to paste or upload YAML/JSON manifests.

**Fields**:

- `manifest_text`
- `manifest_file`
- `input_format` (`yaml`, `json`, or auto)
- `artifact_digest` or artifact reference
- `approved_integration_refs`
- `candidate_revision`
- `idempotency_key`
- `validation_reason`

**POST behavior**:

- Requires platform admin role.
- Accepts either paste or upload; if both are present, the explicit uploaded
  file takes precedence and the page explains which source was used.
- Parses YAML/JSON with structured parsers.
- Validates against the existing v1 manifest schema.
- Stores or computes candidate revision where supported.
- Renders safe manifest summary, digest, candidate revision, parse errors,
  schema issues, and next actions.
- Does not echo raw manifest text back to the browser.

## Candidate Validation

**POST** `/admin/skill-registry/ui/packages/{slug}/candidate/validate`

Runs validation for the current candidate.

**Fields**:

- `candidate_revision`
- `validation_reason`
- `idempotency_key`

**POST behavior**:

- Requires platform admin role.
- Rejects stale candidate revision with conflict state.
- Delegates to existing validation pipeline.
- Renders inline findings grouped as blocking, warning, and informational.
- Shows affected area, field path where safe, safe explanation, and
  recommended correction.
- Enables publish action only when validation is current and has no blocking
  findings.

## Publish Immutable Version

**POST** `/admin/skill-registry/ui/packages/{slug}/candidate/publish`

Publishes a validated candidate as an immutable package version.

**Fields**:

- `candidate_revision`
- `semantic_version`
- `publish_reason`
- `idempotency_key`

**POST behavior**:

- Requires platform admin role.
- Refuses publication when validation is missing, failed, stale, blocking,
  duplicated by semantic version, slug/version mismatched, or lifecycle state
  disallows publication.
- Delegates to existing publish service.
- Redirects to version detail on success.
- Renders safe blocked reason and recovery action on failure.

## Version Detail And Tenant Grants

**GET** `/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}`

Shows immutable version provenance, safe manifest summary, artifact and
manifest digests, validation evidence, lifecycle state, grant summary,
credential requirements, smoke-test expectations, compatibility, and audit.

**GET** `/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}/grants`
**POST** `/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}/grants`

Manages tenant availability.

**Fields**:

- `selected_tenant_ids`
- `grant_reason`
- `grant_revision`
- `idempotency_key`

**POST behavior**:

- Requires platform admin role.
- Grants one or more selected tenants.
- Removing a tenant grant affects future discovery/install only.
- Existing pinned installations remain usable unless separately quarantined or
  withdrawn by policy.
- Rejects stale grant revision with conflict state.

## Available Skill Versions Tenant Page

**GET** `/admin/skill-registry/ui/available-versions?tenant_id={tenant_id}`

Lists versions discoverable and installable by the selected tenant.

**Required content**:

- Safe package/version summary.
- Grant status.
- Credential requirements.
- Smoke-test expectations.
- Compatibility summary.
- Withdrawal/quarantine indicators.
- Install action for installable versions.

**Required states**:

- Empty state for no authorized grants.
- Cross-tenant direct links render absent/not found.
- Same-tenant role failures render denied.

## Tenant Install Action

**POST** `/admin/skill-registry/ui/installations`

Installs a granted immutable package version for the selected tenant.

**Fields**:

- `tenant_id`
- `slug`
- `semantic_version`
- `previous_installation_id`
- `idempotency_key`

**POST behavior**:

- Requires tenant admin access to `tenant_id`.
- Delegates to existing install service.
- Redirects to installation detail with exact package version, installation
  version, revision token, readiness state, credential status, smoke-test
  status, and binding eligibility state.
- Ungranted, quarantined, withdrawn, incompatible, or cross-tenant installs
  fail closed with safe state.

## Installation List And Detail

**GET** `/admin/skill-registry/ui/installations?tenant_id={tenant_id}`
**GET** `/admin/skill-registry/ui/installations/{installation_id}`

Shows tenant-scoped installed skills and exact installation detail.

**Required detail sections**:

- Tenant scope and exact package/install version.
- Manifest and artifact digests.
- Revision token.
- Readiness state and findings.
- Credential-reference status.
- Smoke-test status/history.
- Binding eligibility preview panel.
- Quarantine/runtime block indicators.
- Audit timeline.

**Required states**:

- Empty installation list.
- Ready, blocked, smoke-test failed, quarantined, withdrawn, denied, not found.
- Pinned version note: installed versions and existing bindings do not float to
  newer package versions.

## Credential Reference Configuration

**GET** `/admin/skill-registry/ui/installations/{installation_id}/credentials`
**POST** `/admin/skill-registry/ui/installations/{installation_id}/credentials`

Configures credential references for an installation.

**Fields**:

- `revision_token`
- one row per manifest credential requirement
- `selected_reference_id` from tenant-authorized picker options
- predefined delegated credential metadata fields
- `idempotency_key`

**POST behavior**:

- Requires tenant admin access to the installation tenant.
- Does not accept arbitrary reference identifiers from text fields.
- Does not contain raw secret input fields.
- Detects missing, revoked, unauthorized, wrong-scope, incompatible, or
  removed references and renders per-requirement readiness findings.
- Rejects stale revision with conflict state and no state change.

## Smoke-Test And Readiness Evidence

**POST** `/admin/skill-registry/ui/installations/{installation_id}/smoke-tests`

Enqueues run/rerun for declared smoke tests.

**Fields**:

- `revision_token`
- `fixture_keys`
- `action_reason`
- `idempotency_key`

**POST behavior**:

- Requires tenant admin access.
- Enqueues a job when policy allows.
- Renders queued/running status immediately.
- Provides refresh or optional polling for final status.
- Shows passed, failed, skipped, blocked, timeout, last-run time, safe fixture
  identity, safe evidence summary, and redacted failure reasons.

## Binding Eligibility Preview

**POST** `/admin/skill-registry/ui/installations/{installation_id}/eligibility-preview`

Previews whether an installation can be bound to a selected profile or
workflow-role context.

**Fields**:

- `revision_token`
- `context_type`
- `context_id`

**POST behavior**:

- Requires tenant admin access.
- Context options are limited to authorized profiles or workflow roles.
- Delegates to existing eligibility/policy preview services.
- Renders allowed or denied result with pinned installation version, package
  version, readiness state, safe policy reasons, credential reasons,
  compatibility reasons, quarantine reasons, and recovery guidance.

## Stale Revision Conflict

Applies to candidate, grant, credential, readiness/smoke, and binding-related
mutable actions.

**Required behavior**:

- Return a safe 409-equivalent UI state or redirect with a conflict flash.
- Apply no stale state change.
- Record safe audit evidence for the rejected action.
- Explain the conflict in plain language.
- Provide reload-latest and retry affordances.
- Do not render the raw submitted payload.

## Cross-Tenant Denial And Empty States

- Globex or any ungranted tenant cannot discover, install, inspect, preview,
  or view evidence for Acme-only skill versions or installations.
- Cross-tenant direct links render absent/not found without existence hints.
- Same-tenant role failures render access denied.
- Empty states must be clear for no packages, no candidate, no grants, no
  available versions, no installations, no smoke-test history, and no eligible
  binding contexts.

## Tests Required By This Contract

- Browser GET/POST route tests for every route above.
- Template assertions for field errors, inline findings, safe notices, empty
  states, denied/not-found states, and conflict states.
- Authorization tests for platform-only, tenant-only, cross-tenant, and
  same-tenant denied cases.
- Redaction tests that render representative unsafe payloads and assert they
  are absent.
- Docs test that fails if `qa014_ui.md` reintroduces curl, SQL, or direct API
  commands for primary lifecycle actions.
