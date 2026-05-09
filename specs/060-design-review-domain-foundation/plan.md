# Implementation Plan: Design Review Domain Foundation

**Branch**: `codex/060-design-review-domain-foundation` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/060-design-review-domain-foundation/spec.md`

## Summary

Add the first durable backend domain for the Design Reviewer Council scenario.
The implementation will introduce tenant-scoped design review tables, repository
operations, domain service rules, Pydantic contracts, and authenticated admin
JSON routes for sessions, revisions, rounds, assignments, verdicts, quorum
decisions, manual decisions, and handoff metadata. The feature is explicitly
backend-only: no live model calls, no coordinator auto-launch, no cyclic runtime
graph behavior, and no Admin workspace UI are added in Spec 060.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, Alembic, PostgreSQL 16+, existing local-principal/Auth0 authorization, audit helpers, storage/artifact-reference conventions, pytest, Ruff, mypy  
**Storage**: PostgreSQL for transactional design review records; artifact metadata references only for design packets, verdict outputs, and handoffs  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Alembic migration validation, Ruff, mypy, Spec QA, Playwright smoke validation, multi-agent curl runner  
**Target Platform**: FastAPI admin/control-plane service with PostgreSQL-backed tenant data  
**Project Type**: Backend web service feature  
**Performance Goals**: Session list/detail queries remain tenant-filtered and bounded; detail responses avoid unbounded eager loading by using explicit per-session relationship limits.  
**Constraints**: No live model, Auth0, Telegram, connector, provider, or outbound calls. No raw prompts, completions, secrets, credential values, provider authorization headers, private channel payloads, memory contents, unauthorized payloads, raw external tool payloads, raw artifact bodies, storage URLs, local filesystem paths, or stack traces in persisted records, responses, logs, docs, screenshots, or QA artifacts.  
**Scale/Scope**: One additive design-review domain package, one migration, one schema module, one router, model/repository/service tests, integration routes, QA docs, curl coverage, and validation manifest updates for Spec 060.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Sessions, revisions, evidence records, manual decisions, handoffs, and idempotency keys are persisted.
- Immutable State And Memory: PASS. Revisions, assignments, verdicts, quorum decisions, manual decisions, and handoffs are immutable or append-only evidence.
- Contract-First Agent Coordination: PASS. Backend-owned Pydantic/OpenAPI contracts define the boundary before later coordinator and executor work.
- Security With Practical Development Ergonomics: PASS. Production auth remains Auth0-shaped and local QA uses explicit local-principal authorization checks.
- Operability Is A Product Requirement: PASS. Audit-safe events, route evidence, QA guides, and curl coverage are required.
- Spec-Driven Delivery: PASS. Work follows specify, clarify, plan, tasks, analyze, implement, and validation phases.
- Test And Documentation Discipline: PASS. Unit, repository, contract, integration, QA docs, Playwright, and curl regression are planned.
- Clear Ownership And Small Safe Changes: PASS. Spec 060 is bounded to backend domain foundation and docs.
- Tenant Isolation And Fair Scheduling: PASS. Tenant context is explicit in models, repositories, services, routes, tests, and curl commands.
- Version-Pinned Execution: PASS. This spec stores workflow bundle/profile/prompt/provider references as metadata and does not start runtime execution.
- Secret Hygiene And Controlled Tool Access: PASS. Records store references, summaries, digests, and provenance only.
- Tiered Storage For Large Payloads: PASS. Raw artifacts are not stored in PostgreSQL; only artifact references and digests are stored.
- Human Approval Is Durable State: PASS. Manual decisions are append-only durable records with actor, type, rationale, and idempotency.

## Project Structure

### Documentation (this feature)

```text
specs/060-design-review-domain-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── design-review-domain.openapi.yaml
│   └── design-review-domain-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/design_review/
│   ├── __init__.py
│   ├── models.py
│   ├── redaction.py
│   └── service.py
├── api/
│   ├── routers/admin_design_review.py
│   └── schemas/design_review.py
├── db/
│   ├── models/design_review.py
│   ├── models/__init__.py
│   └── repositories/design_review.py
└── api/main.py

alembic/versions/
└── 0021_design_review_domain.py

tests/
├── contract/test_design_review_contracts.py
├── integration/api/test_admin_design_review_api.py
├── unit/admin/design_review/
└── unit/db/test_design_review_repository.py

scripts/qa/
├── seed_design_review_qa060.py
└── verify_design_review_qa060.py
```

**Structure Decision**: Add a dedicated `admin/design_review` backend domain
because design review sessions are an admin scenario surface, while durable
tables and repositories live under the existing SQLAlchemy model/repository
boundaries. Keep API contracts under `/admin/design-reviews` rather than
`/admin/app/design-reviews` until the Admin workspace is added in Spec 063.

## Complexity Tracking

No constitution violations are expected.

## Phase 0: Research

Research covers table ownership, immutability/idempotency, tenant authorization,
safe artifact metadata, audit events, route shape, migration compatibility, and
QA/curl validation. Findings are recorded in [research.md](research.md).

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](data-model.md)
- [contracts/design-review-domain.openapi.yaml](contracts/design-review-domain.openapi.yaml)
- [contracts/design-review-domain-ui.md](contracts/design-review-domain-ui.md)
- [quickstart.md](quickstart.md)

## Migration Notes

- Add one Alembic migration after the current head for the design-review tables
  and indexes.
- Use UUID primary keys, tenant foreign keys, created/updated timestamps, and
  explicit uniqueness constraints for `(tenant_id, idempotency_key)` where
  retries must be deduplicated.
- Prefer nullable foreign-key references for workflow bundle, prompt/profile,
  provider, runtime run, and artifact metadata so Spec 060 can land before
  coordinator/model/template specs.
- Do not backfill or mutate existing workflow, runtime, provider, prompt,
  test-bench, or admin data.

## Post-Design Constitution Check

- Durable records, tenant filters, idempotency, append-only evidence, safe
  summaries, artifact-reference boundaries, and local/Auth0 validation remain
  covered by the design artifacts.
- No new constitution violation was introduced by Phase 1 design.
