# Data Model: Workflow Registry React Parity

## WorkflowRegistryReactEnvelope

Represents the authorized workflow registry landing state.

Fields:

- `page_id`: Stable workflow page identifier.
- `scope`: Active React admin scope.
- `filters`: Current status, scope, kind, search, saved-filter, sort, and pagination state.
- `items`: List of `WorkflowRegistryReactItem`.
- `create_action`: Optional authorized create action.
- `legacy_routes`: Relevant `WorkflowLegacyRouteMapping` records.
- `common_state`: Optional denied, empty, unavailable, or dependency state.

Rules:

- Tenant scope is resolved by the backend before items are returned.
- Unauthorized workflow or tenant labels are omitted from denied and unavailable states.

## WorkflowRegistryReactItem

Safe workflow list entry.

Fields:

- `workflow_lineage_id`
- `workflow_draft_id`
- `workflow_version_bundle_id`
- `name`
- `workflow_kind`
- `status`
- `owner_label`
- `tenant_label`
- `updated_at_label`
- `sharing_summary`
- `required_evidence_summary`
- `actions`: Open draft, open revisions, open publish gate, open version, copy, or create from template.

Rules:

- Labels are safe summaries.
- Actions are present only when authorized.

## WorkflowCreateState

React create workflow state.

Fields:

- `metadata`: Workflow kind, starter templates, allowed scope, and field help.
- `defaults`: Safe default name, description, scope, kind, and starter template.
- `create_action`: JSON action and redirect behavior.
- `validation`: Field-level validation results.

Rules:

- Create decisions use existing workflow registry service validation.
- Failed creates return safe mutation results or problem details without Jinja.

## WorkflowDraftReactState

Extends the Spec 030 builder state for active draft editing.

Fields:

- `draft`: Safe editable workflow draft document.
- `field_help`: Safe field-help records.
- `reference_catalog`: Authorized prompt/profile/provider/model/skill/subworkflow/test-suite options.
- `graph_preview`: `WorkflowGraphParityPreview`.
- `validation`: Current validation summary.
- `publish_readiness`: Current publish gate.
- `revisions`: Revision summaries.
- `sharing`: Workflow sharing summary and authorized actions.
- `stale_conflict`: Optional stale revision conflict state.

Rules:

- Browser state never becomes the source of truth for draft revision, publish readiness, tenant scope, or sharing.
- Saves, validation, publish, copy, and restore actions include idempotency and revision information.

## WorkflowGraphParityPreview

Accessible graph review state.

Fields:

- `nodes`: Safe node summaries.
- `edges`: Safe edge summaries.
- `branch_groups`: Parallel branch and join summaries.
- `validation_links`: Finding-to-node references.
- `visual_layout`: Non-authoritative visual placement hints.
- `keyboard_lists`: Node, edge, branch, and validation list alternatives.

Rules:

- Visual layout does not define execution semantics.
- Keyboard lists must contain equivalent safe labels for graph inspection.

## WorkflowPublishGateReactState

Server-owned publish readiness and action state.

Fields:

- `decision`: blocked, ready, confirmation_required, accepted, unavailable, or stale.
- `revision`
- `validation_summary`
- `required_evidence`
- `sharing_summary`
- `blockers`
- `warnings`
- `confirmation`
- `publish_action`
- `published_bundle_summary`

Rules:

- Missing, stale, or cross-tenant test evidence blocks publish.
- Publish confirmation is explicit and backend-owned.

## WorkflowRevisionReactState

Revision and published version detail state.

Fields:

- `workflow_lineage_id`
- `workflow_draft_id`
- `workflow_version_bundle_id`
- `current_revision`
- `revision_history`
- `published_detail`
- `rollback_references`
- `safe_artifacts`
- `actions`

Rules:

- Published version details are immutable summaries.
- Raw workflow documents, prompts, completions, credentials, memory contents, and tool payloads are not rendered.

## WorkflowLegacyRouteMapping

Maps an old workflow browser URL to its React or compatibility behavior.

Fields:

- `legacy_path`
- `methods`
- `react_path`
- `preserved_parameters`
- `redirect_status`
- `compatibility_response`
- `authorization_behavior`
- `inventory_item_id`
- `evidence_references`
- `retirement_outcome`: deleted, redirected, converted, retained_with_blocker, or outside_scope.

Rules:

- Redirects preserve tenant id, workflow ids, draft ids, revision ids, filters, saved-filter intent, anchors, and safe breadcrumbs only when authorized and unambiguous.
- Unsafe, missing, or unauthorized mappings return non-Jinja safe problem responses.

## WorkflowRetirementEvidence

Reviewer-facing deletion record for workflow-owned surfaces.

Fields:

- `item_type`: template, include, route, form action, helper, static asset, docs link, or test evidence.
- `path_or_route`
- `outcome`
- `proof`
- `blocker`
- `rollback_note`
- `planned_owner`

Rules:

- A workflow template or asset cannot be deleted without route tests, scanner proof, and QA evidence.
- Shared or non-workflow dependencies are retained with blockers for later specs.
