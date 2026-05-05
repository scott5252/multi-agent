# Requirements Quality Checklist: React Workflow Builder

**Feature**: `specs/030-react-workflow-builder/spec.md`  
**Created**: 2026-05-05

## Content Quality

- [x] No implementation details leak into user-facing requirements beyond required platform/API boundaries.
- [x] User stories are prioritized and independently testable.
- [x] Acceptance scenarios use Given/When/Then form.
- [x] Edge cases cover stale revisions, evidence staleness, dependency failures, large workflows, and tenant isolation.
- [x] Requirements describe dual-auth-mode coverage.
- [x] Requirements state fail-closed authorization, tenant, audit, and redaction behavior.
- [x] Requirements preserve existing Jinja workflow editor fallback during migration.
- [x] Requirements avoid live provider, Telegram, credential, and connector calls in local QA.

## Completeness

- [x] Functional requirements include protected React routes and backend-owned contracts.
- [x] Functional requirements include guided metadata, references, graph, validation, publish, and revision workflows.
- [x] Functional requirements include generated TypeScript contract expectations.
- [x] Functional requirements include keyboard-accessible graph alternatives.
- [x] Functional requirements include read-only JSON inspector behavior.
- [x] Functional requirements include repository-backed required test evidence.
- [x] Functional requirements include explicit save and stale-conflict behavior.
- [x] Functional requirements include QA docs, Playwright, and full Spec QA evidence.

## Clarification Recording

- [x] Semantic saves remain explicit backend submissions. (autopilot)
- [x] Graph layout annotations are non-authoritative. (autopilot)
- [x] Graph execution semantics come from backend validation. (autopilot)
- [x] Advanced JSON is read-only and collapsed by default. (autopilot)
- [x] Validation refreshes on demand and after saves. (autopilot)
- [x] Publish gate is a guided review. (autopilot)
- [x] Large local validation supports 100-node workflows. (autopilot)
- [x] React is required for the new builder while old Jinja editor remains fallback during migration. (autopilot)

## Readiness

- [x] No `[NEEDS CLARIFICATION]` markers remain.
- [x] Assumptions are explicit and safe.
- [x] Success criteria are measurable.
- [x] Security, tenant isolation, redaction, and audit uncertainty are stop conditions.
