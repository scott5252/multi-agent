# Data Model: Skill Registry And Installation Lifecycle

## SkillPackage

Platform-approved skill identity and lineage root.

**Table**: `skill_packages`

**Fields**: `skill_package_id`, `slug`, `display_name`, `description`,
`owner_principal_id`, `approval_status`, `lifecycle_state`,
`safe_documentation_summary`, `latest_published_version`,
`created_by_principal_id`, `created_at`, `updated_at`, `retired_at`,
`quarantined_at`.

**Relationships**: Owns many SkillPackageVersion records and SkillAuditRecord
events.

**Validation rules**: `slug` is globally unique, lowercase, stable, and
matches the manifest slug. Description and safe documentation summary are
redacted before storage. Retired packages cannot accept new package versions
unless reactivated by a platform admin.

**State transitions**: `draft` -> `approved` -> `retired`; `approved` ->
`quarantined`; `quarantined` -> `approved` only through an authorized
resolution audit event.

## SkillPackageVersion

Immutable published package version.

**Table**: `skill_package_versions`

**Fields**: `skill_package_version_id`, `skill_package_id`, `slug`,
`semantic_version`, `manifest_digest`, `manifest_snapshot`,
`safe_manifest_summary`, `artifact_id`, `artifact_digest`,
`documentation_artifact_id`, `documentation_digest`, `fixture_artifact_id`,
`fixture_digest`, `compatibility_metadata`, `validation_status`,
`validation_summary`, `lifecycle_state`, `availability_mode`,
`published_by_principal_id`, `published_at`, `withdrawn_at`,
`quarantined_at`, `runtime_blocked_at`, `created_at`.

**Relationships**: Belongs to SkillPackage; references ArtifactRecord rows for
package payload, docs, fixtures, and optional validation evidence; owns
TenantAvailabilityGrant rows; is pinned by SkillInstallation rows; is
referenced by SkillAuditRecord and QuarantineDecision.

**Validation rules**: Unique `(skill_package_id, semantic_version)`.
Semantic version must be valid SemVer. Manifest slug and version must match
the package slug and version. Published rows are immutable except lifecycle
columns for withdrawal/quarantine/runtime block and additive audit evidence.
Artifact, manifest, documentation, and fixture digests are required before
publication.

**State transitions**: `candidate` -> `validated` -> `published`;
`published` -> `withdrawn_from_new_installs`; `published` or `withdrawn` ->
`quarantined`; `quarantined` -> `published` or `withdrawn_from_new_installs`
through authorized resolution.

## SkillPackageArtifact

Object-storage provenance for package payloads and oversized evidence.

**Storage**: Existing `artifacts` table plus skill-specific metadata in
SkillPackageVersion and SkillInstallationTest.

**Fields**: `artifact_id`, `tenant_id` null for platform packages,
`scope_type = skill_package`, `provider`, `storage_key`, `media_type`,
`size_bytes`, `checksum`, `retention_class`, `status`, `created_at`,
`updated_at`.

**Relationships**: Referenced by SkillPackageVersion package, docs, fixtures,
validation evidence, and by SkillInstallationTest evidence reports.

**Validation rules**: Artifact keys are content-addressed by package slug,
semantic version, artifact purpose, and digest. Writes are idempotent and must
verify checksum before publication. Raw credentials and unsafe secrets are
forbidden in package artifacts and evidence payloads.

## SkillManifest

Typed schema stored as immutable JSON snapshot on SkillPackageVersion.

**Fields**: `schema_version`, `slug`, `semantic_version`, `description`,
`entrypoint`, `tools`, `action_categories`, `network_requirements`,
`credential_requirements`, `runtime_permissions`, `test_fixtures`,
`compatibility`, `safe_documentation`, `artifact_digests`, `maintainers`,
`support`, `deprecation`.

**Relationships**: Drives SkillPackageVersion validation,
SkillInstallation readiness, smoke tests, Spec 007 binding eligibility,
allowed tool policies, outbound domain policies, credential requirements, and
workflow publish validation.

**Validation rules**: `entrypoint.type` must be `approved_tool_ref` or
`approved_mcp_ref`. Arbitrary executable code, standalone external HTTP
service entrypoints, embedded raw secrets, credential values, undeclared
network access, unknown tool ids, unknown action categories, and unsafe docs
are blocking findings. Canonical JSON is sorted and hashed to
`manifest_digest`.

## ToolDeclaration

Manifest-declared tool surface.

**Fields**: `tool_id`, `display_name`, `description`, `approved_integration_id`,
`entrypoint_ref`, `action_categories`, `input_contract_ref`,
`output_contract_ref`, `safe_usage`, `side_effect_profile`.

