# Data Model: Design Reviewer Template, Test Bench, And Publish Gates

## CouncilTemplateInstallRequest

- `tenant_id`: Tenant receiving the template. Must match the active principal
  scope unless the principal has platform-admin authority for that tenant.
- `template_key`: Stable template identifier. Default is
  `design-reviewer-council`.
- `idempotency_key`: Required caller-provided replay key.
- `run_required_tests`: Whether installation should launch safe-mode Test Bench
  evidence immediately. Default is true.
- `safe_mode`: Evidence execution mode. Supported values are deterministic
  local safe mode and governed model-backed safe mode without live provider
  calls in QA.

## CouncilTemplateInstallSummary

- `template_key`
- `tenant_id`
- `workflow_draft_id`
- `workflow_lineage_id`
- `workflow_draft_revision_id`
- `workflow_key`
- `display_name`
- `agent_test_suite_id`
- `agent_test_run_id`
- `required_evidence_status`
- `publish_gate_status`
- `replayed`
- `safe_summary`
- `actions`

Validation rules:

- Identifiers are tenant-scoped and safe to display.
- `safe_summary` must not include raw prompts, completions, secrets, provider
  payloads, private channel data, memory contents, unauthorized payloads, or raw
  external tool payloads.
- `replayed=true` only when the service reused an existing canonical template
  setup or an idempotent install result.

## CouncilWorkflowDraft

The install service creates a workflow draft containing these logical role
nodes:

- lead intake role
- four default reviewer roles plus support for a five-reviewer quorum scenario
- quorum join
- synthesis role
- development handoff role

Validation rules:

- Graph is acyclic.
- Quorum joins use manual-resolution failure behavior.
- Draft document carries required Test Bench evidence references for the
  workflow draft target.

## CouncilEvidenceSuite

The required suite targets the council workflow draft and is marked required for
publish.

Required cases:

- four-of-five quorum success
- three-of-four quorum success
- revision-required outcome
- blocking issue handling
- manual-resolution pause
- retry behavior
- cancel behavior
- approved handoff
- cross-tenant denial
- redaction
- Admin live-data states
- model-backed safe-mode boundary

Validation rules:

- Cases use safe payload summaries and contract assertions only.
- Evidence run target version must match the current workflow draft revision to
  satisfy the publish gate.

## PublishGateSummary

- `workflow_draft_id`
- `workflow_draft_revision_id`
- `validation_status`
- `required_evidence_status`
- `ready_to_publish`
- `blocking_reasons`
- `latest_passing_run_id`
- `safe_summary`

State transitions:

- `not_installed` -> `evidence_pending` after draft and suite creation without
  passing current evidence.
- `evidence_pending` -> `ready` after current passing evidence.
- `ready` -> `stale` after a newer draft revision is saved.
- `stale` -> `ready` after evidence passes for the newer revision.
- `ready` -> `published` after the existing workflow publish action succeeds.

## AdminTemplateState

The Admin workspace exposes the live template state alongside design-review
sessions.

- `status`: `not_installed`, `evidence_pending`, `evidence_failed`, `stale`,
  `ready`, or `published`
- `template_key`
- `workflow_draft_id`
- `workflow_draft_revision_id`
- `agent_test_suite_id`
- `latest_run_id`
- `publish_gate_status`
- `safe_summary`
- `primary_action`

Validation rules:

- No synthetic design-review sessions or reviewer rows may be created by this
  state.
- Denied users receive safe problem details, not hidden template metadata.
