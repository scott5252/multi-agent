# Data Model: Admin Workflow Studio And Registry

## Overview

The workflow studio feature adds durable workflow-authoring metadata to the
platform so admins can create drafts, validate designs, publish immutable
workflow versions, and share approved platform-scoped assets with selected
tenants. The canonical authored content is a Pydantic-first workflow document
saved as immutable revision snapshots, while PostgreSQL keeps queryable registry
metadata, revision history, validation results, and publish lineage.

Existing `Tenant`, `ArtifactRecord`, `AuditEvent`, `PrincipalIdentity`, and
authorization entities from the foundation and auth features remain in use and
are extended by the models below.

## Core Persistent Entities

### WorkflowLineage

| Field | Type | Notes |
|---|---|---|
| `workflow_lineage_id` | UUID | Primary key |
| `scope_type` | enum | `tenant`, `platform` |
| `tenant_id` | UUID nullable | Required for tenant-scoped workflows |
| `slug` | text | Stable identifier unique within scope |
| `display_name` | text | Human-readable workflow name |
| `description` | text nullable | Registry summary |
| `workflow_kind` | enum | `main_workflow`, `subworkflow` |
| `status` | enum | `drafting`, `published`, `archived` |
| `latest_published_version_id` | UUID nullable | FK to `WorkflowVersionBundle` |
| `created_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last metadata update |

**Validation rules**

- `tenant_id` is required when `scope_type = tenant`.
- `slug` must be unique within `(scope_type, tenant_id)` and normalized to
  lowercase kebab-case.
- `workflow_kind = subworkflow` is required for assets intended to be referenced
  through `subworkflow_ref`.

**Relationships**

- One lineage has zero or more draft heads over time and many published version
  bundles.

### WorkflowDraft

| Field | Type | Notes |
|---|---|---|
| `workflow_draft_id` | UUID | Primary key |
| `workflow_lineage_id` | UUID | FK to `WorkflowLineage` |
| `scope_type` | enum | `tenant`, `platform` |
| `tenant_id` | UUID nullable | Scope mirror for simpler filtering |
| `status` | enum | `active`, `published_source`, `archived`, `replaced` |
| `current_revision_number` | integer | Optimistic concurrency head |
| `latest_revision_id` | UUID | FK to `WorkflowDraftRevision` |
| `created_from_version_id` | UUID nullable | Published version used to seed the draft |
| `created_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `last_edited_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last head update |

**Validation rules**

- At most one `active` draft may exist per `workflow_lineage_id`.
- `current_revision_number` must match the highest revision stored for the draft.
- `created_from_version_id` must point to a published version from the same
  lineage or an explicitly referenceable published version when the draft is
  being forked from a platform-scoped template.

**State transitions**

- `active -> published_source`
- `active -> archived`
- `active -> replaced`

### WorkflowDraftRevision

| Field | Type | Notes |
|---|---|---|
| `workflow_draft_revision_id` | UUID | Primary key |
| `workflow_draft_id` | UUID | FK to `WorkflowDraft` |
| `revision_number` | integer | Monotonic per draft |
| `authoring_document_json` | JSONB | Serialized `WorkflowDraftDocument` |
| `document_sha256` | text | Immutable snapshot digest |
| `change_summary` | text nullable | Optional author note |
| `created_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `created_at` | timestamptz | Revision timestamp |

**Validation rules**

- `(workflow_draft_id, revision_number)` must be unique.
- `document_sha256` must match the canonical serialized document.
- Revisions are immutable once written.

### ValidationResult

| Field | Type | Notes |
|---|---|---|
| `validation_result_id` | UUID | Primary key |
| `workflow_draft_revision_id` | UUID | FK to `WorkflowDraftRevision` |
| `rule_set_version` | text | Validation ruleset digest/version |
| `status` | enum | `passed`, `failed`, `superseded` |
| `blocking_issue_count` | integer | Count of publish-blocking findings |
| `advisory_issue_count` | integer | Count of non-blocking findings |
| `findings_json` | JSONB | Summary findings grouped by category |
| `report_artifact_id` | UUID nullable | Optional FK to `ArtifactRecord` |
| `executed_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `executed_at` | timestamptz | Validation timestamp |

**Validation rules**

- Only the most recent non-superseded result for a revision may be used for
  publish eligibility.
- `status = passed` requires `blocking_issue_count = 0`.
- A validation result becomes `superseded` when a newer revision or newer
  validation of the same revision is accepted.

**State transitions**

- `passed -> superseded`
- `failed -> superseded`

### WorkflowVersionBundle

| Field | Type | Notes |
|---|---|---|
| `workflow_version_bundle_id` | UUID | Primary key |
| `workflow_lineage_id` | UUID | FK to `WorkflowLineage` |
| `scope_type` | enum | `tenant`, `platform` |
| `tenant_id` | UUID nullable | Required for tenant-scoped versions |
| `version_sequence` | integer | Monotonic publish number per lineage |
| `display_version` | text | Display label such as `v3` |
| `status` | enum | `published`, `hidden`, `retired` |
| `published_from_draft_id` | UUID | FK to `WorkflowDraft` |
| `published_from_revision_id` | UUID | FK to `WorkflowDraftRevision` |
| `validation_result_id` | UUID | FK to `ValidationResult` |
| `previous_version_bundle_id` | UUID nullable | Prior published version in lineage |
| `compiled_bundle_artifact_id` | UUID | FK to `ArtifactRecord` |
| `compiled_bundle_digest` | text | SHA-256 of canonical compiled bundle |
| `compiler_version` | text | Publish compiler version |
| `summary_json` | JSONB | Query-friendly registry summary |
| `published_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `published_at` | timestamptz | Publish timestamp |

