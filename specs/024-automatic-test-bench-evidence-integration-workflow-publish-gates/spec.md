# Feature Specification: Automatic Test Bench Evidence Integration In Workflow Publish Gates

**Feature Branch**: `codex/024-automatic-test-bench-evidence-integration-workflow-publish-gates`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Wire agent workflow test-bench evidence directly into workflow publish gates. When a workflow draft declares required test suites, validation and publication must query the test-bench repository for current passing evidence tied to the candidate draft revision or published target version. Admins must no longer manually copy latest_result_status into the workflow document. Stale, missing, failing, or cross-tenant test evidence must block publication with safe diagnostics."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Block Publish Without Current Evidence (Priority: P1)

Tenant and platform admins can declare required agent test suites on a workflow draft and rely on validation plus publish gates to query authoritative test-bench runs for the current candidate revision before publication.

**Why this priority**: This removes the manual `latest_result_status` workaround that currently lets stale or copied status values bypass real evidence.

**Independent Test**: Create a tenant workflow draft with a required suite, validate it before any current passing run exists, and confirm validation and publish gate responses block with safe missing or stale evidence diagnostics.

**Acceptance Scenarios**:

1. **Given** a workflow draft declares a required suite and no passing run exists for the current draft revision, **When** an admin validates the draft, **Then** the validation result includes a blocking required-test finding and a missing evidence summary.
2. **Given** a required suite has a passing run for a previous draft revision only, **When** an admin opens the publish gate for the current revision, **Then** the gate is blocked as stale and does not expose raw fixture, transcript, or tenant-private payloads.
3. **Given** a required suite has a failing, blocked, or errored run for the current revision, **When** publication is attempted, **Then** publication fails with a safe diagnostic that required evidence is not passing.

---

### User Story 2 - Accept Only Tenant-Scoped Current Passing Evidence (Priority: P1)

Workflow validation and publication accept required test evidence only when the suite and latest passing run belong to the workflow tenant and match the workflow draft target and current revision.

**Why this priority**: Publish readiness is tenant-sensitive release evidence; cross-tenant or wrong-target evidence must fail closed.

**Independent Test**: Reference a suite from another tenant or with a mismatched target from a tenant workflow draft and confirm the workflow gate reports unavailable evidence without revealing the other tenant's suite details.

**Acceptance Scenarios**:

1. **Given** a tenant workflow references a suite ID owned by another tenant, **When** validation runs, **Then** the result blocks as unavailable evidence and does not disclose the other tenant name, suite name, run details, fixtures, or transcripts.
2. **Given** a suite exists for the same tenant but targets a different workflow draft, **When** publish readiness is evaluated, **Then** the gate blocks as stale or mismatched target evidence.
3. **Given** a suite and passing run match the tenant, target draft, and current revision, **When** validation and publish gate evaluation run, **Then** the required-test summary is ready and publication can proceed when all other gates pass.

---

### User Story 3 - Show Safe Evidence Summaries In Admin UI (Priority: P2)

Admins can inspect workflow publish gates and see which required suites are passing, missing, stale, failing, or unavailable using safe summaries backed by test-bench evidence.

**Why this priority**: Admins need clear release-blocker guidance without copying status fields or opening raw run payloads.

**Independent Test**: Open the workflow publish gate UI for drafts with passing, missing, and stale evidence and confirm the status, counts, and remediation text are understandable and redaction-safe.

**Acceptance Scenarios**:

1. **Given** a publish gate has required test blockers, **When** the admin opens the gate UI, **Then** the page lists the safe evidence summary and disables confirmation.
2. **Given** all required suites pass for the current revision, **When** the admin opens the gate UI, **Then** the page shows passing counts and permits confirmation when validation is current.
3. **Given** a validation result stores required-test snapshots, **When** an admin reviews the workflow editor validation panel, **Then** the summary reflects repository-backed evidence rather than manual document status.

### Edge Cases

- A required suite ID is malformed, deleted, archived, or unavailable in the current tenant.
- A suite exists but has no active test cases and therefore cannot produce current evidence.
- A latest run is queued or running when the publish gate is evaluated.
- A passing run exists for the same suite but an older draft revision.
- A passing run exists for the current revision but for a different workflow draft target.
- A platform-scoped workflow declares tenant-scoped tests without an explicit tenant evidence context.
- Validation is run, then the draft is saved, making the previous test evidence stale for the new revision.
- The workflow document still contains legacy `latest_result_status` values from older drafts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST evaluate workflow `test_requirements` by querying authoritative agent test-bench records instead of trusting `latest_result_status` in the workflow document.
- **FR-002**: The system MUST bind required workflow-draft evidence to the current `workflow_draft_id` and current `workflow_draft_revision_id`.
- **FR-003**: The system MUST treat passing runs for previous draft revisions, different target IDs, or different target types as stale or mismatched evidence.
- **FR-004**: The system MUST fail closed when required evidence belongs to another tenant or cannot be resolved in the workflow tenant context.
- **FR-005**: Validation results MUST include required-test blocking findings when evidence is missing, stale, failing, unavailable, or cross-tenant.
- **FR-006**: Publish gate evaluation and final publication MUST re-query the latest evidence before allowing publication.
- **FR-007**: Required-test summaries MUST include required, passing, failing, missing, and stale counts derived from repository evidence.
- **FR-008**: Publish gate pin summaries MUST include safe required-test evidence identifiers, status, matching target version, passing run IDs when available, and redaction-safe summaries.
- **FR-009**: Admin UI publish gate pages MUST show required-test evidence status and remediation without exposing fixtures, raw transcripts, secrets, or cross-tenant record details.
- **FR-010**: Existing workflow documents with `latest_result_status` values MUST remain parseable, but those values MUST NOT make a gate ready without matching repository evidence.
- **FR-011**: The system MUST emit audit-safe workflow validation and publish-gate events that include gate status and counts without raw test payloads.
- **FR-012**: Automated tests MUST cover current passing, missing, stale, failing, malformed, wrong-target, and cross-tenant evidence behavior.

