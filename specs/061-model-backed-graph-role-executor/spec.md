# Feature Specification: Model-Backed Graph Role Executor

**Feature Branch**: `codex/061-model-backed-graph-role-executor`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Add governed model-backed role-node execution for workflow graph role nodes. The feature must allow a published workflow role node to execute through ModelGateway when the run's execution mode and policy pins permit it. The executor must resolve active prompt/profile/provider pins, build redaction-safe model inputs from upstream summaries and artifact references, call ModelGateway, validate structured output against the role output contract, persist large allowed outputs as artifact references, capture usage/provenance, and return safe RoleExecutionResult data to graph execution. It must fail closed when pins, credentials, provider policy, contract validation, redaction, or tenant scope is invalid. Existing deterministic execution must remain available for local QA and test bench."

## Clarifications

### Session 2026-05-08

- Q: What execution mode enables model-backed role-node execution? -> A: Existing deterministic execution remains default; model-backed execution requires an explicit run/workflow execution mode that maps to a mocked or governed ModelGateway path and valid tenant-scoped pins (autopilot).
- Q: What may be included in model inputs and persisted role results? -> A: Only safe summaries, structured contract metadata, artifact references, digests, policy references, and provenance may be included; raw prompts, completions, secrets, provider payloads, memory contents, private messages, unauthorized payloads, and raw external tool payloads are excluded (autopilot).
- Q: How should local QA exercise the model-backed path? -> A: Use mocked ModelGateway/provider responses and local-principal seed data; no real Auth0, Telegram, provider, credential, connector, or outbound call is required (autopilot).
- Q: How should invalid pins, policies, credentials, or output contracts behave? -> A: Fail closed before graph success, return safe role failure metadata, and avoid provider calls when denial occurs before gateway invocation (autopilot).
- Q: What is deferred to later scenario specs? -> A: Spec 061 owns role-node execution only; coordinator retry loops, Admin design review workspace, reusable workflow templates, and publish-gate evidence remain deferred to Specs 062-064 (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Governed Role Execution (Priority: P1)

A workflow run with a published role node chooses deterministic execution or
model-backed execution based on the run's execution mode and governed pins,
then fails closed when required prompt, profile, provider, credential, policy,
or tenant context is unavailable.

**Why this priority**: The platform must decide safely whether a role node may
use a provider before any model call is attempted.

**Independent Test**: Run role-node execution with deterministic mode,
model-backed mode, missing pins, denied policy, and cross-tenant context, then
verify only permitted runs reach the model-backed path and all denied paths
return safe failures without provider calls.

**Acceptance Scenarios**:

1. **Given** a runnable workflow role node and deterministic execution mode, **When** graph execution reaches the node, **Then** the existing deterministic role result is returned and no model provider path is invoked.
2. **Given** a runnable workflow role node, model-backed execution mode, and valid governed prompt/profile/provider pins, **When** graph execution reaches the node, **Then** the model-backed executor is selected for that role node.
3. **Given** missing, inactive, denied, or cross-tenant pins, **When** model-backed role execution is requested, **Then** the system fails closed with a safe denial reason and no raw provider request is sent.

---

### User Story 2 - Execute Role Nodes Through Governed Model Gateway (Priority: P2)

Authorized model-backed role nodes build safe model inputs from upstream
summaries, artifact references, and workflow context, call the model gateway
through existing governance, and validate structured outputs against the role
contract before graph execution can continue.

**Why this priority**: Model output must be bounded, validated, and redacted
before it becomes runtime state or design-review evidence.

**Independent Test**: Execute a model-backed role node with a mocked gateway
response, then verify safe input construction, gateway call provenance, contract
validation, redaction checks, structured result mapping, and validation failure
behavior.

**Acceptance Scenarios**:

1. **Given** valid role inputs, upstream summaries, artifact references, and pins, **When** the model-backed executor runs, **Then** it submits only redaction-safe input metadata to the gateway and receives a structured response.
2. **Given** a response that matches the role output contract, **When** validation completes, **Then** the executor returns safe role output data, artifact references, usage, and provenance to graph execution.
3. **Given** malformed, unsafe, overlarge, or contract-invalid output, **When** validation runs, **Then** the executor records a safe failure and graph execution does not treat the node as successful.

---

### User Story 3 - Preserve Evidence And Deterministic QA (Priority: P3)

Runtime and QA operators can inspect safe role execution provenance, usage, and
artifact references while local QA and test bench flows continue to use the
deterministic executor unless they explicitly opt into mocked model-backed
execution.

**Why this priority**: The scenario must be production-ready without breaking
existing deterministic regression tests or exposing raw prompts/completions.

**Independent Test**: Run deterministic and mocked model-backed executions, then
verify usage/provenance evidence, artifact reference behavior for large allowed
outputs, redacted failure summaries, test-bench compatibility, and curl/QA
coverage.

**Acceptance Scenarios**:

1. **Given** model-backed execution succeeds, **When** runtime evidence is inspected, **Then** it includes safe prompt/profile/provider references, usage totals, output digest, artifact references, latency, and policy decision summaries without raw prompts or completions.
2. **Given** local QA or test bench does not opt into model-backed mode, **When** role nodes execute, **Then** deterministic execution remains unchanged.
3. **Given** an allowed output is too large for inline role result metadata, **When** the executor persists it, **Then** graph execution receives an artifact reference and digest rather than raw body content.

### Edge Cases

- Model-backed execution must not run when execution mode, tenant context, prompt/profile/provider pin, credential readiness, routing policy, or provider health fails validation.
- A provider or gateway response that lacks required contract fields, contains raw protected content, exceeds safe inline limits, or cannot be parsed must fail the role node safely.
- Upstream role outputs may be absent, failed, or represented only by artifact references; the executor must include safe summaries and references rather than raw hidden payloads.
- Replayed or retried workflow steps must not duplicate model usage/evidence records when an idempotent result is already available.
- Cross-tenant workflow, prompt, profile, provider, credential, artifact, or design-review references must be denied without disclosing whether the referenced object exists.
- Deterministic QA and test bench execution must remain the default for existing suites and must not require real provider credentials.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a role-node executor selection path that preserves deterministic execution and adds model-backed execution only when the workflow run execution mode permits it.
- **FR-002**: The system MUST resolve prompt, runtime profile, model routing/provider, credential readiness, and policy pins for each model-backed role node using tenant-scoped governance state.
- **FR-003**: The system MUST fail closed before a provider call when required pins are missing, inactive, stale, unauthorized, cross-tenant, or policy-denied.
- **FR-004**: The system MUST build model input from safe workflow metadata, upstream safe summaries, artifact references, role instructions, and contract metadata without raw secrets, private channel payloads, memory contents, raw prompts, or unauthorized payloads.
- **FR-005**: The system MUST call the existing ModelGateway through mocked or governed provider paths and capture safe attempt, usage, latency, and routing provenance.
- **FR-006**: The system MUST validate each model-backed response against the role output contract before returning success to graph execution.
- **FR-007**: The system MUST reject malformed, incomplete, unsafe, contract-invalid, overlarge inline, or unredactable model output and return a safe role failure.
- **FR-008**: The system MUST persist or reference large allowed outputs using artifact references and digests rather than embedding raw bodies in runtime state or QA artifacts.
- **FR-009**: The system MUST return a safe `RoleExecutionResult` compatible with existing graph execution status, timeline, handoff, and quorum behavior.
- **FR-010**: The system MUST record safe usage/provenance evidence for model-backed role execution without raw prompts, raw completions, provider authorization headers, credential values, or raw provider payloads.
- **FR-011**: The system MUST expose test or diagnostic coverage that proves deterministic mode still uses the deterministic executor and model-backed mode can run through mocked gateway responses.
- **FR-012**: The system MUST keep local QA, test bench, and existing curl regression flows deterministic by default unless a scenario explicitly selects mocked model-backed execution.
- **FR-013**: The system MUST enforce tenant isolation across workflow runs, prompt/profile/provider pins, credentials, artifacts, and design-review references.
- **FR-014**: The system MUST add audit-safe failure categories for pin resolution, provider policy denial, credential denial, contract validation failure, redaction failure, and tenant-scope denial.
- **FR-015**: The system MUST provide unit, contract, integration, QA, Playwright, and curl evidence for the model-backed executor selection and safe mocked execution path.

### Key Entities *(include if feature involves data)*

- **Role Execution Request**: Tenant, workflow run, role node, execution mode, upstream result summaries, artifact references, and contract metadata used to execute one graph role node.
- **Governed Role Pins**: Prompt version, runtime profile version, model routing/provider version, credential readiness, and policy decision references resolved for a role node.
- **Safe Model Invocation**: Redaction-safe gateway request metadata, attempt provenance, and usage context sent through the existing model gateway path.
- **Role Output Contract**: Structured requirements for role-node outputs that determine whether a model response can become a successful graph result.
- **Role Execution Result**: Safe status, output summary, structured output, artifact references, failure category, usage, provenance, and digest returned to graph execution.
- **Model Role Evidence**: Audit-safe record or runtime evidence summary describing pin resolution, policy decisions, gateway attempt, validation result, usage, and artifact references.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Existing deterministic role-node tests and test-bench flows continue to pass without model-backed configuration or real provider credentials.
- **SC-002**: A mocked model-backed role-node execution with valid pins completes and returns a safe graph-compatible role result with usage and provenance evidence.
- **SC-003**: Missing pins, denied policy, missing credentials, cross-tenant references, unsafe output, and contract-invalid output each fail closed before graph success and expose only safe failure summaries.
- **SC-004**: Unit and integration tests prove no raw prompts, completions, secrets, provider authorization headers, private channel payloads, memory contents, unauthorized payloads, or raw provider payloads are persisted, logged, returned, screenshotted, or included in QA artifacts.
- **SC-005**: QA guide, Playwright smoke evidence, and curl regression coverage demonstrate deterministic default behavior plus the safe mocked model-backed execution path.

## Assumptions

- Spec 061 owns model-backed role-node execution and safe evidence only; iterative design review coordination, Admin design-review workspace UI, and reusable templates remain deferred to Specs 062 through 064.
- Local QA uses local-principal authentication, deterministic data setup, and mocked ModelGateway/provider behavior; no real provider, Auth0, Telegram, connector, credential, or outbound calls are required.
- Existing workflow registry, graph execution, prompt/runtime profile, model provider gateway, storage, audit, and usage services remain authoritative and are extended additively.
- Workflow graphs remain acyclic; this feature only changes role-node execution behavior inside one existing graph run.
- The implementation may add small internal diagnostic or QA routes only if needed for validation, and any new public/admin JSON route must be reflected in `curl_testing.md`.

## Testing Instructions

- Add unit coverage for executor selection, pin resolution, redaction-safe input building, output contract validation, artifact-reference handling, and safe failure categories.
- Add integration coverage for graph execution with deterministic mode, mocked model-backed mode, denied policy, missing pins, and contract-invalid output.
- Add contract coverage for any new role execution result, diagnostic, or QA-only JSON schemas introduced by this spec.
- Add QA docs for `qa061.md`, `qa061_ui.md`, `.env.qa061`, `qa061_user_guide.md`, and reviewer notes.
- Update `curl_testing.md` for any new or changed API surface and run the full multi-agent curl regression after spec validation.

## PR Review Guidance

- Confirm deterministic role execution remains unchanged for existing QA and test-bench paths.
- Confirm model-backed execution cannot send raw prompts, secrets, provider headers, private channel payloads, memory contents, unauthorized payloads, or raw external tool payloads to logs, records, responses, screenshots, or QA artifacts.
- Confirm every denied path fails closed before a provider call and records only safe diagnostic evidence.
- Confirm graph execution still returns compatible role results for success, failure, quorum, and timeline behavior.

## Documentation Impact

- Add Spec 061 plan, research, data model, contracts, quickstart, tasks, QA guide, UI walkthrough, manual QA user guide, and reviewer notes.
- Update `curl_testing.md` only for new or changed public/admin/runtime JSON contracts.
- Update `AGENTS.md` Spec Kit plan pointer during planning through the normal plan flow.
