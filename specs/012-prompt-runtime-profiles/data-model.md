# Data Model: Prompt Library And Agent Runtime Profiles

## PromptLineage

Named prompt family in platform or tenant scope.

**Fields**: `prompt_lineage_id`, `scope_type`, `tenant_id`, `slug`,
`display_name`, `purpose`, `status`, `latest_draft_id`,
`latest_published_prompt_version_id`, `created_by_principal_id`,
`created_at`, `updated_at`.

**Relationships**: Has many `PromptDraft`, `PromptDraftRevision`,
`PromptVersion`, `PromptAuditRecord`, and `TenantPromptVersionGrant` records.

**Validation rules**: `tenant_id` is required for tenant scope and null for
platform scope. `slug` is unique within `(scope_type, tenant_id)`. Archived
lineages cannot create new drafts for new use.

## PromptDraft

Mutable authoring head for one prompt lineage.

**Fields**: `prompt_draft_id`, `prompt_lineage_id`, `scope_type`,
`tenant_id`, `status`, `current_revision_number`, `latest_revision_id`,
`created_from_prompt_version_id`, `last_validation_result_id`,
`created_by_principal_id`, `last_edited_by_principal_id`, `created_at`,
`updated_at`.

**Relationships**: Belongs to `PromptLineage`; has many
`PromptDraftRevision`, `PromptRenderTest`, and draft-scoped
`PromptAuditRecord` rows.

**Validation rules**: One active draft per lineage unless a future branch
workflow explicitly adds multiple draft heads. Saves require the expected
revision number. `created_from_prompt_version_id` must be visible to the actor
and must not be modified in place.

**State transitions**: `active -> published_source`; `active -> archived`;
`active -> replaced`.

## PromptDraftRevision

Immutable snapshot of editable prompt draft content.

**Fields**: `prompt_draft_revision_id`, `prompt_draft_id`,
`revision_number`, `prompt_title`, `purpose`, `usage_notes`,
`template_content`, `template_content_sha256`, `variable_declarations_json`,
`fixture_value_sets_json`, `safe_summary_json`, `created_by_principal_id`,
`created_at`.

**Relationships**: Referenced by validation results, render tests, and
published prompt versions.

**Validation rules**: `(prompt_draft_id, revision_number)` is unique.
`template_content_sha256` must match canonical template content. Fixture
values must be sanitized before storage. Revision rows are immutable.

## PromptTemplateVariable

Structured variable declaration stored in draft revisions and published prompt
versions.

**Fields**: `name`, `purpose`, `required`, `allowed_value_category`,
`safety_classification`, `sample_guidance`, `display_order`.

**Validation rules**: `name` must match `[A-Za-z_][A-Za-z0-9_]*`. Duplicate
names are invalid. Declared variables must align with placeholders in
`template_content`. Executable template constructs are invalid.

## FixtureValueSet

Sanitized sample values persisted with prompt drafts for repeatable preview.

**Fields**: `fixture_set_id`, `label`, `values_by_variable`,
`sanitization_summary`, `created_by_principal_id`, `created_at`,
`updated_at`.

**Validation rules**: Values may contain only non-sensitive fixture content
inside allowed categories. Raw secrets, credential values, unauthorized run
content, cross-tenant protected content, and oversized values are rejected
before storage or preview.

## PromptValidationResult

Result of validating a prompt draft revision.

**Fields**: `prompt_validation_result_id`, `prompt_draft_revision_id`,
`rule_set_version`, `status`, `blocking_issue_count`,
`advisory_issue_count`, `findings_json`, `template_content_sha256`,
`validated_fixture_set_ids`, `executed_by_principal_id`, `executed_at`.

**Relationships**: Used as publish evidence by `PromptVersion`.

**Validation rules**: `status = passed` requires zero blocking issues and must
match the current draft revision content digest. Validation is superseded when
a newer draft revision is saved.

## PromptRenderTest

Evidence for a safe fixture preview attempt.

**Fields**: `prompt_render_test_id`, `prompt_draft_revision_id`,
`fixture_set_id`, `viewer_principal_id`, `outcome`, `missing_variables`,
`redaction_categories`, `rendered_preview_sha256`, `safe_preview_summary`,
`created_at`.

**Validation rules**: Stores safe summary and digest only by default. Full
rendered text is not stored in audit records and is never persisted when it
contains protected or unauthorized content.

## PromptVersion

Immutable published prompt snapshot.

