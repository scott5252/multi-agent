# Data Model: Test Bench React Live Data

## Agent Test Suite

Represents a tenant-scoped suite used to qualify a workflow, profile, prompt, or published bundle.

- **Identity**: `agent_test_suite_id`, tenant id, name, target type, target id, optional target version.
- **Authoring State**: description, default safe mode, model/tool modes, pass threshold, required-for-publish flag, status, revision, created-by principal, timestamps.
- **Relationships**: has many agent test cases, publication requirements, and test runs.
- **Validation Rules**: Suite names are tenant-unique. Archived suites cannot be launched. Target references must be authorized for the active tenant or return unavailable/denied projection state.
- **State Transitions**: draft/active to archived; revision increments on durable edits; publication requirement can be active or archived.

## Agent Test Case

Represents one executable case within a suite.

- **Identity**: `agent_test_case_id`, suite id, tenant id, case name.
- **Authoring State**: description, fixture summary, fixture artifact reference, expected contract shape, evaluator reference, model/tool modes, pass threshold, order, status, revision, timestamps.
- **Relationships**: belongs to one suite; has many assertions; can be referenced by run steps and artifacts.
- **Validation Rules**: Case records must belong to a suite in the same tenant. Fixture summaries must be safe and must not render raw fixture bodies, prompts, completions, private messages, memory content, or tool payloads.
- **State Transitions**: active to archived; revision increments on durable edits.

## Agent Test Assertion

Represents a redaction-safe assertion definition attached to a case.

- **Identity**: `agent_test_assertion_id`, case id, tenant id.
- **Definition State**: kind, path summary, comparator, expected value or schema summary, threshold, severity, weight, description.
- **Relationships**: belongs to one case and contributes to run-step assertion results.
- **Validation Rules**: Expected values and schema details must be summarized before React; unsafe marker values are rejected by schema validators.

## Agent Test Run

Represents a durable execution request and result.

- **Identity**: `agent_test_run_id`, tenant id, suite id, idempotency key, trace id.
- **Execution State**: target type/id/version, safe mode, status, pass status, triggering principal, timestamps, usage summary, latency, redaction summary, artifact summary, blocked side-effect count, failure summary.
- **Relationships**: belongs to one suite; has many run steps; may have artifact records; can satisfy publication requirements when passing and current.
- **Validation Rules**: Run launch requires an active suite with active cases. Idempotency keys replay the existing run for the same tenant. Real probes require explicit approved references and remain unavailable in QA validation.
- **State Transitions**: queued/running to passed, failed, blocked, or error; terminal runs expose safe result summaries only.

## Agent Test Run Step

Represents ordered case execution and progress evidence for a run.

- **Identity**: `agent_test_run_step_id`, run id, optional case id, tenant id, sequence.
- **Execution State**: step name, status, provider/model/profile/workflow references, latency, token usage summary, contract validation summary, assertion result summaries, blocked side effects, redacted transcript summary, artifact references, failure reason.
- **Relationships**: belongs to one run and optionally one case.
- **Validation Rules**: Raw transcripts, prompts, completions, runtime payloads, and stack traces are not rendered. Safe summaries and artifact references may be exposed.

## Agent Test Artifact

Represents safe metadata for test evidence stored outside transactional state.

- **Identity**: `agent_test_artifact_id`, tenant id, optional run id, optional case id.
- **Artifact State**: artifact type, checksum, size, content type, redaction classification, retention state, safe summary, creation and expiration timestamps.
- **Relationships**: may belong to a run or case and may reference external/object storage metadata.
- **Validation Rules**: React receives artifact reference ids, safe labels, hashes, size labels, retention state, access status, and safe summaries. Storage URIs and raw contents never render.

## Agent Test Publication Requirement

Represents a required suite for a target's publish gate.

- **Identity**: `agent_test_publication_requirement_id`, tenant id, target type, target id, suite id.
- **Gate State**: required flag, minimum pass status, created-by principal, archived timestamp, timestamps.
- **Relationships**: points to one suite and is evaluated against latest qualifying runs for the target and revision.
- **Validation Rules**: Required evidence must match tenant, target, suite, and current target version when present. Missing or stale runs produce missing/stale evidence.

## Test Bench Audit Record

Represents append-only safe evidence for authoring, launch, progress, artifact, gate, denial, or export activity.

- **Identity**: audit reference id or event id, tenant id, actor, action, outcome, timestamp.
- **Audit State**: safe diff summary, scope label, target reference, route or service reference, trace id when safe.
- **Relationships**: may reference suites, cases, runs, artifacts, publication requirements, or target records.
- **Validation Rules**: Audit summaries must not reveal unauthorized tenant labels, raw payloads, local paths, stack traces, prompts, completions, or private messages.

## Response Envelope Metadata

Represents provenance and empty-state context added to test bench JSON responses.

- **Provenance Fields**: source (`live_repository`), source record counts, tenant id or platform scope, generated timestamp, bounded query notes.
- **Empty-State Fields**: state key, title, summary, recommended action, unavailable/denied reason when applicable.
- **Validation Rules**: Empty-state metadata must be truthful for empty databases and must not invent suite, case, run, artifact, gate, or audit rows.
