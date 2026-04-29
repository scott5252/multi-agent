# Data Model: Guided Admin Workflow Builder

## Overview

The workflow builder extends the existing workflow registry data model. The
existing persistent entities remain authoritative:

- `WorkflowLineage`
- `WorkflowDraft`
- `WorkflowDraftRevision`
- `ValidationResult`
- `WorkflowVersionBundle`
- `RegistrySharingGrant`
- `ArtifactRecord`
- `AuditEvent`

This feature adds richer nested document models, editor metadata, graph preview
projections, validation finding locations, reference readiness snapshots, and
publish gate results. Additive database columns or tables are only required if
validation reports or publish gate evidence outgrow the current
`ValidationResult.findings_json` and `WorkflowVersionBundle.summary_json`
capacity; the default design stores compact safe summaries in existing JSON
fields and large reports in artifact storage.

## Persistent Entities

### WorkflowDraftRevision

Existing entity. The builder stores the extended authoring document in
`authoring_document_json`.

Additional rules:

- The document must validate as `WorkflowBuilderDocument`.
- `document_sha256` is computed from canonical JSON including builder sections.
- Revisions are immutable; restore creates a new revision.
- Save, restore, and copy operations require current `base_revision_number`.

### ValidationResult

Existing entity. Builder validation stores `BuilderValidationFinding` records
inside `findings_json`.

Additional fields in `findings_json`:

- `rule_set_version`
- `draft_revision_id`
- `reference_snapshot_digest`
- `publish_blocking`
- `findings: list[BuilderValidationFinding]`
- `reference_readiness: list[ReferenceReadinessSnapshot]`
- `graph_summary`
- `required_test_summary`

Validation results become superseded when a newer draft revision is saved or a
new validation result replaces them for the same revision.

### WorkflowVersionBundle

Existing entity. Builder publication writes additional safe summaries to
`summary_json`:

- `source_draft_revision_id`
- `source_document_sha256`
- `prompt_profile_pins`
- `model_routing_provenance`
- `provider_catalog_pins`
- `skill_installation_pins`
- `subworkflow_bundle_pins`
- `contract_compatibility`
- `approval_gate_summary`
- `graph_preview_summary`
- `required_test_evidence`
- `publish_gate_id`
- `publish_gate_digest`

Published bundle records remain immutable except status transitions already
allowed by the registry model.

## Canonical Builder Document

### WorkflowBuilderDocument

The top-level document saved in each draft revision.

Fields:

- `workflow_key`
- `display_name`
- `description`
- `workflow_kind`
- `metadata: WorkflowBuilderMetadata`
- `entry_node_key`
- `roles: list[WorkflowRoleDefinition]`
- `prompt_profile_references: list[PromptProfileReference]`
- `skill_installations: list[SkillInstallationReference]`
- `contracts: list[WorkflowContractDefinition]`
- `nodes: list[GraphNodeDefinition]`
- `edges: list[GraphEdgeDefinition]`
- `join_policies: list[JoinPolicyDefinition]`
- `approval_gates: list[ApprovalGateDefinition]`
- `subworkflow_refs: list[ReusableSubworkflowReference]`
- `test_requirements: list[TestSuiteRequirement]`
- `editor_annotations: BuilderEditorAnnotations`

Validation rules:

- Keys are unique within each section.
- `entry_node_key` references an existing node.
- Tenant-scoped documents require tenant scope and tenant-owned or granted
  references.
- Platform-scoped documents cannot embed tenant-only references unless policy
  explicitly allows a reusable platform template placeholder.
- Raw secrets, credential values, provider tokens, unsafe prompts, and rendered
  prompt previews are forbidden.

### WorkflowBuilderMetadata

Fields:

- `name`
- `description`
- `owner_principal_id`
- `scope_type`
- `tenant_id`
- `status`
- `tags`
- `publication_intent`
- `reviewer_notes`

Validation rules:

- `tenant_id` is required for tenant scope and omitted for platform scope.
- `publication_intent` identifies whether the draft is intended for immediate
  publish, template review, subworkflow reuse, or migration.
- Tags are safe, bounded strings.

### WorkflowRoleDefinition

Represents a primary agent or sub-agent role.

Fields:

- `role_key`
- `display_name`
- `role_kind`: `agent` or `subagent`
- `purpose`
- `responsibilities`
- `allowed_references`
- `profile_reference_key`
- `prompt_reference_keys`
- `input_contract_key`
- `output_contract_key`
- `skill_installation_keys`
- `handoff_expectations`
- `graph_node_keys`
- `review_notes`

Validation rules:

- Every graph role node references exactly one role.
- Every role selected for publish must resolve to an active authorized runtime
  profile version.
