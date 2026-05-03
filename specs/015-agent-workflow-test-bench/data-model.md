# Data Model: Agent And Workflow Test Bench

## AgentTestSuite

Tenant-scoped collection of reusable test cases for an agent, prompt/profile,
workflow draft, published subworkflow, or published workflow.

**Fields**: `id`, `tenant_id`, `name`, `description`, `target_type`,
`target_id`, `target_version`, `default_safe_mode`, `model_mode`,
`tool_mode`, `pass_threshold`, `is_required_for_publish`, `status`,
`revision`, `created_by`, `created_at`, `updated_at`, `archived_at`.

**Relationships**: Has many `AgentTestCase`, `AgentTestRun`, and
`AgentTestPublicationRequirement` records.

**Validation rules**: Name is required per tenant. Target type must be one of
`prompt_version`, `agent_profile_version`, `workflow_draft`,
`published_subworkflow`, or `published_workflow`. Pass threshold is between 0
and 1. Tenant id is immutable after creation.

**State transitions**: `draft -> active -> archived`; archived suites cannot
start new runs or satisfy publish gates until restored.

## AgentTestCase

A scenario inside a suite with fixture inputs, expected contract shapes,
assertions, optional evaluator configuration, and execution overrides.

**Fields**: `id`, `suite_id`, `tenant_id`, `name`, `description`,
`fixture_summary`, `fixture_artifact_id`, `expected_contract_shape`,
`model_mode`, `tool_mode`, `evaluator_prompt_ref`, `pass_threshold`, `order`,
`status`, `revision`, `created_at`, `updated_at`, `archived_at`.

**Relationships**: Belongs to `AgentTestSuite`; has many
`AgentTestAssertion`; contributes to `AgentTestRunStep`.

**Validation rules**: Fixture summary must be redacted and inline-safe. Large
or sensitive fixtures require an artifact reference. Expected contract shape
must be structured JSON. Case target and tenant must match the parent suite.

## AgentTestAssertion

Typed deterministic or evaluator-backed assertion for a test case.

**Fields**: `id`, `case_id`, `tenant_id`, `kind`, `path`, `comparator`,
`expected_value`, `expected_schema`, `threshold`, `severity`, `weight`,
`description`, `created_at`, `updated_at`.

**Relationships**: Belongs to `AgentTestCase`; evaluated into one or more
run-step diagnostics.

**Validation rules**: Deterministic assertions require a comparator and either
an expected value or schema. Evaluator assertions require threshold and
evaluator prompt reference metadata. Arbitrary code execution is forbidden.

## AgentTestRun

Durable execution record for a suite against a target version and safe mode.

**Fields**: `id`, `tenant_id`, `suite_id`, `target_type`, `target_id`,
`target_version`, `safe_mode`, `status`, `pass_status`, `triggered_by`,
`idempotency_key`, `trace_id`, `started_at`, `completed_at`,
`usage_summary`, `latency_ms`, `redaction_summary`, `artifact_summary`,
`blocked_side_effect_count`, `failure_summary`, `created_at`.

**Relationships**: Belongs to `AgentTestSuite`; has many
`AgentTestRunStep` and `AgentTestArtifact` records.

**Validation rules**: Safe mode must be one of `mock_model`, `mock_tools`,
`real_model_side_effects_disabled`, or `approved_real_probe`. Approved probe
mode requires approval metadata. Run target version must match the suite target
or an explicitly supplied candidate version.

**State transitions**: `queued -> running -> passed|failed|blocked|error`;
terminal states are immutable except for redaction/artifact retention metadata.

## AgentTestRunStep

Per-case or per-runtime-step diagnostic result.

**Fields**: `id`, `run_id`, `tenant_id`, `case_id`, `step_name`, `status`,
`sequence`, `model_provider`, `model_id`, `prompt_version_id`,
`profile_version_id`, `skill_version_refs`, `workflow_version_ref`,
`latency_ms`, `token_usage`, `contract_validation`, `assertion_results`,
`blocked_side_effects`, `redacted_transcript`, `artifact_refs`,
`failure_reason`, `created_at`.

**Relationships**: Belongs to `AgentTestRun`; optionally belongs to
`AgentTestCase`; references artifacts by metadata id.

**Validation rules**: Raw transcript payloads are never stored inline. Step
metadata must be tenant-scoped and redacted before persistence when it may be
displayed.

## AgentTestArtifact

Metadata for fixture, transcript, evaluator, screenshot, or result payloads
stored outside PostgreSQL.

**Fields**: `id`, `tenant_id`, `run_id`, `case_id`, `artifact_type`,
`storage_uri`, `checksum_sha256`, `size_bytes`, `content_type`,
`redaction_classification`, `retention_state`, `safe_summary`, `created_at`,
`expires_at`.

**Relationships**: Belongs to `AgentTestRun` and optionally
`AgentTestCase`.

**Validation rules**: Storage URI must point to an allowed artifact root.
Safe summary must not contain raw secrets, prompt bodies, credential values, or
large payloads. Expired artifacts remain as metadata with unavailable state.

## AgentTestPublicationRequirement

Rule requiring one or more suites to pass before publishing a workflow,
subworkflow, or draft candidate.

**Fields**: `id`, `tenant_id`, `target_type`, `target_id`, `suite_id`,
`required`, `minimum_pass_status`, `created_by`, `created_at`, `updated_at`,
`archived_at`.

**Relationships**: Belongs to `AgentTestSuite`; evaluated against
`AgentTestRun` evidence.

**Validation rules**: Requirement target must match suite target type/id or an
authorized compatible workflow target. Archived requirements do not block
publication. Passing evidence must match the current candidate target version.

## SafeModeDecision

Domain value recorded inside run and step metadata.

**Values**:

- `mock_model`: deterministic model response and mock tool outputs.
- `mock_tools`: real or mocked model path with tool calls replaced by safe
  tool responses.
- `real_model_side_effects_disabled`: governed gateway call allowed, tool and
  external side effects blocked.
- `approved_real_probe`: explicit approved probe metadata required before any
  dependency probe can run.

## Redaction And Retention Rules

- Inline fixture and transcript summaries are redacted before storage.
- Raw prompt bodies, provider messages, memory payloads, credential values,
  tool payloads, and external responses are not rendered in API or UI results.
- Large artifacts use storage references plus checksum and retention metadata.
- Deleting or expiring an artifact does not delete the run, audit, or gate
  evidence metadata.