**Fields**: `prompt_version_id`, `prompt_lineage_id`, `scope_type`,
`tenant_id`, `version_sequence`, `display_version`, `status`,
`published_from_draft_id`, `published_from_revision_id`,
`validation_result_id`, `template_content`, `template_content_sha256`,
`variable_declarations_json`, `purpose`, `usage_notes`, `safe_summary_json`,
`published_by_principal_id`, `published_at`, `publication_reason`,
`retired_by_principal_id`, `retired_at`, `retirement_reason`.

**Relationships**: Target of Spec 007 `PromptReferenceVersion.prompt_version_id`,
runtime profile prompt references, workflow bundle pins, run pins, render
history, grants, and audit records.

**Validation rules**: Published content, variables, purpose, scope, sequence,
and validation evidence are immutable. `status = active` prompt versions can
be selected for new references if authorized. `status = retired` versions are
blocked from new references but remain visible for authorized historical
review.

**State transitions**: `active -> retired`; `retired -> historical_only`
through retention policy only.

## TenantPromptVersionGrant

Explicit platform-to-tenant visibility grant for one prompt version.

**Fields**: `tenant_prompt_version_grant_id`, `prompt_version_id`,
`grantee_tenant_id`, `status`, `granted_by_principal_id`, `created_at`,
`revoked_by_principal_id`, `revoked_at`, `reason`.

**Validation rules**: Only platform-scoped published prompt versions can be
granted. One active grant may exist per `(prompt_version_id,
grantee_tenant_id)`. Grants affect future selection and review only; they do
not mutate prompt versions or existing pins.

## AgentRuntimeProfile

Governed profile lineage for one agent or sub-agent key.

**Fields**: `agent_runtime_profile_id`, `scope_type`, `tenant_id`,
`agent_key`, `agent_kind`, `display_name`, `purpose`, `status`,
`latest_draft_id`, `active_profile_version_id`, `created_by_principal_id`,
`created_at`, `updated_at`.

**Relationships**: Has many `AgentProfileDraft`,
`AgentProfileDraftRevision`, `AgentProfileVersion`,
`TenantProfileVersionGrant`, and `PromptAuditRecord` rows.

**Validation rules**: `agent_key` is unique per `(scope_type, tenant_id,
agent_kind)` for active profile lineages. Tenant workflows resolve tenant
active profile first, then authorized platform active profile.

## AgentProfileDraft

Mutable authoring head for a runtime profile.

**Fields**: `agent_profile_draft_id`, `agent_runtime_profile_id`,
`scope_type`, `tenant_id`, `status`, `current_revision_number`,
`latest_revision_id`, `created_from_profile_version_id`,
`last_validation_result_id`, `created_by_principal_id`,
`last_edited_by_principal_id`, `created_at`, `updated_at`.

**Validation rules**: Saves require expected revision number. The source
version must be visible and authorized. Active drafts cannot activate until
their latest revision has passed validation.

## AgentProfileDraftRevision

Immutable snapshot of runtime profile authoring state.

**Fields**: `agent_profile_draft_revision_id`, `agent_profile_draft_id`,
`revision_number`, `agent_key`, `agent_kind`, `purpose`,
`prompt_references_json`, `model_routing_hints_json`,
`memory_scope_policy_json`, `skill_requirements_json`,
`tool_policy_expectations_json`, `output_contract_expectations_json`,
`test_suite_requirements_json`, `safe_summary_json`,
`created_by_principal_id`, `created_at`.

**Validation rules**: Required contract sections must be present. Referenced
prompt versions must exist, be active for new use when activating, and be
authorized for the profile scope. Revision rows are immutable.

## AgentProfileValidationResult

Validation evidence for one profile draft revision.

**Fields**: `agent_profile_validation_result_id`,
`agent_profile_draft_revision_id`, `rule_set_version`, `status`,
`blocking_issue_count`, `advisory_issue_count`, `findings_json`,
`referenced_prompt_version_ids`, `referenced_model_routing_scope_ids`,
`referenced_memory_policy_hash`, `referenced_skill_requirement_hash`,
`executed_by_principal_id`, `executed_at`.

**Validation rules**: Activation requires a non-superseded passed validation
for the current revision. Findings must identify the profile section and clear
remediation text.

## AgentProfileVersion

Immutable active runtime profile snapshot.

