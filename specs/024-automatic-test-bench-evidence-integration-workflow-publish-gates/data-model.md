# Data Model: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Workflow Required Test Declaration

Existing workflow document entity: `TestSuiteRequirement`.

Key fields:

- `requirement_key`: Stable workflow-local key for one required suite.
- `suite_id`: String identifier of the selected `AgentTestSuite`.
- `target_type`: Compatibility field. `workflow_revision` maps to test-bench `workflow_draft`.
- `freshness_policy`: `latest_revision` means evidence must match the current draft revision.
- `latest_result_id`, `latest_result_status`, `executed_at`, `safe_summary`: Legacy compatibility metadata; not authoritative for publish readiness.

Validation rules:

- Requirement keys remain unique inside the workflow document.
- Malformed or unavailable suite IDs block safely as missing evidence.
- Legacy status fields do not make evidence ready.

## Agent Test Suite

Existing database entity: `AgentTestSuite`.

Relevant fields:

- `agent_test_suite_id`
- `tenant_id`
- `target_type`
- `target_id`
- `target_version`
- `status`
- `is_required_for_publish`

Validation rules:

- Suite must belong to the workflow tenant.
- Suite must be active and target the current workflow draft for draft publish gates.
- Suite target mismatch blocks as stale or mismatched evidence.

## Agent Test Run Evidence

Existing database entity: `AgentTestRun`.

Relevant fields:

- `agent_test_run_id`
- `tenant_id`
- `agent_test_suite_id`
- `target_type`
- `target_id`
- `target_version`
- `status`
- `pass_status`
- `completed_at`
- `redaction_summary`
- `artifact_summary`

Validation rules:

- Passing run must match suite, tenant, target type, target ID, and current target version.
- Passing run for an older target version is stale.
- Failing, blocked, errored, queued, or running current-version runs are not passing evidence.

## Required Test Evidence Snapshot

New service-level projection, represented in API responses as a `ReferenceReadinessSnapshot`.

Fields:

- `reference_type`: `test_suite`
- `reference_key`: workflow requirement key
- `status`: `passed`, `missing`, `stale`, `failed`, or `unavailable`
- `blocking`: true unless status is `passed`
- `safe_summary`: short remediation-safe sentence
- `pin_payload`: suite ID, run ID when available, target type, target ID, target version, status, and freshness policy

Validation rules:

- Pin payload must not include fixtures, expected contract payloads, raw transcripts, prompt text, secrets, tenant names, or cross-tenant details.

## Required Test Summary

Existing API projection: `RequiredTestSummary`.

Fields:

- `required_count`
- `passing_count`
- `failing_count`
- `missing_count`
- `stale_count`

Validation rules:

- Ready only when every required suite has a current passing run.
- Counts are derived from repository evidence, not workflow document status fields.