### Key Entities *(include if feature involves data)*

- **Workflow Required Test Declaration**: Existing workflow document entry that names a required suite and freshness policy; legacy result status fields remain compatibility metadata only.
- **Agent Test Suite**: Tenant-owned test-bench suite with target type, target ID, optional target version, cases, safe mode, and required-for-publish metadata.
- **Agent Test Run Evidence**: Tenant-owned run result with status, target type, target ID, target version, run ID, completion time, and redaction-safe summaries.
- **Required Test Evidence Snapshot**: Redaction-safe publish-gate snapshot derived from repository records for one workflow requirement.
- **Publish Gate Summary**: Combined gate response that includes validation status, reference readiness, required-test evidence summary, digest, and blocking findings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A workflow draft with no current passing required-test run is blocked by validation and publish gate evaluation 100 percent of the time in automated tests.
- **SC-002**: A workflow draft with a same-tenant passing run for the current revision can publish when all other readiness checks pass.
- **SC-003**: Cross-tenant suite references are denied without leaking the other tenant's suite name, run ID, fixture, transcript, or payload.
- **SC-004**: Legacy manual `latest_result_status="passed"` values do not allow publication unless repository evidence also passes.
- **SC-005**: The publish gate UI displays required, passing, missing, failing, and stale counts for required-test evidence.
- **SC-006**: Focused tests plus project quality gates pass with at least 90 percent coverage for the repository.

## Assumptions

- Workflow draft test evidence is considered current only when the run target version equals the current `workflow_draft_revision_id`.
- Existing `TestSuiteRequirement.target_type="workflow_revision"` maps to the test-bench `workflow_draft` target with `workflow_draft_id` as the target ID and the revision ID as the target version.
- Platform-scoped workflows cannot use tenant-owned test evidence unless a future spec defines a platform evidence scope; for this feature, platform workflows with declared tenant tests fail closed.
- Existing test-bench safe-mode and redaction behavior is reused; this feature does not execute tests automatically during publication.
- Publication performs a fresh evidence lookup even if validation already passed to avoid stale state.

## Constitution Alignment

- **Durability and recovery**: In scope. Evidence is read from persisted PostgreSQL test-bench runs and validation results, not transient UI state.
- **Tenant isolation and fair use**: In scope. Suite and run lookups are tenant-scoped and cross-tenant evidence fails closed.
- **Contracts, versioning, and lineage**: In scope. Current draft revision IDs are the target-version boundary, and publish bundles pin safe evidence summaries.
- **Security, secrets, and tool access**: In scope. Summaries must not expose raw fixtures, transcripts, secrets, or tool payloads.
- **Artifact and data storage**: In scope only for metadata. No new large artifacts are stored; existing test artifacts stay in the test-bench storage model.
- **Approval and resume behavior**: Not directly in scope. Publish confirmation remains an existing admin action and does not introduce a durable wait state.
- **Observability and auditability**: In scope. Validation and publish-gate decisions continue to emit safe workflow audit events with status and counts.

## Testing Instructions

- Add focused unit tests for repository-backed evidence classification and publish gate summaries.
- Add service tests for validation and publication that prove manual document status is ignored.
- Add cross-tenant denial tests that assert safe messages do not expose foreign suite details.
- Add UI route/template tests for required-test evidence summary rendering.
- Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.

## PR Review Guidance

- Confirm every new evidence query includes tenant ID and target binding.
- Confirm publication re-queries evidence after validation instead of reusing stale validation JSON.
- Confirm raw fixtures, transcripts, prompts, secrets, and cross-tenant identifiers are absent from diagnostics.
- Confirm legacy `latest_result_status` compatibility does not recreate the bypass.
- Confirm docs and QA guides explain how reviewers create current passing evidence.

## Documentation Impact

- Add `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/quickstart.md`.
- Add `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/testing-instructions.md`.
- Add `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/pr-review-notes.md`.
- Update `README.md` and `docs/quickstart.md` to mention repository-backed workflow publish evidence.
- Generate QA024 manual, UI, environment, and non-developer user guide artifacts after implementation.
