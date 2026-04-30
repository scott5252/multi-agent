# Data Model: Skill Registry Lifecycle Browser Workflows

This V2 feature is primarily a browser workflow increment. It reuses the
existing Spec 014 lifecycle data model for packages, package versions,
availability grants, tenant installations, credentials, smoke tests,
eligibility, and audit records. New persistent data should be added only if
existing tables cannot durably represent browser candidate revisions,
validation run linkage, grant-list revision tokens, or form idempotency keys.

## SkillPackageBrowserForm

Browser form used by platform admins to create a package lineage root.

**Fields**: `slug`, `display_name`, `description`, `steward_principal_id`,
`lifecycle_intent`, `safe_documentation_summary`, `idempotency_key`.

**Maps to**: Existing `SkillPackageCreateRequest` and package creation
service/repository operation.

**Validation rules**: Slug is lowercase and globally unique. Safe
documentation summary is redacted before rendering or persistence. Duplicate
submits with the same idempotency key return the existing safe result where
supported.

**UI states**: Empty form, field validation errors, duplicate package conflict,
created success redirect, same-tenant denied, platform-role denied.

## ManifestCandidateBrowserState

Browser-visible state for a pasted or uploaded manifest candidate.

**Fields**: `candidate_id` if persisted, `package_slug`, `candidate_revision`,
`input_format`, `safe_manifest_summary`, `manifest_digest`, `artifact_digest`
or artifact reference, `validation_status`, `validation_run_id`,
`validated_revision`, `blocking_count`, `warning_count`, `info_count`,
`created_by_principal_id`, `updated_by_principal_id`, `updated_at`.

**Maps to**: Existing manifest schema, validation result, package version
publication service, artifact metadata, and audit records.

**Validation rules**: Candidate text/upload must parse as YAML or JSON and
must validate against the existing v1 manifest schema. Candidate manifest slug
must match the package slug. Publication requires the validation result to
refer to the current candidate revision and to contain no blocking findings.

**UI states**: New candidate, parse failed, schema failed, validation pending,
validation failed with blocking findings, validation passed with warnings,
stale validation, publish blocked, publish succeeded.

**Migration note**: If existing Spec 014 storage lacks durable candidate
revision records, add an additive table or JSON metadata column for candidate
revision, safe summary, validation linkage, and idempotency evidence. Do not
mutate published package version rows.

## ValidationFindingView

Safe browser rendering of candidate validation findings.

**Fields**: `severity`, `blocking`, `code`, `affected_area`, `field_path`,
`safe_explanation`, `recommended_correction`, `source_revision`.

**Maps to**: Existing `SkillValidationFinding` and
`SkillRegistryFindingResponse`.

**Validation rules**: Findings never include raw manifest payload, raw package
contents, unsafe docs, secrets, credential values, provider tokens, or
cross-tenant data. Blocking findings prevent publication. Warnings and
informational findings remain visible and do not block publication unless
policy marks them blocking.

## PackageVersionPublishAction

Browser action that creates an immutable package version from a validated
candidate.

**Fields**: `package_slug`, `candidate_revision`, `semantic_version`,
`manifest_digest`, `artifact_digest`, `validation_run_id`, `publish_reason`,
`idempotency_key`, `actor_principal_id`.

**Maps to**: Existing package version publication service and
`SkillPackageVersion`.

**Validation rules**: Requires platform admin role, current successful
validation, no blocking findings, no duplicate semantic version, matching
manifest slug/version, allowed lifecycle state, and current candidate revision.

**UI states**: Publish available, publish disabled, publish refused with safe
reason, duplicate version conflict, stale revision conflict, published success
redirect to version detail.

## TenantAvailabilityGrantForm

Browser form used by platform admins to grant or remove future availability
for one or more tenants.

**Fields**: `package_slug`, `semantic_version`, `selected_tenant_ids`,
`grant_reason`, `grant_revision`, `idempotency_key`, `actor_principal_id`.

**Maps to**: Existing tenant availability grant records and service methods.

**Validation rules**: Requires platform admin role and published package
version. Removing a grant affects only future discovery and installation; it
does not disable existing pinned tenant installations unless a separate
quarantine or withdrawal rule applies. Stale grant revisions reject with no
state change.

**UI states**: No tenants selected, grant saved, partial tenant validation
errors, stale grant conflict, empty grant list, cross-tenant safe summaries.

## AvailableSkillVersionView

Tenant-scoped browser projection of package versions available to install.