**Validation rules**

- `(workflow_lineage_id, version_sequence)` must be unique.
- Published bundles are immutable; only `status` may change after publish.
- `compiled_bundle_digest` must match the referenced artifact content.

**State transitions**

- `published -> hidden`
- `published -> retired`
- `hidden -> published`
- `hidden -> retired`

### RegistrySharingGrant

| Field | Type | Notes |
|---|---|---|
| `registry_sharing_grant_id` | UUID | Primary key |
| `workflow_version_bundle_id` | UUID | FK to `WorkflowVersionBundle` |
| `grantee_tenant_id` | UUID | FK to `Tenant` |
| `status` | enum | `active`, `revoked` |
| `granted_by_principal_id` | UUID | FK to `PrincipalIdentity` |
| `created_at` | timestamptz | Grant timestamp |
| `revoked_at` | timestamptz nullable | Revocation timestamp |

**Validation rules**

- Only platform-scoped published versions may receive sharing grants.
- Only one active sharing grant may exist per `(workflow_version_bundle_id,
  grantee_tenant_id)`.
- Revoked grants do not alter the immutable published bundle; they only affect
  discoverability and reference eligibility.

## Canonical Nested Document Models

The entities below are persisted inside `authoring_document_json` for draft
revisions and inside the compiled bundle artifact for published versions.

### WorkflowDraftDocument

The top-level authored document.

- `workflow_key`
- `display_name`
- `description`
- `workflow_kind`
- `entry_node_key`
- `roles: list[AgentRoleDefinition]`
- `contracts: list[ContractSchemaDefinition]`
- `nodes: list[WorkflowNodeDefinition]`
- `edges: list[WorkflowEdgeDefinition]`
- `join_policies: list[JoinPolicyDefinition]`
- `approval_gates: list[ApprovalGateDefinition]`
- `subworkflow_refs: list[SubworkflowReference]`

**Validation rules**

- `entry_node_key` must reference an existing node.
- `roles`, `contracts`, `nodes`, `join_policies`, `approval_gates`, and
  `subworkflow_refs` use stable unique keys within the document.
- The authored graph must be acyclic for the initial feature.

### AgentRoleDefinition

Reusable role metadata for an agent or subagent step.

- `role_key`
- `display_name`
- `role_kind`: `agent`, `subagent`
- `purpose`
- `input_contract_key`
- `output_contract_key`
- `skill_bindings: list[SkillBinding]`
- `allowed_tool_policy_refs: tuple[str, ...]`
- `notes_markdown`

**Validation rules**

- Every role must bind to exactly one input and one output contract.
- `role_kind = subagent` may be used only for nodes that operate inside the
  current workflow, not for `subworkflow_ref` nodes.

### SkillBinding

The authored link between a role and a skill.

- `binding_key`
- `skill_slug`
- `skill_version`
- `binding_mode`: `required`, `optional`
- `purpose`
- `expected_runtime_refs`: prompt/model/tool-policy refs resolved on publish

**Validation rules**

- `skill_version` must be exact, not a range.
- The referenced skill version must exist and expose the runtime refs required
  for publish compilation.

### ContractSchemaDefinition

The schema definition for a handoff or workflow boundary.

- `contract_key`
- `display_name`
- `semantic_version`
- `schema_kind`: `workflow_input`, `workflow_output`, `handoff`, `approval`
- `json_schema`
- `example_payload`
- `compatibility_notes`

**Validation rules**

- `semantic_version` follows `major.minor.patch`.
- `json_schema` must be derived from a valid Pydantic model export.
- Breaking changes relative to the last published contract with the same
  `contract_key` must be surfaced as blocking findings when the contract is
  still referenced by pinned subworkflow or role boundaries.

### WorkflowNodeDefinition

Graph node metadata.

- `node_key`
- `node_type`: `agent_step`, `parallel_group`, `condition`, `approval_gate`,
  `subworkflow_ref`
- `display_name`
- `description`
- `role_key` nullable
- `approval_gate_key` nullable
- `subworkflow_ref_key` nullable
- `join_policy_key` nullable

**Validation rules**