- Prompt/profile references must be publish-ready before publication.
- Role contracts must exist and match edge or subworkflow contracts.

### PromptProfileReference

Connects a role or graph node to prompt/profile governance.

Fields:

- `reference_key`
- `role_key`
- `agent_key`
- `agent_kind`
- `agent_profile_version_id`
- `prompt_reference_version_ids`
- `prompt_version_ids`
- `source_scope`
- `resolution_digest`
- `model_routing_preview: ModelRoutingPreviewReference`
- `readiness_status`

Validation rules:

- Active tenant-scoped profile wins over granted platform profile when both
  match.
- Referenced prompt versions must be active, authorized, digest-compatible, and
  visible for the workflow scope.
- Runtime profile model routing hints must not bypass model-skill routing
  authorization.

### ModelRoutingPreviewReference

Safe link or snapshot for expected model routing.

Fields:

- `preview_key`
- `scope`
- `model_routing_version_id`
- `provider_connection_id`
- `provider_catalog_entry_id`
- `model_id`
- `health_state`
- `policy_status`
- `preview_url`
- `evaluated_version_ids`
- `safe_summary`

Validation rules:

- Preview must resolve through `model_skill_config`.
- Provider catalog entry must be tenant-visible, active, and health-policy
  compatible.
- Preview summaries must not include raw prompts, provider responses, or
  credentials.

### SkillInstallationReference

Required skill dependency for a role, node, or workflow.

Fields:

- `skill_installation_key`
- `skill_slug`
- `skill_version`
- `scope_type`
- `tenant_id`
- `binding_mode`
- `compatibility_expectation`
- `credential_requirement_status`
- `policy_notes`
- `tool_policy_refs`
- `outbound_policy_refs`
- `secret_reference_ids`

Validation rules:

- Required skills must be exact-versioned, installed or bound in the
  authorized scope, and active for the workflow use context.
- Credential readiness checks use secret-reference metadata only.
- Secret values and delegated credential material are never stored.

### WorkflowContractDefinition

Extends existing contract definitions.

Fields:

- `contract_key`
- `display_name`
- `semantic_version`
- `contract_kind`: `workflow_input`, `workflow_output`, `handoff`, `artifact`,
  `memory`, `tool_access`, `approval_decision`, `failure_outcome`
- `json_schema`
- `example_payload`
- `compatibility_notes`
- `producer_keys`
- `consumer_keys`

Validation rules:

- `semantic_version` follows `major.minor.patch`.
- Referenced contracts must exist for roles, edges, joins, approvals, and
  subworkflows.
- Breaking changes against the latest published bundle or selected
  subworkflow contracts are blocking when they affect active boundaries.

### GraphNodeDefinition

Fields:

- `node_key`
- `node_type`: `agent`, `subagent`, `approval_gate`, `subworkflow_call`,
  `skill_action`, `validation_checkpoint`, `join`, `terminal`
- `display_name`
- `description`
- `role_key`
- `approval_gate_key`
- `subworkflow_ref_key`
- `skill_installation_key`
- `join_policy_key`
- `input_contract_key`
- `output_contract_key`
- `position`
- `retry_policy`
- `timeout_policy`

Validation rules:

- Node-specific reference fields must match `node_type`.
- Terminal nodes have no outgoing success edge.
- Approval and retry loop nodes must define bounded resume/attempt behavior.

### GraphEdgeDefinition

Fields:

- `edge_key`
- `source_node_key`
- `target_node_key`
- `edge_type`: `sequence`, `branch`, `handoff`, `approval_resume`,
  `failure_path`, `retry`
- `condition`
- `contract_key`
- `failure_behavior`
- `loop_bound`
- `label`

Validation rules:

- Source and target nodes must exist.
- Contract keys must be compatible with source output and target input.
- Retry and approval-resume edges must include loop bounds and exits.
- Arbitrary cycles are blocking.

### JoinPolicyDefinition

Fields:

- `join_policy_key`
- `strategy`: `all_success`, `quorum`, `first_success`, `manual_resolution`
- `required_inbound_edge_keys`
- `quorum_count`
- `failure_behavior`
- `timeout_policy`
- `output_merge_contract_key`
- `merge_notes`

Validation rules:

- Required inbound edges must target the join node.
- Quorum count is required only for `quorum` and cannot exceed inbound count.
- Output merge contract is required when downstream edges consume merged data.

### ApprovalGateDefinition

Fields:

- `approval_gate_key`
- `display_name`
- `approver_scope`
- `approver_role_code`
- `reason`
- `decision_contract_key`
- `resume_behavior`
- `timeout_policy`
- `blocked_state_visibility`
- `instructions`

Validation rules:

- Named-role approvals require `approver_role_code`.
- Decision contract must exist when configured.
- Resume behavior is required for publish.
- Timeout and blocked-state visibility are required for durable wait-state
  review.

### ReusableSubworkflowReference

Fields:

- `subworkflow_ref_key`
- `alias`
- `workflow_lineage_id`
- `workflow_version_bundle_id`
- `display_version`
- `scope_type`
- `tenant_id`
- `input_contract_key`
- `output_contract_key`
- `compatibility_status`
- `selected_at_validation_result_id`

Validation rules:

- References must point to exact visible published subworkflow bundle versions.
- Tenant admins may reference platform subworkflows only through grants.
- Publish pins the selected `workflow_version_bundle_id`.
- Input/output contracts must be compatible with parent graph contracts.

### TestSuiteRequirement

Fields:

- `test_requirement_key`
- `suite_id`
- `required_status`
- `target_type`: `workflow_draft_revision`, `agent_profile_version`,
  `subworkflow_bundle`
- `target_reference_key`
- `freshness_policy`
- `latest_result_id`
- `latest_result_status`
- `executed_at`
- `safe_summary`

Validation rules:

- Required tests block publication when missing, failing, or stale relative to
  the current draft revision or selected profile/subworkflow version.
- Result summaries must be safe and must not include prompt or provider
  payloads.

## Editor And Validation Projections

### WorkflowEditorMetadata

Fields:

- `section_order`
- `sections`
- `field_help`
- `field_definitions`
- `lookup_sources`
- `graph_node_types`
- `graph_edge_types`
- `validation_code_mapping`
- `capabilities`
- `action_urls`

Validation rules:

- Metadata is filtered by principal, scope, and tenant.
- Unauthorized lookup links are omitted rather than rendered disabled with
  protected identifiers.

### GraphPreview

Fields:

- `draft_revision_id`
- `document_sha256`
- `nodes: list[GraphPreviewNode]`
- `edges: list[GraphPreviewEdge]`
- `entry_node_key`
- `terminal_node_keys`
- `cycle_summaries`
- `validation_badges`
- `layout_hints`

Validation rules:

- Preview is derived from the server-validated draft document.
- Graph element ids map back to canonical builder field paths.

### BuilderValidationFinding

Fields:

- `finding_id`
- `category`
- `code`
- `severity`: `blocking`, `advisory`, `info`
- `blocking`
- `message`
- `remediation`
- `section_key`
- `field_path`
- `graph_element_id`
- `reference_type`
- `reference_id`
- `authorized_link`
- `safe_context`

Validation rules:

- Blocking findings prevent publish.
- Links are present only when the current actor may view the target.
- Safe context excludes secrets, prompts, provider payloads, and unauthorized
  identifiers.

### ReferenceReadinessSnapshot

Fields:

- `reference_key`
- `reference_type`: `prompt`, `profile`, `model_route`, `provider_catalog`,
  `skill`, `subworkflow`, `contract`, `approval_role`, `test_suite`
- `reference_id`
- `status`: `ready`, `missing`, `retired`, `unauthorized`,
  `unhealthy`, `incompatible`, `stale`, `failing`
- `blocking`
- `validated_at`
- `source_service`
- `safe_summary`
- `pin_payload`

Validation rules:

- Snapshots are evidence, not authority; publish gate re-checks readiness.
- `pin_payload` includes only ids, digests, versions, and safe provenance.

### PublishGateResult

Fields:

- `publish_gate_id`
- `workflow_draft_id`
- `workflow_draft_revision_id`
- `document_sha256`
- `validation_result_id`
- `status`: `ready`, `blocked`, `stale`, `unauthorized`
- `blocking_issue_count`
- `advisory_issue_count`
- `findings`
- `reference_readiness`
- `pin_summary`
- `required_test_summary`
- `expires_at`
- `created_by_principal_id`
- `created_at`
- `digest`

Validation rules:

- Ready status requires current revision, passing validation, no blocking
  findings, and fresh reference/test readiness.
- Publish accepts only a current, unexpired gate or re-runs the gate before
  bundle creation.
- Stale gates cannot publish.

## State Transitions

### Draft Lifecycle

```text
active -> active                    # save creates new revision
active -> published_source          # successful publish
active -> archived                  # explicit archive
active -> replaced                  # copy/restore into another lineage if needed
published_source -> archived
```

### Validation Lifecycle

```text
passed -> superseded
failed -> superseded
```

### Publish Gate Lifecycle

```text
ready -> consumed
ready -> stale
blocked -> superseded
stale -> superseded
unauthorized -> superseded
```

Gate lifecycle may be represented inside validation/audit records until a
dedicated table is warranted.
