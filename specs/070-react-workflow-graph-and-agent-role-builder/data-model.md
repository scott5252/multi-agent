# Data Model: React Workflow Graph And Agent Role Builder

## Overview

Spec 070 uses the existing `WorkflowDraftDocument` persisted by the workflow
registry. Browser state is an editable projection of that document and is not a
separate source of truth. All durable writes use the Spec 069 full-document
save contract with revision tokens and idempotency keys.

No new database tables are planned for this spec.

## Entities

### Workflow Role Editor Item

Represents an agent or sub-agent role in `document.roles`.

Fields used by the editor:

- `key`: Stable role key, unique within the workflow document.
- `display_name`: Safe user-facing label.
- `role_kind`: Agent, sub-agent, reviewer, coordinator, or other supported
  role type already accepted by workflow validation.
- `purpose`: Safe short purpose summary.
- `responsibilities`: Safe list of responsibilities.
- `input_contract_key`: Optional reference to a contract key.
- `output_contract_key`: Optional reference to a contract key.
- `prompt_profile_reference_key`: Placeholder/reference for Spec 071 binding.
- `prompt_reference_keys`: Placeholder list for Spec 071 prompt binding.
- `skill_binding_keys`: Safe references to future or existing skill bindings.

Validation rules:

- Role keys must be unique and non-empty.
- Contract references must point at existing contracts when present.
- Role deletion must not silently remove graph nodes that reference the role.
- Prompt/profile placeholders may be saved, but complete creation and readiness
  validation are deferred to Spec 071.

### Workflow Contract Editor Item

Represents reusable workflow data contracts in `document.contracts`.

Fields used by the editor:

- `key`: Stable contract key, unique within the workflow document.
- `display_name`: Safe label.
- `contract_type`: Input, output, handoff, artifact, memory, tool access,
  approval decision, failure outcome, or other supported contract category.
- `description`: Safe contract summary.
- `schema_summary`: Human-readable safe schema notes. Raw JSON schema editing is
  not required by this spec.
- `example_summary`: Optional safe example summary.

Validation rules:

- Contract keys must be unique and non-empty.
- Referenced contract keys must exist.
- Deleting a referenced contract must surface dependency warnings or backend
  validation findings before persistence succeeds.

### Graph Node Editor Item

Represents workflow topology nodes in `document.nodes`.

Fields used by the editor:

- `key`: Stable node key, unique within the workflow document.
- `node_type`: Role, join, approval, subworkflow, terminal, or other supported
  topology kind.
- `label`: Safe label.
- `role_key`: Required for role nodes.
- `join_policy_key`: Optional reference for join nodes.
- `approval_gate_key`: Optional reference for approval nodes.
- `subworkflow_reference_key`: Optional reference for subworkflow nodes.
- `is_entry`: Marks the entry node when supported by validation.
- `layout`: Safe x/y annotation used by the editor and graph preview.

Validation rules:

- Node keys must be unique and non-empty.
- Role nodes must reference existing roles.
- Join, approval, and subworkflow nodes must reference existing matching items
  when a reference is set.
- Entry node requirements remain backend-owned.

### Graph Edge Editor Item

Represents topology edges in `document.edges`.

Fields used by the editor:

- `key`: Stable edge key, unique within the workflow document.
- `source_node_key`: Existing source node key.
- `target_node_key`: Existing target node key.
- `branch_label`: Safe branch label.
- `contract_key`: Optional contract reference.
- `failure_behavior`: Safe option for retry, continue, halt, or route behavior
  supported by backend validation.

Validation rules:

- Edge keys must be unique and non-empty.
- Source and target nodes must exist.
- Contract references must exist when present.
- Unsupported branch/failure combinations are rejected by backend validation.

### Join Policy Editor Item

Represents coordination rules in `document.join_policies`.

Fields used by the editor:

- `key`: Stable join policy key.
- `display_name`: Safe label.
- `inbound_edge_keys`: Edge keys that feed the join.
- `required_behavior`: All branches, any branch, quorum, or supported equivalent.
- `quorum_count`: Required when quorum behavior is selected.
- `timeout_seconds`: Optional bounded timeout.
- `failure_behavior`: Safe failure handling option.
- `output_contract_key`: Optional merge output contract reference.

Validation rules:

- Join keys must be unique and non-empty.
- Inbound edge keys and output contract keys must exist when present.
- Quorum count must be positive and cannot exceed inbound branch count.

### Approval Gate Editor Item

Represents manual or policy approval points in `document.approval_gates`.

Fields used by the editor:

- `key`: Stable approval key.
- `display_name`: Safe label.
- `approver_scope`: Tenant, platform, role, or supported policy scope.
- `resume_behavior`: Continue, branch, halt, or supported equivalent.
- `summary`: Safe approval instructions summary.

Validation rules:

- Approval keys must be unique and non-empty.
- Approval nodes must reference existing gates when a gate reference is set.
- Approval text must pass protected-value validation.

### Subworkflow Reference Item

Represents an authorized reusable workflow reference in
`document.subworkflow_references`.

Fields used by the editor:

- `key`: Stable local reference key.
- `display_name`: Safe label.
- `workflow_key`: Authorized workflow lineage or alias.
- `version_reference`: Optional safe version reference.
- `summary`: Safe purpose summary.

Validation rules:

- Reference keys must be unique and non-empty.
- Authorization remains backend-owned; the UI must not infer cross-tenant access.

### Layout Annotation

Represents safe editor metadata in `document.editor_annotations` or node-level
layout fields.

Fields used by the editor:

- `element_key`: Role, node, edge, join, approval, or subworkflow key.
- `x`: Stable canvas x coordinate.
- `y`: Stable canvas y coordinate.
- `collapsed`: Optional section collapsed state.

Validation rules:

- Layout annotations must not change execution semantics.
- Missing annotations should not block workflow validation.

## State Transitions

1. User edits a collection item in React local state.
2. UI marks the document dirty and updates the graph preview/list projection.
3. User saves through the Spec 069 save action with current revision token and
   idempotency key.
4. Backend validates tenant scope, payload size, protected text, duplicate keys,
   graph references, stale revision, and audit behavior.
5. Successful response returns the new draft envelope and clears dirty state.
6. Validation or conflict responses render section-specific findings and keep
   the unsaved safe browser state available for correction.

## Deferred Fields

Prompt/profile creation, profile activation, test evidence creation, publish
evidence binding, and runtime launch state are intentionally deferred to Specs
071 through 073. Spec 070 may preserve safe references for these fields but
does not own their lifecycle.
