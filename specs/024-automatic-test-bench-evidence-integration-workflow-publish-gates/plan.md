# Implementation Plan: Automatic Test Bench Evidence Integration In Workflow Publish Gates

**Branch**: `codex/024-automatic-test-bench-evidence-integration-workflow-publish-gates` | **Date**: 2026-05-04 | **Spec**: `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/spec.md`
**Input**: Feature specification from `/specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/spec.md`

## Summary

Workflow publish readiness will stop trusting copied `latest_result_status` fields and will derive required-test readiness from the existing agent test-bench database. The workflow registry service will resolve each declared required suite against the workflow tenant, current draft ID, and current draft revision ID, then feed redaction-safe evidence snapshots into validation results, publish gate responses, publish bundle summaries, and the admin publish-gate UI.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0/local-principal authorization, existing workflow registry services, existing agent test-bench services, audit/redaction helpers, Jinja2 admin templates, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: Existing PostgreSQL workflow registry and agent test-bench tables; no new table is required  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, coverage gate  
**Target Platform**: Multi-agent platform API, worker-compatible services, and server-rendered admin UI  
**Project Type**: Backend web service with server-rendered admin console  
**Performance Goals**: Publish gate evidence lookup should be bounded by declared required suites and avoid broad run scans; typical gate evaluation should remain under the existing admin request budget.  
**Constraints**: Tenant-scoped evidence only, redaction-safe summaries only, no automatic real model/tool execution during publish, no destructive data changes, no production endpoint or credential use.  
**Scale/Scope**: Workflow drafts with a small declared set of required suites; repository queries remain index-backed by tenant, suite, target, status, and target version.

## Constitution Check

- **I. Durable By Default**: PASS. Evidence comes from persisted test-bench runs and validation records; publication rechecks current evidence.
- **II. Immutable State And Memory**: PASS. Existing immutable draft revision IDs are the freshness boundary; no mutable in-memory status is authoritative.
- **III. Contract-First Agent Coordination**: PASS. Workflow `TestSuiteRequirement`, publish gate response, and evidence snapshot schemas are explicit and tested.
- **IV. Security With Practical Development Ergonomics**: PASS. Local-principal QA is supported while tenant checks and authorization remain active.
- **V. Operability Is A Product Requirement**: PASS. Validation and publish-gate events include safe status/count payloads for debugging.
- **VI. Spec-Driven Delivery**: PASS. This plan, spec, tasks, quickstart, contracts, and QA docs track the implementation.
- **VII. Test And Documentation Discipline**: PASS. Tasks include focused tests, docs, README, quickstart, and coverage gates.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Changes are limited to agent test evidence resolution, workflow validation/publish gates, UI summaries, docs, and tests.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Evidence queries include tenant IDs and fail closed for missing tenant context.
- **X. Version-Pinned Execution**: PASS. Current draft revision ID is used as target version, and published bundles record safe evidence pins.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. No real provider/tool calls are introduced; diagnostics are redaction-safe.
- **XII. Tiered Storage For Large Payloads**: PASS. No large payload storage is added; only metadata summaries are persisted.
- **XIII. Human Approval Is Durable State**: PASS. Existing publish confirmation remains unchanged and no new approval wait state is introduced.

## Design Decisions

- **Durability and failure recovery**: Required-test evidence is reloaded on every validation, publish-gate evaluation, and final publication. Saved validation results are useful for diagnostics but final publish readiness is not trusted without a fresh lookup.
- **Tenant isolation, fairness, and quotas**: `AgentTestRepository` evidence queries always include `tenant_id`. Platform-scoped workflows with required tenant tests block until a future platform evidence scope exists.
- **Subworkflow boundaries and parent-child lineage**: No new subworkflow lineage is introduced. Published workflow bundle summaries record current required-test evidence alongside existing pin summaries.
- **Version-bundle pinning and contract compatibility**: For workflow drafts, target type `workflow_revision` maps to test-bench target `workflow_draft`, target ID equals `workflow_draft_id`, and target version equals `workflow_draft_revision_id`.
- **Secret management, delegated credentials, and tool policy**: No credentials or tool calls are resolved. Evidence summaries include suite/run identifiers and status only.
- **Artifact storage and retention**: Existing test-bench artifacts remain governed by the test bench. This feature stores no new raw evidence artifacts.
- **Approval, wait-state, and resume behavior**: Not changed. Publish remains an explicit admin action guarded by validation and publish gate readiness.
- **Observability, audit, replay, and operator debugging**: Existing workflow registry audit events include publish gate status/counts. Required-test snapshots are persisted in validation JSON and publish bundle summary for safe replay context.
- **Test strategy**: Unit tests cover evidence classification. Service tests cover validation, publish gate, final publish, stale revision, manual status bypass, and cross-tenant denial. UI tests cover publish-gate summary rendering.
- **Documentation and security review notes**: Quickstart, testing instructions, PR notes, QA docs, README, and docs quickstart updates will describe repository-backed evidence and redaction checks.

## Project Structure

### Documentation (this feature)

```text
specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── workflow-publish-test-evidence.md
├── quickstart.md
├── tasks.md
├── testing-instructions.md
├── pr-review-notes.md
├── qa024.md
├── qa024_ui.md
├── qa024_user_guide.md
└── .env.qa024
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/workflow_registry/
│   ├── publish_gate.py
│   ├── reference_validation.py
│   └── service.py
├── api/schemas/
│   ├── workflow_editor.py
│   └── workflow_registry.py
├── db/repositories/
│   └── agent_tests.py
├── testing/agent_bench/
│   ├── models.py
│   └── service.py
└── web_admin/templates/workflows/
    └── publish_gate.html

tests/
├── unit/admin/
│   ├── test_publish_gate.py
│   ├── test_workflow_builder_references.py
│   └── test_workflow_registry_service.py
└── integration/api/
    └── test_admin_workflow_ui.py
```

**Structure Decision**: Keep the feature inside the existing workflow registry and agent test-bench modules. No new service boundary, frontend app, or database table is required.

## Complexity Tracking

No constitution violations require justification.