**Fields**: `agent_profile_version_id`, `agent_runtime_profile_id`,
`scope_type`, `tenant_id`, `agent_key`, `agent_kind`, `version_sequence`,
`display_version`, `status`, `activated_from_draft_id`,
`activated_from_revision_id`, `validation_result_id`, `purpose`,
`prompt_references_json`, `model_routing_hints_json`,
`memory_scope_policy_json`, `skill_requirements_json`,
`tool_policy_expectations_json`, `output_contract_expectations_json`,
`test_suite_requirements_json`, `safe_summary_json`,
`activated_by_principal_id`, `activated_at`, `activation_reason`,
`retired_by_principal_id`, `retired_at`, `retirement_reason`.

**Relationships**: Referenced by workflow validation, published workflow
bundle summaries, run execution bundles, dynamic first-use pins, profile
history, and audit records.

**Validation rules**: Contract fields are immutable after activation. Only one
active profile version may exist for the same `(scope_type, tenant_id,
agent_kind, agent_key)` unless a future explicit context selector is added.
Retired versions are unavailable for new workflow validation but remain
reviewable for historical pins.

**State transitions**: `active -> retired`; `retired -> historical_only`
through retention policy only.

## TenantProfileVersionGrant

Explicit platform-to-tenant visibility grant for one profile version.

**Fields**: `tenant_profile_version_grant_id`, `agent_profile_version_id`,
`grantee_tenant_id`, `status`, `granted_by_principal_id`, `created_at`,
`revoked_by_principal_id`, `revoked_at`, `reason`.

**Validation rules**: Only platform-scoped active profile versions can be
granted. One active grant may exist per `(agent_profile_version_id,
grantee_tenant_id)`. Grants do not apply to future profile versions.

## ActiveAgentProfilePointer

Fast lookup projection for profile resolution.

**Fields**: `active_agent_profile_pointer_id`, `scope_type`, `tenant_id`,
`agent_kind`, `agent_key`, `active_profile_version_id`,
`activated_by_principal_id`, `activated_at`, `activation_reason`,
`expected_previous_version_id`.

**Validation rules**: Unique per `(scope_type, tenant_id, agent_kind,
agent_key)`. Updates require the expected previous active version to prevent
conflicting activation races.

## WorkflowPromptProfilePin

Published workflow bundle or run-level pin linking workflows to exact prompt
and profile versions.

**Fields**: `workflow_prompt_profile_pin_id`, `tenant_id`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `workflow_run_id`,
`agent_key`, `agent_kind`, `step_key`, `prompt_reference_version_id`,
`prompt_version_id`, `agent_profile_version_id`, `pin_source`,
`pinned_at`, `pinned_by_principal_id`, `trace_id`, `safe_summary_json`.

**Validation rules**: Published bundle pins are created during workflow
publication or validation. Run pins are persisted at run acceptance for all
workflow-declared references. `pin_source = first_use_dynamic` is allowed only
for dynamically selected agents/sub-agents not declared upfront and must be
persisted before side effects.

## PromptAuditRecord

Append-only safe audit event for prompt and profile actions.

**Fields**: `prompt_audit_record_id`, `tenant_id`, `actor_principal_id`,
`actor_role`, `action`, `resource_kind`, `resource_id`, `affected_scope`,
`prior_version_id`, `new_version_id`, `reason`, `request_id`, `trace_id`,
`outcome`, `denial_category`, `redacted_diff_summary`, `created_at`.

**Validation rules**: Required for create, save, validate, preview, publish,
retire, activate, deactivate, grant, revoke, denied authorization, denied
selection, and failed validation attempts. Raw secret values, credential
values, full rendered prompts, unauthorized run content, and protected
cross-tenant details are forbidden.

## Indexes And Constraints

- Unique prompt lineage slugs by scope and tenant.
- Unique prompt version sequence per prompt lineage.
- Unique draft revision numbers per prompt draft.
- Unique active prompt grant per prompt version and tenant.
- Unique runtime profile key by scope, tenant, agent kind, and key.
- Unique profile version sequence per profile lineage.
- Unique active profile pointer by scope, tenant, agent kind, and key.
- Unique active profile grant per profile version and tenant.
- Indexes on tenant/status/search columns for prompt/profile list pages.
- Indexes on prompt/profile version ids used by Spec 007 references, workflow
  bundle pins, run pins, and audit history.
- Check constraints for scope/tenant consistency, lifecycle status enums,
  prompt variable JSON shape, fixture JSON object shape, and positive version
  sequences where practical.