**Relationships**: Compared against existing approved tool/MCP integration
catalog and Spec 007 allowed tool policy vocabulary.

**Validation rules**: Tool ids are unique within a manifest. Action categories
must be recognized. Side-effect profile must be compatible with policy and
smoke-test fixture declarations.

## CredentialRequirement

Package-declared credential need without secret material.

**Fields**: `requirement_key`, `credential_kind`, `tool_id`,
`action_category`, `required`, `allowed_secret_reference_scopes`,
`delegated_credential_scopes`, `rotation_policy`, `safe_description`.

**Relationships**: Satisfied by SkillInstallationCredentialReadiness records
that reference existing `secret_references`, Spec 007
`secret_reference_versions`, or `delegated_credential_links`.

**Validation rules**: Raw values are forbidden. Required credentials must map
to declared tools and action categories. Tenant installation readiness fails
when referenced secrets are missing, revoked, expired, unauthorized,
cross-tenant, wrong-scope, or incompatible with delegated credential policy.

## RuntimePermission

Manifest-declared runtime permission.

**Fields**: `permission_key`, `permission_type`, `tool_id`,
`action_category`, `network_domains`, `data_scope`, `side_effect_level`,
`required`, `safe_description`.

**Relationships**: Evaluated against Spec 007 allowed tool policies, outbound
domain policies, credential requirements, and runtime policy decisions.

**Validation rules**: Domains are lowercased and IDNA-normalized before
comparison. Wildcards must be explicit and bounded. Permissions outside
tenant or workflow policy fail validation or binding eligibility.

## TestFixture

Safe package-declared fixture used by package validation and tenant smoke
tests.

**Fields**: `fixture_key`, `tool_id`, `action_category`, `fixture_kind`,
`safe_input_summary`, `object_storage_ref`, `fixture_digest`,
`requires_credentials`, `expected_outcome`, `timeout_seconds`.

**Relationships**: Referenced by SkillInstallationTest and validation
evidence.

**Validation rules**: Fixtures must be classified safe before publication.
Fixtures cannot include raw secrets, live tenant data, credential values, or
undeclared network destinations. Timeout and side-effect profile must fit the
runner policy.

## TenantAvailabilityGrant

Platform decision that makes package versions discoverable and installable.

**Table**: `skill_package_tenant_grants`

**Fields**: `tenant_grant_id`, `skill_package_version_id`, `tenant_id` null
for all tenants, `grant_mode`, `status`, `granted_by_principal_id`,
`granted_at`, `revoked_at`, `reason`, `audit_record_id`.

**Relationships**: Read by tenant discovery and installation authorization.

**Validation rules**: Grant checks must combine package lifecycle,
withdrawal/quarantine state, tenant scope, and platform authorization.
Revoking availability blocks new installs only and does not delete historical
installations.

## SkillInstallation

Tenant-scoped immutable installation version and readiness projection.

**Table**: `skill_installations`

**Fields**: `skill_installation_id`, `tenant_id`,
`skill_package_version_id`, `slug`, `semantic_version`,
`installation_version`, `previous_installation_id`,
`manifest_digest`, `manifest_summary`, `artifact_digest`,
`readiness_state`, `credential_status`, `compatibility_status`,
`permission_status`, `smoke_test_status`, `binding_eligibility_status`,
`policy_summary`, `findings`, `quarantine_state`, `runtime_blocked`,
`installed_by_principal_id`, `installed_at`, `ready_at`, `retired_at`,
`revision_token`, `updated_at`.

**Relationships**: Belongs to tenant and SkillPackageVersion; owns
SkillInstallationCredentialReadiness, SkillInstallationTest, upgrade lineage,
quarantine decisions, and SkillAuditRecord events; is referenced by Spec 007
SkillBindingVersion through exact installation evidence.

**Validation rules**: Unique `(tenant_id, slug, installation_version)`.
Installation version is assigned monotonically per tenant and package slug.
Package version, manifest digest, artifact digest, and version summary are
immutable. Mutable readiness/configuration writes require `revision_token` and
reject stale requests with no state change.

**State transitions**: `installed` -> `configuring` -> `testing` ->
`ready`; any active state -> `blocked`; any active state -> `quarantined`;
`ready` -> `retired`; `quarantined` -> prior non-ready state only through
authorized resolution and new readiness evaluation.

## SkillInstallationCredentialReadiness

Tenant credential satisfaction for manifest requirements.

**Table**: `skill_installation_credentials`

