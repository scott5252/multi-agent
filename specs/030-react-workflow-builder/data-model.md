# Data Model: React Workflow Builder

## WorkflowBuilderBootstrap

Represents the authorized builder page envelope.

Fields:

- `page_id`: Stable page identifier.
- `title`: Safe page title.
- `description`: Safe page summary.
- `scope`: Active `ReactAdminScope`.
- `shell`: Optional `ReactAdminShellState`.
- `draft`: `WorkflowDraftDocument`.
- `sections`: Ordered builder sections and completion state.
- `field_help`: Safe field help records.
- `reference_catalog`: `WorkflowReferenceCatalog`.
- `graph_preview`: `WorkflowGraphPreview`.
- `validation`: `WorkflowValidationSummary`.
- `publish_readiness`: `WorkflowPublishReadiness`.
- `revisions`: List of `WorkflowRevisionSummary`.
- `actions`: Save, validate, publish, and export/review actions.
- `json_inspector`: Collapsed read-only `WorkflowJsonInspector`.

Safety:

- All display text is sanitized.
- Raw workflow JSON is not rendered directly.
- Tenant labels are restricted to authorized scope.

## WorkflowDraftDocument

Safe editable representation of a workflow draft.

Fields:

- `workflow_draft_id`: Draft identifier.
- `workflow_lineage_id`: Workflow lineage identifier.
- `tenant_id`: Tenant identifier when scoped to tenant.
- `revision`: Current revision token.
- `name`: Safe workflow name.
- `description`: Safe workflow description.
- `status`: Draft, validating, ready, blocked, stale, or published.
- `metadata`: Owner, tags, Daily Briefing pattern flag, and safe category labels.
- `roles`: Primary agent and sub-agent role descriptors.
- `references`: Prompt, profile, provider route, model, skill, connector, and subworkflow references.
- `graph`: Semantic node and edge summaries.
- `approval_gates`: Gate descriptors.
- `required_tests`: Required test suite references.

Validation:

- Names and descriptions use safe text validators.
- Revision is required for save and publish.
- Tenant ID must match active scope.

## WorkflowReferenceCatalog

Backend-owned lookup data for reference pickers.

Fields:

- `prompt_options`
- `profile_options`
- `provider_options`
- `model_options`
- `skill_options`
- `tool_options`
- `subworkflow_options`
- `test_suite_options`

Each option includes:

- `reference_id`
- `label`
- `kind`
- `readiness_status`
- `tenant_eligible`
- `version_label`
- `safe_summary`
- `href`

Safety:

- No raw prompt text, provider authorization, credential value, or tool payload appears.
- Unavailable or unauthorized references are summarized without leaking raw reasons.

## WorkflowGraphPreview

Non-authoritative visual graph model.

Fields:

- `nodes`: Node summaries with visual positions, labels, type, status, and section links.
- `edges`: Edge summaries with source, target, label, and condition category.
- `branches`: Parallel fan-out and branch grouping summaries.
- `join_policies`: Join policy summaries.
- `approval_gates`: Approval gate summaries.
- `accessibility_lists`: Keyboard-friendly node and edge list equivalents.
- `layout_revision`: Visual layout token.

Rules:

- Layout positions do not define execution semantics.
- Backend validation owns semantic graph validity.
- Node and edge list data must be equivalent to the canvas labels.

## WorkflowValidationSummary

Backend validation state for the active draft.

Fields:

- `validation_id`
- `status`: pending, running, passed, warning, blocked, unavailable, stale.
- `revision`
- `generated_at_label`
- `summary`
- `findings`
- `safe_artifact_references`
- `refresh_action`

`ValidationFinding` fields:

- `finding_id`
- `severity`
- `category`
- `section`
- `message`
- `recommended_action`
- `href`
- `evidence_reference_id`

Safety:

- Findings contain safe categories and summaries only.
- No stack trace or raw external payload appears.

## WorkflowPublishReadiness

Publish gate state for the active draft.

Fields:

- `decision`: blocked, ready, confirmation_required, accepted, unavailable.
- `revision`
- `summary`
- `blockers`
- `warnings`
- `required_evidence`
- `reference_readiness`
- `validation_freshness`
- `confirmation`
- `publish_action`
- `published_bundle_summary`

Rules:

- Missing/stale required test evidence blocks publish.
- Stale draft revision blocks publish.
- Publish action requires explicit confirmation.
- Published bundle summary is immutable and safe.

## WorkflowRevisionSummary

Safe revision history record.

Fields:

- `revision`
- `created_at_label`
- `actor_label`
- `change_category`
- `summary`
- `audit_reference_id`
- `compare_href`
- `current`

Safety:

- Actor labels are safe summaries.
- Change summaries do not include raw documents.

## WorkflowJsonInspector

Collapsed read-only advanced inspector.

Fields:

- `collapsed_by_default`
- `summary`
- `redaction_summary`
- `safe_document_preview`
- `artifact_reference_id`

Rules:

- Read-only only.
- No direct text editing.
- No raw secret, prompt, completion, memory, credential, provider, Telegram, connector, local path, or unauthorized tenant data.

## BuilderMutationResult

Shared save, validate, and publish result.

Fields:

- `status`: accepted, validation_error, stale_conflict, confirmation_required, dependency_unavailable, rejected, replayed.
- `summary`
- `revision`
- `field_errors`
- `stale_conflict`
- `confirmation`
- `toast`
- `audit_reference_id`
- `publish_bundle`
- `validation`
- `redirect_href`

Rules:

- Idempotent safe results may be replayed.
- Stale conflicts include current revision metadata only.
- Confirmation prompts must be explicit and auditable.
