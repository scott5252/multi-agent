# Implementation Plan: Model-Backed Graph Role Executor

**Branch**: `codex/061-model-backed-graph-role-executor` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/061-model-backed-graph-role-executor/spec.md`

## Summary

Add a governed model-backed role-node executor beside the existing
deterministic executor. The implementation will keep deterministic graph
execution as the default, add safe executor selection for model-backed role
nodes, resolve tenant-scoped prompt/profile/model pins through existing
configuration services, invoke `ModelGateway` with mocked or governed provider
dependencies, validate structured role outputs, store or reference large
allowed outputs safely, and return graph-compatible `RoleExecutionResult`
metadata without exposing raw prompts, completions, credentials, provider
payloads, memory contents, private payloads, or raw external tool data.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI runtime/service container, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, existing `GraphExecutionService`, `RoleNodeExecutor` protocol, `ModelGateway`, `ProviderSecretResolver`, `ModelSkillConfigService`, storage provider, usage capture, audit/timeline helpers, pytest, Ruff, mypy  
**Storage**: Existing runtime step `output_ref`/`error_ref`, gateway operation/attempt/usage records, and artifact storage references; no new migration planned unless implementation discovers a missing durable field  
**Testing**: pytest, pytest-asyncio, integration graph execution tests, contract tests for role execution schemas, Ruff, mypy, Spec QA, Playwright smoke validation, multi-agent curl runner  
**Target Platform**: FastAPI control-plane runtime worker and PostgreSQL-backed workflow execution  
**Project Type**: Backend runtime execution feature  
**Performance Goals**: Preserve existing parallel wave scheduling; model-backed executor must not add provider work for deterministic runs and must bound inline output metadata size.  
**Constraints**: Local QA uses mocked gateway/provider behavior and local-principal auth only. No real provider, Auth0, Telegram, credential, connector, or outbound calls. No raw prompts, completions, secrets, credential values, provider authorization headers, private channel payloads, memory contents, unauthorized payloads, raw provider payloads, or raw artifact bodies in persisted records, route responses, logs, screenshots, or QA artifacts.  
**Scale/Scope**: One additive runtime executor module, contract validation helpers, worker/container factory wiring, tests, QA scripts/docs, and validation manifest reconciliation for Spec 061.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Gateway operations, attempts, usage events, run steps, timeline events, and artifact references remain durable.
- Immutable State And Memory: PASS. Model-backed results become append-only runtime evidence and do not mutate memory or raw provider payloads.
- Contract-First Agent Coordination: PASS. Role output validation and `RoleExecutionResult` contracts gate graph success.
- Security With Practical Development Ergonomics: PASS. Production provider access remains governed; local QA uses explicit mocked gateway/provider paths.
- Operability Is A Product Requirement: PASS. Safe failure categories, timeline evidence, gateway attempts, usage capture, QA docs, and curl regression are required.
- Spec-Driven Delivery: PASS. Work follows specify, clarify, plan, tasks, analyze, implement, and validation phases.
- Test And Documentation Discipline: PASS. Unit, contract, integration, QA docs, Playwright, and curl regression evidence are planned.
- Clear Ownership And Small Safe Changes: PASS. Changes are limited to runtime role execution and worker dependency wiring.
- Tenant Isolation And Fair Scheduling: PASS. Tenant context is required for pin resolution, gateway invocation, artifact handling, and usage evidence.
- Version-Pinned Execution: PASS. Existing runtime bundle and config pinning remain authoritative for prompt/profile/model references.
- Secret Hygiene And Controlled Tool Access: PASS. Credentials resolve only inside `ModelGateway`/secret resolver and never enter role outputs.
- Tiered Storage For Large Payloads: PASS. Large allowed outputs use artifact references and digests.
- Human Approval Is Durable State: PASS. No manual-resolution semantics change in this spec.

## Project Structure

### Documentation (this feature)

```text
specs/061-model-backed-graph-role-executor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── model-backed-role-executor.md
│   └── model-backed-role-executor-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── runtime/orchestration/
│   ├── graph_roles.py
│   ├── graph_execution.py
│   ├── model_backed_roles.py
│   └── role_output_contracts.py
├── runtime/versioning.py
├── bootstrap/
│   ├── container.py
│   └── worker.py
└── workers/orchestration.py

tests/
├── contract/test_model_backed_role_executor_contracts.py
├── integration/runtime/test_model_backed_graph_execution.py
├── unit/runtime/orchestration/test_graph_roles.py
├── unit/runtime/orchestration/test_model_backed_roles.py
├── unit/bootstrap/test_worker_gateway_bootstrap.py
└── unit/guardrails/test_model_gateway_only_provider_calls.py

scripts/qa/
├── seed_model_backed_roles_qa061.py
└── verify_model_backed_roles_qa061.py
```

**Structure Decision**: Keep model-backed execution under
`runtime/orchestration` because it plugs into the existing `RoleNodeExecutor`
protocol and graph service. Reuse existing model gateway, usage, config, and
storage domains rather than introducing a design-review-specific executor.

## Complexity Tracking

No constitution violations are expected.

## Phase 0: Research

Research covers executor selection, model/prompt/profile pin resolution, safe
gateway input construction, output contract validation, artifact references,
usage/provenance, worker wiring, deterministic QA preservation, and curl/API
impact. Findings are recorded in [research.md](research.md).

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](data-model.md)
- [contracts/model-backed-role-executor.md](contracts/model-backed-role-executor.md)
- [contracts/model-backed-role-executor-ui.md](contracts/model-backed-role-executor-ui.md)
- [quickstart.md](quickstart.md)

## Migration Notes

- No Alembic migration is planned for Spec 061.
- Persist model-backed role success/failure through existing runtime run-step
  `output_ref`/`error_ref`, timeline events, gateway operations/attempts,
  usage events, and artifact metadata where needed.
- If implementation discovers that existing runtime/gateway tables cannot
  represent a required safe reference, stop and revise this plan before adding
  schema.

## Post-Design Constitution Check

- The design keeps deterministic execution default, requires tenant-scoped
  governed pin resolution before provider work, validates output contracts
  before graph success, stores only safe metadata/artifact references, and uses
  mocked gateway behavior for QA.
- No new constitution violation was introduced by Phase 1 design.
