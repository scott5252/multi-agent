# Research: Model-Backed Graph Role Executor

## Decision: Preserve `RoleNodeExecutor` As The Extension Point

**Rationale**: `GraphExecutionService` already accepts a `RoleNodeExecutor` and
the worker currently falls back to `DeterministicRoleNodeExecutor`. A composite
or factory-backed executor can preserve deterministic execution while routing
explicit model-backed role contexts to a new executor.

**Alternatives considered**:

- Replace `GraphExecutionService`: rejected because it increases graph runtime
  blast radius.
- Add a design-review-specific runtime path: rejected because role execution is
  a platform primitive and later design-review specs should reuse it.

## Decision: Resolve Model/Prompt Pins Through Existing Config Services

**Rationale**: `ModelSkillConfigService.resolve_model_step` already records
runtime model/prompt decisions, uses scope selectors, and returns safe model and
prompt reference metadata. Reusing it keeps version pinning and policy evidence
consistent with Specs 012/025.

**Alternatives considered**:

- Read active model routes directly in the executor: rejected because it would
  bypass runtime decision evidence.
- Store new pin columns on runtime steps: rejected because existing runtime
  decisions and gateway context already carry pin evidence.

## Decision: Use Existing `ModelGateway` And Mocked Adapters For QA

**Rationale**: `RuntimeOrchestrationService.invoke_model_gateway_step` already
builds `GatewayInvocationContext` with workflow, step, prompt, profile,
idempotency, and policy metadata. Spec 061 should use this route with mocked
adapters in QA rather than direct provider SDK calls.

**Alternatives considered**:

- Call provider adapters directly: rejected by the model gateway guardrail.
- Require live provider probes for QA: rejected because the scenario roadmap
  requires deterministic local QA unless explicitly approved.

## Decision: Validate Role Outputs Before Graph Success

**Rationale**: Graph execution treats a role result as successful only after
`RoleExecutionResult.succeeded` is true. The model-backed executor must parse
gateway content into structured output, validate required safe fields against
the role output contract, redact values, compute a digest, and only then return
success.

**Alternatives considered**:

- Accept raw model content and let downstream nodes validate: rejected because
  unsafe or malformed output would enter graph state.
- Store only a text summary: rejected because quorum, handoff, and test-bench
  flows require structured role evidence.

## Decision: Use Artifact References For Large Allowed Outputs

**Rationale**: The constitution prohibits PostgreSQL as a blob store. Inline
role output metadata should remain bounded; large allowed structured output can
be stored through the configured storage provider and represented by a safe
artifact reference plus digest.

**Alternatives considered**:

- Persist raw output in runtime step JSON: rejected due tiered storage and
  redaction risk.
- Drop large output: rejected because later handoff and test-bench evidence may
  need references.

## Decision: No Public API Change Is Planned

**Rationale**: Spec 061 changes backend runtime behavior. Existing runtime and
debug APIs should display model-backed evidence through already-supported
run-step, timeline, gateway, and usage records. Curl regression still runs, but
`curl_testing.md` only changes if implementation requires a new or changed JSON
route.

**Alternatives considered**:

- Add an admin diagnostic route for model-backed roles: deferred unless needed
  for validation, because internal unit/integration and QA scripts can prove
  the executor without increasing API surface.
