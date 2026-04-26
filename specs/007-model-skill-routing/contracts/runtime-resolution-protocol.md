# Contract: Runtime Configuration Resolution Protocol

This protocol defines how runtime orchestration calls the configuration
subsystem before accepting a run, before invoking a model-backed step, and
before any skill/tool/domain/credential side effect.

## Run Acceptance Pinning

**Caller**: `multi_agent_platform.runtime.orchestration.service`

**Operation**: `ConfigurationService.pin_run_configuration(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `run_bundle_id`
- `bundle_digest`
- `workflow_lineage_id`
- `workflow_version_bundle_id`
- `initiating_principal_id`
- `trace_id`

**Response fields**:

- `resolved_execution_configuration_id`
- `resolution_digest`
- `model_routing_version_ids`
- `prompt_reference_version_ids`
- `skill_binding_version_ids`
- `allowed_tool_policy_version_ids`
- `outbound_domain_policy_version_ids`
- `secret_reference_version_ids`
- `credential_requirement_version_ids`
- `warnings`

**Rules**:

- The response must be persisted in the same acceptance flow that creates or
  links the runtime execution bundle.
- The resolver validates that a tenant global default exists when any
  model-backed path may require fallback.
- The resolver validates all statically knowable model, prompt, skill, tool,
  outbound, secret-reference, and credential configuration before the run is
  eligible for workers.
- Failure returns a stable safe category and no run worker side effect starts.

## Model Step First Use

**Operation**: `ConfigurationService.resolve_model_step(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `run_step_id`
- `run_bundle_id`
- `resolved_execution_configuration_id`
- `workflow_lineage_id`
- `workflow_version_bundle_id`
- `agent_key`
- `step_key`
- `trace_id`
- `idempotency_key`

**Response fields**:

- `runtime_policy_decision_id`
- `outcome`
- `model_provider_key`
- `model_id`
- `model_routing_version_id`
- `model_source_scope`
- `prompt_reference_version_id`
- `prompt_id`
- `prompt_version_id`
- `prompt_digest`
- `evaluated_version_ids`
- `safe_reason`

**Rules**:

- Model precedence is step, agent, workflow, tenant default.
- Prompt precedence is step, agent, workflow only.
- The decision row is inserted before the model provider is called.
- Repeated calls for the same run, step, and idempotency key return the first
  persisted decision.

## Skill Access First Use

**Operation**: `ConfigurationService.evaluate_skill_access(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `run_step_id`
- `resolved_execution_configuration_id`
- `agent_key`
- `skill_slug`
- `skill_version`
- `use_context`
- `trace_id`

**Response fields**:

- `runtime_policy_decision_id`
- `outcome`
- `evaluated_skill_binding_version_ids`
- `winning_skill_binding_version_ids`
- `denial_category`
- `safe_reason`

**Rules**:

- Missing explicit binding denies the skill.
- Every applicable active binding constraint must allow the use context.
- Denials are persisted before skill execution.

## Tool Use First Use

**Operation**: `ConfigurationService.evaluate_tool_use(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `run_step_id`
- `resolved_execution_configuration_id`
- `agent_key`
- `step_key`
- `skill_slug`
- `tool_id`
- `action_category`
- `destination_url`
- `credential_context`
- `trace_id`
- `idempotency_key`

**Response fields**:

- `runtime_policy_decision_id`
- `outcome`
- `evaluated_tool_policy_version_ids`
- `evaluated_outbound_domain_policy_version_ids`
- `evaluated_credential_requirement_version_ids`
- `evaluated_secret_reference_version_ids`
- `authorized_secret_reference_ids`
- `authorized_delegated_credential_link_ids`
- `denial_category`
- `safe_reason`

**Rules**:

- Tool use is denied unless every applicable tool policy allows the tool and
  action category.
- Network-capable tool use is denied unless every applicable outbound policy
  allows the normalized destination.
- Credentialed tool use is denied unless every applicable credential
  requirement is satisfied by an active authorized secret reference or
  delegated credential.
- Authorized secret references are ids only. Raw secret values are resolved by
  the runtime secret provider after the allow decision is persisted.
- Denied decisions must not trigger DNS, HTTP, model, or external tool calls.

## Resume Behavior

Runtime resume must pass the original `resolved_execution_configuration_id`.
The configuration service evaluates unused decisions against the pinned
candidate set for that run. Previously persisted decisions are reused. Latest
active configuration is ignored for that run unless a
RunConfigurationMigrationRecord exists and has passed authorization and
compatibility checks.

## Error Categories

- `missing_global_default`
- `invalid_model_reference`
- `missing_prompt_version`
- `skill_not_bound`
- `tool_denied`
- `domain_denied`
- `credential_unsatisfied`
- `secret_reference_invalid`
- `resolution_conflict`
- `authorization_failed`
- `stale_configuration`

All errors include safe identifiers, trace id, and a remediation hint when
available. Errors never include raw prompts, raw secrets, credential values,
provider tokens, or unauthorized run content.
