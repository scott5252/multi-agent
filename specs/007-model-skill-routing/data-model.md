# Data Model: Model Routing And Skill Configuration

## ModelProviderCatalogEntry

Represents a model provider and model that may be referenced by routing
configuration.

**Fields**: `model_provider_entry_id`, `tenant_id`, `provider_key`,
`model_id`, `display_name`, `capabilities`, `cost_metadata`, `status`,
`created_at`, `updated_at`, `retired_at`.

**Relationships**: Referenced by ModelRoutingVersion records.

**Validation rules**: `provider_key` and `model_id` are unique per tenant when
tenant-scoped, or global when `tenant_id` is null. Active routing can reference
only entries with `status = active` and allowed tenant availability.

## ModelRoutingVersion

Immutable configuration version that selects an LLM for a tenant default,
workflow, agent, or step scope.

**Fields**: `model_routing_version_id`, `tenant_id`, `scope_type`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `agent_key`, `step_key`,
`model_provider_entry_id`, `routing_parameters`, `status`,
`version_sequence`, `previous_version_id`, `created_by_principal_id`,
`created_at`, `activation_reason`, `effective_from`, `effective_until`,
`redacted_summary`.

**Relationships**: Points to ModelProviderCatalogEntry; may be referenced by
ActiveConfigurationPointer, ResolvedExecutionConfiguration, and
RuntimePolicyDecision.

**Validation rules**: Tenant default versions must not include workflow,
agent, or step selectors. Step versions must include `step_key`. Agent
versions must include `agent_key`. Active singleton uniqueness applies per
tenant and exact scope.

**State transitions**: `draft` -> `active`; `active` -> `inactive`;
`active` -> `rolled_back_from`; any state -> `archived` only through retention
policy. Existing version payloads are immutable.

## PromptReferenceVersion

Immutable reference to a prompt version usable by a workflow, agent, or step.

**Fields**: `prompt_reference_version_id`, `tenant_id`, `scope_type`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `agent_key`, `step_key`,
`prompt_id`, `prompt_version_id`, `prompt_digest`, `status`,
`version_sequence`, `previous_version_id`, `created_by_principal_id`,
`created_at`, `activation_reason`, `redacted_summary`.

**Relationships**: Referenced by ResolvedExecutionConfiguration and
RuntimePolicyDecision.

**Validation rules**: Prompt resolution uses step, agent, then workflow only.
Tenant-global prompt references are invalid. Active prompt references must
point to immutable prompt versions visible to the tenant.

## SkillBindingVersion

Immutable authorization for an agent or scope to use a specific skill.

**Fields**: `skill_binding_version_id`, `tenant_id`, `workflow_lineage_id`,
`workflow_version_bundle_id`, `agent_key`, `skill_slug`, `skill_version`,
`allowed_contexts`, `runtime_ref_constraints`, `status`, `version_sequence`,
`previous_version_id`, `created_by_principal_id`, `created_at`,
`activation_reason`, `redacted_summary`.

**Relationships**: Evaluated by RuntimePolicyDecision for skill access and
referenced by ResolvedExecutionConfiguration.

**Validation rules**: Skill version must be exact, active, and visible to the
tenant. Runtime reference constraints cannot contain raw secrets or credential
values. Missing binding denies skill access.

## AllowedToolPolicyVersion

Immutable policy defining which tools and operation categories are allowed.

**Fields**: `allowed_tool_policy_version_id`, `tenant_id`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `agent_key`, `step_key`,
`skill_slug`, `tool_id`, `allowed_action_categories`, `constraints`,
`status`, `version_sequence`, `previous_version_id`,
`created_by_principal_id`, `created_at`, `activation_reason`,
`redacted_summary`.

**Relationships**: Evaluated with SkillBindingVersion, OutboundDomainPolicy,
ToolCredentialRequirementVersion, and SecretReferenceVersion during tool use.

**Validation rules**: Tool use is denied unless every applicable active tool
policy allows the requested tool and action category. Unknown tools or action
categories are invalid at activation.

## OutboundDomainPolicyVersion

Immutable policy controlling network destinations for network-capable tools.

**Fields**: `outbound_domain_policy_version_id`, `tenant_id`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `agent_key`, `step_key`,
`tool_id`, `action_category`, `allowed_domain_patterns`, `allowed_schemes`,
`allowed_ports`, `status`, `version_sequence`, `previous_version_id`,
`created_by_principal_id`, `created_at`, `activation_reason`,
`redacted_summary`.

**Relationships**: Evaluated during network-capable tool decisions and stored
in RuntimePolicyDecision.

**Validation rules**: Hosts are lowercase and IDNA-normalized before matching.
Malformed hosts, embedded credentials, ambiguous wildcards, missing policies,
and destinations outside any applicable policy are denied.

## SecretReferenceVersion

Versioned metadata pointer to secret material stored outside workflow,
configuration, provenance, logs, and audits.

**Fields**: `secret_reference_version_id`, `tenant_id`,
`secret_reference_id`, `provider_key`, `external_reference`, `allowed_scopes`,
`status`, `version_sequence`, `previous_version_id`,
`created_by_principal_id`, `created_at`, `activation_reason`,
`rotation_metadata`, `redacted_summary`.