**Fields**: `credential_readiness_id`, `skill_installation_id`, `tenant_id`,
`requirement_key`, `credential_kind`, `secret_reference_id`,
`secret_reference_version_id`, `delegated_credential_link_id`, `status`,
`failure_reason`, `safe_summary`, `configured_by_principal_id`,
`configured_at`, `last_checked_at`, `audit_record_id`.

**Relationships**: References existing `secret_references`, Spec 007
SecretReferenceVersion metadata, or `delegated_credential_links`. Feeds
readiness and smoke-test runner inputs.

**Validation rules**: Exactly one secret reference or delegated credential link
is supplied when required. References must belong to the tenant or allowed
global scope, be active, not revoked/expired, and satisfy manifest and policy
scope. Raw credential values are never accepted.

## SkillInstallationTest

Tenant-scoped smoke-test run evidence.

**Table**: `skill_installation_tests`

**Fields**: `skill_installation_test_id`, `skill_installation_id`,
`tenant_id`, `skill_package_version_id`, `installation_version`,
`fixture_key`, `test_run_id`, `idempotency_key`, `runner_status`,
`outcome`, `credential_readiness_summary`, `policy_decision_summary`,
`failure_reasons`, `safe_output_summary`, `evidence_artifact_id`,
`started_at`, `completed_at`, `duration_ms`, `trace_id`, `audit_record_id`.

**Relationships**: Belongs to SkillInstallation and package version; may
reference ArtifactRecord for oversized safe evidence; uses RuntimePolicyDecision
or preview summaries from Spec 007.

**Validation rules**: Test runs are tenant-scoped, idempotent by
`idempotency_key`, and can only use declared safe fixtures. Evidence cannot
store raw secrets, credential values, provider tokens, unsafe fixture payloads,
or cross-tenant content.

**State transitions**: `queued` -> `running` -> `passed`, `failed`,
`skipped`, or `errored`; retryable infrastructure failures may enqueue a new
attempt with the same idempotency key and incremented attempt metadata.

## QuarantineDecision

Safety action for package versions or tenant installations.

**Table**: `skill_quarantine_decisions`

**Fields**: `quarantine_decision_id`, `target_type`,
`skill_package_version_id`, `skill_installation_id`, `tenant_id`,
`state`, `reason_code`, `safe_reason`, `blocked_runtime_use`,
`decided_by_principal_id`, `decided_at`, `resolved_by_principal_id`,
`resolved_at`, `resolution_summary`, `audit_record_id`.

**Relationships**: Updates package/installation lifecycle projections and is
referenced by runtime eligibility, binding preview, workflow publish
validation, and audit views.

**Validation rules**: Quarantine must preserve immutable package and
installation records. Active quarantine blocks new installs, readiness
promotion, new bindings, workflow publish, and runtime use for affected
installations.

## SkillBindingEligibility

Projection that explains whether an installation can be bound.

**Fields**: `skill_installation_id`, `tenant_id`, `eligible`,
`denial_reasons`, `matched_tool_policy_version_ids`,
`matched_outbound_policy_version_ids`, `matched_credential_requirement_ids`,
`required_action_categories`, `required_tool_ids`, `manifest_digest`,
`revision_token`, `evaluated_at`.

**Relationships**: Produced by registry eligibility adapter and consumed by
Spec 007 binding creation, model_skill_config preview APIs, runtime
resolution, and workflow publish validation.

**Validation rules**: Eligibility is denied for non-ready, unauthorized,
quarantined, runtime-blocked, stale, incompatible, or missing policy/credential
installations. Successful Spec 007 binding records must pin exact
installation id, installation version, package slug/version, and manifest
digest in safe metadata.

## SkillAuditRecord

Append-only lifecycle audit event.

**Table**: `skill_audit_records`

**Fields**: `skill_audit_record_id`, `tenant_id`, `actor_principal_id`,
`actor_role`, `action`, `target_type`, `skill_package_id`,
`skill_package_version_id`, `skill_installation_id`,
`installation_version`, `affected_binding_id`, `outcome`,
`failure_category`, `safe_summary`, `redacted_metadata`, `request_id`,
`idempotency_key`, `trace_id`, `created_at`.

**Relationships**: Linked from packages, versions, grants, installations,
credential readiness, smoke tests, quarantine decisions, binding attempts, and
workflow publish validation results.

**Validation rules**: Required for package creation, validation, validation
failure, publication, tenant availability, installation, credential
configuration, smoke-test execution, readiness changes, binding attempts,
binding changes, upgrades, withdrawals, quarantine, authorization denials,
stale write rejections, and restricted-content redactions. Raw secrets,
credential values, unsafe package payloads, and cross-tenant data are
forbidden.