- `agent_step` nodes require `role_key`.
- `approval_gate` nodes require `approval_gate_key`.
- `subworkflow_ref` nodes require `subworkflow_ref_key`.
- `parallel_group` nodes require `join_policy_key`.

### WorkflowEdgeDefinition

Directed graph edge metadata.

- `edge_key`
- `from_node_key`
- `to_node_key`
- `contract_key`
- `transition_label`

**Validation rules**

- Every edge must reference a contract key compatible with the source and target
  nodes.
- Parallel fan-out and join edges must match a declared join policy.

### SubworkflowReference

An authored dependency on a published reusable workflow.

- `subworkflow_ref_key`
- `alias`
- `target_workflow_lineage_id`
- `target_workflow_version_bundle_id`
- `input_contract_key`
- `output_contract_key`
- `sharing_grant_required`

**Validation rules**

- Only published versions may be referenced.
- Target versions must have `workflow_kind = subworkflow`.
- Platform-scoped target versions require an active `RegistrySharingGrant` when
  accessed from a tenant-scoped draft.

### JoinPolicyDefinition

Explicit merge behavior for concurrent branches.

- `join_policy_key`
- `strategy`: `all_success`, `quorum`, `first_success`, `manual_resolution`
- `required_branch_keys`
- `quorum_count` nullable
- `failure_behavior`: `fail_fast`, `wait_for_all`, `manual_resolution`

**Validation rules**

- `quorum_count` is required only for `strategy = quorum`.
- Every branch that fan-outs from the associated parallel group must be covered.
- `manual_resolution` requires at least one follow-on approval or operator path.

### ApprovalGateDefinition

Design-time schema for a human approval step.

- `approval_gate_key`
- `display_name`
- `approver_scope`: `tenant_admin`, `platform_admin`, `named_role`
- `named_role_key` nullable
- `decision_contract_key`
- `timeout_policy`: `none`, `expire`, `escalate`
- `instructions_markdown`

**Validation rules**

- `named_role_key` is required when `approver_scope = named_role`.
- `decision_contract_key` must reference an approval-kind contract.
- Approval outcomes must map to explicit outgoing transitions.

## Compiled Bundle Models

### CompiledWorkflowBundle

The immutable artifact created on publish.

- `workflow_version_bundle_id`
- `workflow_lineage_id`
- `version_sequence`
- `source_revision_sha256`
- `compiler_version`
- `graph`
- `dependency_manifest`
- `resolved_skill_runtime_refs`
- `contract_digests`
- `approval_gate_runtime_metadata`
- `join_policy_runtime_metadata`

### RunVersionBundleBlueprint

The publish-time output that future runtime work will clone into a per-run
bundle.

- `workflow_version_bundle_id`
- `compiled_bundle_digest`
- `subworkflow_version_ids`
- `contract_schema_digests`
- `skill_version_ids`
- `prompt_template_version_ids`
- `model_configuration_version_ids`
- `tool_policy_version_ids`

## Supporting Non-Persistent Models

### WorkflowDraftSummary

Registry and draft-list payload with:

- `workflow_lineage_id`
- `workflow_draft_id`
- `display_name`
- `scope_type`
- `status`
- `current_revision_number`
- `last_validated_at`
- `has_blocking_findings`

### WorkflowEditorMetadata

UI metadata served to the admin editor:

- `join_policy_options`
- `approver_scope_options`
- `field_help: list[FieldHelpDefinition]`
- `skill_catalog_options`
- `referenceable_subworkflows`

### FieldHelpDefinition

Help-modal content rendered next to every input field:

- `field_path`
- `icon_name`
- `modal_title`
- `what_this_controls`
- `why_it_matters`
- `runtime_effect`
- `example_values`

## Relationship Summary

- `WorkflowLineage 1 -> 0..N WorkflowDraft`
- `WorkflowDraft 1 -> N WorkflowDraftRevision`
- `WorkflowDraftRevision 1 -> 0..N ValidationResult`
- `WorkflowLineage 1 -> 0..N WorkflowVersionBundle`
- `WorkflowVersionBundle 1 -> 0..N RegistrySharingGrant`
- `Tenant 1 -> 0..N WorkflowLineage`
- `Tenant 1 -> 0..N WorkflowVersionBundle`
- `Tenant 1 -> 0..N RegistrySharingGrant`
- `ArtifactRecord 1 -> 0..N WorkflowVersionBundle`
- `ArtifactRecord 1 -> 0..N ValidationResult`

## Notes For Planning

- The relational model intentionally keeps authoring documents in immutable
  revision snapshots so later schema growth around nodes, contracts, and
  approval types is additive rather than migratory.
- The compiled bundle carries the future runtime’s pinned execution inputs even
  though the actual run-creation feature is out of scope here.
- Field-help metadata is modeled explicitly so the UI requirement for
  icon-triggered pop-up modal guidance remains testable and reusable across
  server-rendered pages and API consumers.