**Relationships**: Referenced by ToolCredentialRequirementVersion and runtime
credential decisions. May wrap existing `secret_references` rows for versioned
audit behavior.

**Validation rules**: Raw secret values are forbidden. External references and
provider keys are safe metadata only. Inactive, revoked, expired, or
cross-tenant references cannot satisfy credential requirements.

## ToolCredentialRequirementVersion

Immutable requirement describing credentials needed for a tool or action.

**Fields**: `tool_credential_requirement_version_id`, `tenant_id`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `agent_key`, `step_key`,
`tool_id`, `action_category`, `credential_kind`, `secret_reference_version_id`,
`delegated_credential_link_id`, `allowed_credential_scope`, `expiry_policy`,
`status`, `version_sequence`, `previous_version_id`,
`created_by_principal_id`, `created_at`, `activation_reason`,
`redacted_summary`.

**Relationships**: References SecretReferenceVersion or delegated credential
metadata. Evaluated by RuntimePolicyDecision before credentialed tool use.

**Validation rules**: Credentialed tool use is denied when a required
reference is missing, inactive, expired, revoked, unauthorized, outside scope,
or disallowed by any applicable active requirement.

## ActiveConfigurationPointer

Fast lookup projection for the active version of a configuration kind and
scope.

**Fields**: `active_configuration_pointer_id`, `tenant_id`, `config_kind`,
`scope_hash`, `scope_selectors`, `active_version_id`, `activated_by_principal_id`,
`activated_at`, `activation_reason`, `expected_previous_version_id`.

**Relationships**: Points to one immutable configuration version. Rebuilt from
ConfigurationAuditRecord and version history if needed.

**Validation rules**: Unique per tenant, config kind, and scope hash. Updates
require expected active version for conflict detection.

## ResolvedExecutionConfiguration

Pinned run-level configuration snapshot created at run acceptance.

**Fields**: `resolved_execution_configuration_id`, `tenant_id`,
`workflow_run_id`, `run_bundle_id`, `bundle_digest`,
`workflow_version_bundle_id`, `accepted_at`, `resolved_by_principal_id`,
`model_routing_version_ids`, `prompt_reference_version_ids`,
`skill_binding_version_ids`, `allowed_tool_policy_version_ids`,
`outbound_domain_policy_version_ids`, `secret_reference_version_ids`,
`credential_requirement_version_ids`, `resolution_digest`, `trace_id`,
`redacted_summary`.

**Relationships**: Linked to runtime execution bundle and workflow run; owns
many RuntimePolicyDecision records.

**Validation rules**: Must be persisted before a run is accepted for worker
execution. Digest is stable for deterministic tests and replay evidence.

## RuntimePolicyDecision

Durable allow or deny outcome for a model, prompt, skill, tool, domain,
secret-reference, or credential decision.

**Fields**: `runtime_policy_decision_id`, `tenant_id`, `workflow_run_id`,
`run_step_id`, `run_bundle_id`, `agent_key`, `step_key`, `decision_category`,
`requested_resource`, `requested_action`, `destination_host`,
`outcome`, `denial_category`, `safe_reason`, `evaluated_version_ids`,
`winning_version_ids`, `source_scopes`, `idempotency_key`, `trace_id`,
`created_at`, `redacted_metadata`.

**Relationships**: References ResolvedExecutionConfiguration and the runtime
run/step that used the decision.

**Validation rules**: Persisted before model or external tool side effects.
Payloads must not contain raw prompts, raw secrets, credential values, or
unauthorized run content.

## ConfigurationAuditRecord

Append-only audit event for configuration and activation changes.

**Fields**: `configuration_audit_record_id`, `tenant_id`,
`actor_principal_id`, `actor_role`, `action`, `config_kind`, `affected_scope`,
`prior_version_id`, `new_version_id`, `reason`, `request_id`, `trace_id`,
`redacted_diff_summary`, `created_at`.

**Relationships**: Linked from configuration history views and rollback
records.

**Validation rules**: Required for create, activate, deactivate, rollback,
migration, failed authorization, and failed validation attempts. Raw secrets,
credential values, and full prompt text are forbidden.

## ConfigurationRollbackRecord

Evidence that a prior immutable version was reactivated.

**Fields**: `configuration_rollback_record_id`, `tenant_id`, `config_kind`,
`scope_hash`, `from_version_id`, `to_version_id`, `actor_principal_id`,
`reason`, `configuration_audit_record_id`, `created_at`.

**Relationships**: References ActiveConfigurationPointer and
ConfigurationAuditRecord.

**Validation rules**: `to_version_id` must belong to the same tenant,
config kind, and scope as `from_version_id`. Rollback changes future active
resolution only.

## RunConfigurationMigrationRecord

Explicit audited migration for in-flight runs that need new pinned
configuration after acceptance.

**Fields**: `run_configuration_migration_record_id`, `tenant_id`,
`workflow_run_id`, `from_resolution_digest`, `to_resolution_digest`,
`old_version_ids`, `new_version_ids`, `compatibility_status`,
`approval_record_id`, `actor_principal_id`, `reason`, `created_at`,
`trace_id`, `redacted_summary`.

**Relationships**: Linked to ResolvedExecutionConfiguration and runtime
approval records when approval is required.

**Validation rules**: Cannot mutate historical decisions already used by
completed model/tool attempts. Requires authorization, reason, and durable
audit record.