**Fields**: `tenant_id`, `package_slug`, `semantic_version`,
`safe_manifest_summary`, `grant_status`, `credential_requirements`,
`smoke_test_expectations`, `compatibility_summary`, `withdrawal_state`,
`quarantine_state`, `install_action_enabled`.

**Maps to**: Existing `list_available_versions` service/repository query and
package version response model.

**Validation rules**: Tenant admins see only versions granted to their tenant
and not blocked for new installs. Ungranted tenants receive an empty state or
not-found direct-link response without existence hints.

## TenantInstallAction

Browser action that installs an authorized immutable package version for a
tenant.

**Fields**: `tenant_id`, `package_slug`, `semantic_version`,
`previous_installation_id`, `idempotency_key`, `actor_principal_id`.

**Maps to**: Existing tenant installation create service and
`SkillInstallation`.

**Validation rules**: Requires tenant admin access to `tenant_id`, a granted
and installable package version, non-quarantined/non-withdrawn state for new
installs, and tenant policy compatibility. Creates a new immutable
installation version pinned to exact package version, manifest digest, and
artifact digest.

**UI states**: Install available, install denied, installed but readiness
blocked, installed ready, duplicate submit, cross-tenant absent/not found.

## CredentialReferenceConfigForm

Browser form for satisfying installation credential requirements.

**Fields**: `installation_id`, `tenant_id`, `revision_token`,
`requirement_key`, `credential_kind`, `selected_reference_id`,
`delegated_metadata_fields`, `safe_summary`, `idempotency_key`.

**Maps to**: Existing `ConfigureCredentialsRequest`,
`CredentialReferenceSummary`, credential readiness records, and readiness
recompute service.

**Validation rules**: Options are limited to active tenant-authorized secret
references or delegated credential links. The form must not expose arbitrary
reference id entry, raw secret values, provider tokens, or credential payloads.
Wrong-scope, revoked, missing, incompatible, unauthorized, or removed
references show safe per-requirement findings. Stale revision tokens reject
with no state change.

## SmokeTestActionView

Browser action/status model for run, rerun, refresh, and evidence review.

**Fields**: `installation_id`, `tenant_id`, `revision_token`,
`fixture_keys`, `job_id`, `runner_status`, `outcome`, `last_run_at`,
`safe_fixture_identity`, `safe_evidence_summary`, `failure_reasons`,
`refresh_url`, `idempotency_key`.

**Maps to**: Existing smoke-test job/evidence records and readiness summary.

**Validation rules**: Run/rerun actions enqueue work and return queued/running
status without waiting for final execution. Evidence omits raw logs, raw
fixtures, raw credentials, provider tokens, and cross-tenant data. Duplicate
enqueue uses idempotency behavior where supported.

## BindingEligibilityPreviewForm

Browser form and result for checking whether an installation can be used by a
selected profile or workflow role context.

**Fields**: `installation_id`, `tenant_id`, `revision_token`,
`selected_context_type`, `selected_context_id`, `allowed`, `reason_codes`,
`safe_policy_summary`, `readiness_reasons`, `credential_reasons`,
`compatibility_reasons`, `quarantine_reasons`, `pinned_version_evidence`.

**Maps to**: Existing binding eligibility service and Spec 007
model_skill_config policy preview/resolver.

**Validation rules**: Context choices are limited to authorized tenant
profiles or workflow roles. Denials show actionable, redacted reasons.
Results make clear that existing bindings remain pinned until explicitly
changed.

## RevisionConflictView

Browser-visible stale submission state.

**Fields**: `resource_type`, `resource_id`, `submitted_revision`,
`current_revision`, `safe_message`, `reload_url`, `retry_url`,
`audit_record_id`.

**Maps to**: Existing service stale revision errors and safe audit records.

**Validation rules**: A stale write applies no state change. The view must not
include raw submitted payloads. The recovery path reloads latest safe state and
requires retry with the current revision.

## RedactionSafePageContext

Shared page context and template contract for all browser pages.

**Fields**: `redaction_notice`, `safe_summaries`, `redacted_fields`,
`tenant_scope_label`, `denial_state`, `empty_state`, `audit_events`.

**Maps to**: Existing admin shell, redaction helpers, and audit timeline
partials.

**Validation rules**: Rendered HTML and screenshot evidence omit raw package
payloads, raw credential values, provider tokens, unsafe docs, unsafe
fixtures, and cross-tenant data. Cross-tenant absence and same-tenant denial
states must be safe and auditable.
