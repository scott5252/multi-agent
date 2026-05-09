# Data Model: Custom Workflow Test Evidence And Publish Setup

## Workflow Evidence Requirement

Represents the workflow document's required test evidence reference.

Fields:

- `requirement_key`: stable workflow-document key for the evidence requirement.
- `suite_id`: opaque Test Bench suite identifier selected or created for the workflow.
- `suite_label`: safe display label.
- `target_type`: workflow target type, expected to identify workflow draft evidence.
- `target_id`: opaque workflow lineage/draft target reference.
- `target_revision`: workflow draft revision that evidence must match.
- `required_case_keys`: ordered safe case keys or labels expected for publish.
- `status`: `missing`, `ready`, `stale`, `failed`, `blocked`, or `denied`.
- `last_run_id`: optional latest safe run reference used by evidence refresh.
- `freshness_summary`: safe backend-owned explanation.

Relationships:

- Belongs to one workflow draft document.
- References one contextual Test Bench suite.
- May reference the latest run summary and artifact references.

Validation rules:

- Must target the active tenant and current workflow draft revision.
- Must not reference cross-tenant suites, failed evidence, unsupported mode runs, synthetic evidence, or stale revisions.
- Must not persist raw transcripts, prompts, completions, provider payloads, local paths, credentials, or private payloads.

## Contextual Test Suite

Represents an existing Test Bench suite eligible for the active workflow setup context.

Fields:

- `suite_id`: opaque suite identifier.
- `suite_name`: safe suite label.
- `target_type`: suite target type.
- `target_id`: workflow target id.
- `target_revision`: selected workflow draft revision.
- `default_safe_mode`: deterministic safe execution mode.
- `required_for_publish`: publish gate flag.
- `pass_threshold`: numeric pass threshold.
- `case_count`: number of safe cases.
- `latest_run_status`: optional latest run status.
- `authorized_actions`: allowed create/select/open/run actions.

Relationships:

- Has many test cases.
- Has many runs.
- Can be attached to one or more publication requirements when eligible.

Validation rules:

- Tenant and principal must be authorized.
- Target type, target id, and target revision must match the workflow context for direct attachment.
- Live provider or external side-effect modes are blocked unless backend policy explicitly approves them.

## Required Case Template

Represents a safe deterministic case pattern users can add from workflow setup.

Fields:

- `template_key`: stable template key.
- `label`: safe label.
- `fixture_summary`: safe fixture summary.
- `expected_contract_summary`: safe expected contract summary.
- `assertion_summaries`: safe assertion summaries.
- `default_threshold`: numeric threshold contribution.
- `recommended_order`: default case order.

Relationships:

- Can create a Test Bench case in the selected suite.
- Maps to workflow contracts, roles, or graph paths where applicable.

Validation rules:

- Template must not contain raw prompts, raw completions, provider payloads, credentials, transcripts, or private data in display surfaces.
- Case creation must be idempotent for repeated workflow setup actions.

## Evidence Run Summary

Represents a redaction-safe run result used by workflow setup.

Fields:

- `run_id`: opaque Test Bench run id.
- `suite_id`: suite id.
- `target_revision`: workflow draft revision used for the run.
- `safe_mode`: deterministic execution mode.
- `run_status`: `queued`, `running`, `passed`, `failed`, `partial`, `timed_out`, `canceled`, `stale`, or `blocked`.
- `passing_count`: number of passing cases/assertions.
- `failing_count`: number of failing cases/assertions.
- `diagnostic_summaries`: safe diagnostic messages.
- `artifact_references`: opaque safe artifact references.
- `completed_at`: optional completion timestamp.

Relationships:

- Belongs to one suite.
- May satisfy one workflow evidence requirement when passing and current.

Validation rules:

- Target revision must match the active draft revision.
- Failed, partial, timed-out, canceled, unsupported-mode, missing artifact, or stale runs cannot satisfy publish readiness.
- Artifact references must not expose local paths or raw payloads.

## Publish Evidence Gate

Represents backend-owned publish readiness for required evidence.

Fields:

- `gate_id`: stable safe gate key.
- `status`: `ready`, `blocked`, `missing`, `stale`, `failed`, or `denied`.
- `required_count`: required suite count.
- `passing_count`: passing current evidence count.
- `failing_count`: failing evidence count.
- `missing_count`: missing evidence count.
- `stale_count`: stale evidence count.
- `safe_reasons`: actionable safe blocker summaries.
- `remediation_links`: safe section/action references for UI navigation.

Relationships:

- Combines workflow validation state with Test Bench evidence summaries.
- Feeds Workflow Publish Panel and validation blockers.

Validation rules:

- Browser state cannot mark a gate ready.
- Synthetic, cross-tenant, failed, missing, incomplete, or stale evidence is rejected.
