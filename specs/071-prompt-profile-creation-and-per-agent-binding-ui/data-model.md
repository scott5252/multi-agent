# Data Model: Prompt Profile Creation And Per-Agent Binding UI

## Prompt Lineage Selection

Represents a prompt family that can be created or selected for a workflow role.

- `prompt_lineage_id`: Stable backend identifier.
- `scope_type`: `tenant` or `platform`.
- `tenant_id`: Present only for tenant-scoped lineages.
- `slug`: Human-readable stable slug.
- `display_name`: Safe label for selectors.
- `purpose`: Safe summary of intended use.
- `status`: Active, retired, or historical-only state.
- `latest_published_prompt_version_id`: Optional immutable version reference.
- `validation_status`: Latest safe validation state.

Rules:

- Only backend-authorized records may appear in workflow setup catalogs.
- Platform records require eligible tenant grants for tenant admins.
- Raw template content is not included in catalog summaries.

## Prompt Draft Editor State

Represents authorized editable prompt data while the admin is in the prompt edit form.

- `prompt_lineage_id`
- `prompt_draft_id`
- `current_revision_number`
- `prompt_title`
- `purpose`
- `usage_notes`
- `template_content`
- `variables`
- `fixture_sets`
- `latest_validation`

Rules:

- `template_content` is raw prompt text and must not appear outside authorized edit controls.
- Saves must use expected revision numbers and fail on stale revisions.
- Variable declarations must use backend prompt validation rules.
- Fixture values must be redacted or summarized when displayed outside the edit form.

## Prompt Version Binding Reference

Represents an immutable published prompt version attached to a workflow role.

- `reference_key`: Workflow-document key used by role references.
- `role_key`: Role that owns or primarily uses the reference.
- `prompt_version_ids`: Published prompt version ids.
- `prompt_reference_version_ids`: Model-skill prompt reference ids when applicable.
- `source_scope`: Tenant/platform source summary.
- `readiness_status`: `ready`, `warning`, `blocked`, `stale`, or `unknown`.
- `resolution_digest`: Safe digest proving resolution without raw prompt content.

Rules:

- Role bindings store ids and safe metadata, not raw prompt templates.
- Retired, inactive, unauthorized, missing, stale, or cross-tenant references are backend validation blockers.

## Runtime Profile Draft Editor State

Represents authorized editable runtime profile data.

- `agent_runtime_profile_id`
- `agent_profile_draft_id`
- `current_revision_number`
- `agent_key`
- `agent_kind`
- `display_name`
- `purpose`
- `prompt_references`
- `model_routing_hints`
- `memory_scope_policy`
- `skill_requirements`
- `tool_policy_expectations`
- `output_contract_expectations`
- `test_suite_requirements`
- `latest_validation`

Rules:

- Prompt references must point to eligible published prompt versions.
- Model routing hints and provider readiness summaries must be safe and redacted.
- Profile activation is blocked until backend validation passes.

## Runtime Profile Version Binding Reference

Represents an immutable active runtime profile version attached to a workflow role.

- `reference_key`: Workflow-document key used by `roles[].profile_reference_key`.
- `agent_profile_version_id`
- `agent_key`
- `agent_kind`
- `display_version`
- `status`
- `source_scope`
- `readiness_status`
- `model_routing_preview`
- `safe_summary`

Rules:

- Only active profile versions are selectable for new role bindings.
- Profile summaries must not expose provider payloads, credentials, raw prompts, raw completions, or private tool payloads.

## Per-Agent Binding Row

Represents one workflow role's binding state in the browser.

- `role_key`
- `display_name`
- `role_kind`
- `prompt_reference_keys`
- `profile_reference_key`
- `prompt_status`
- `profile_status`
- `validation_status`
- `available_actions`
- `findings`

Rules:

- Binding rows are derived from workflow role definitions plus safe prompt/profile catalogs.
- Missing prompt/profile references are truthful incomplete states.
- Saving the workflow persists only role reference keys and prompt/profile reference entries.

## Binding Readiness Finding

Backend-owned finding that maps prompt/profile problems back to a workflow role.

- `code`
- `severity`
- `section`
- `field_path`
- `role_key`
- `reference_key`
- `safe_message`
- `remediation`

Rules:

- Findings must not include raw prompt templates, provider payloads, credential values, raw completions, raw transcripts, local paths, or unauthorized tenant labels.
- Findings must map to visible workflow setup controls for recovery.
