# Implementation Plan: Generic Scenario Intake And Durable Draft Blueprint

**Branch**: `codex/075-generic-scenario-intake-and-durable-draft-blueprint` | **Date**: 2026-05-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/075-generic-scenario-intake-and-durable-draft-blueprint/spec.md`

## Summary

Spec 075 implements scenario-neutral intake, workflow key normalization, generic editable blueprint generation, durable draft creation, revision-safe saves, and tutorial label guardrails. The approach is additive inside the existing React Admin workflow and Console Home architecture. It reuses existing workflow draft create action, full document save action, validation refresh, and generated React API contracts; no new route family, new engine, live provider call, or raw JSON happy path is introduced.

## Technical Context

**Language/Version**: Python 3.12, TypeScript strict mode, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, PostgreSQL, generated React Admin contracts, Testing Library, Vitest, Playwright  
**Storage**: Existing PostgreSQL workflow registry, draft, revision, validation, publish, artifact, and test-bench state  
**Testing**: pytest, Vitest, frontend typecheck, Vite build, generated contract freshness, QA docs validation, Spec QA, Playwright  
**Target Platform**: Local React Admin and FastAPI app under AUTH_MODE=local_principal for QA  
**Project Type**: Web application with FastAPI backend and React Admin frontend  
**Performance Goals**: Bounded 1280 x 800 wizard steps, no large scroll panels, no extra backend round trips beyond existing envelope and mutation refreshes  
**Constraints**: Existing APIs first, backend-owned authorization and readiness, no raw secret or transcript exposure, no tutorial scenario hard-coding  
**Scale/Scope**: Tenant-scoped admin workflows, clean or resumed draft setup, deterministic QA data only  

## Constitution Check

- Durable state remains in workflow registry, draft revisions, validation, publish readiness, test evidence, and runtime surfaces.
- React renders and submits authorized actions but does not become source of truth for publish or tenant decisions.
- Local QA avoids real providers, connectors, Telegram, Auth0, credentials, and external side effects.
- Redaction, safe summaries, and tenant boundaries are preserved in UI, docs, screenshots, tests, and logs.
- Operational evidence includes tests, QA docs, status files, validation manifests, and final README/user guide updates.

## Project Structure

```text
frontend/admin/src/components/home/
frontend/admin/src/components/workflows/
frontend/admin/src/styles/admin.css
frontend/admin/src/api/generated/reactAdminApi.ts
src/multi_agent_platform/api/routers/admin_react.py
specs/075-generic-scenario-intake-and-durable-draft-blueprint/
specs/_autopilot/wizard-ui-roadmap/075-generic-scenario-intake-and-durable-draft-blueprint/
```

## Phase 0: Research

- Reviewed Console Home, Admin shell, App route dispatch, workflow builder, create, lookups, validation, publish, Test Bench, runtime, operations, and graph foundations from Specs 031 through 073.
- Confirmed existing workflow APIs are sufficient for this spec slice.
- Confirmed QA must use visible UI controls after local login and keep curl checks secondary.
- Confirmed no new persistent database field or Alembic migration is required.

## Phase 1: Design

- Add or reuse bounded React components for wizard steps.
- Keep all saves through existing create/save/validate/publish actions and refresh durable state after mutation.
- Preserve tenant query scope in navigation and handoff links.
- Page any collection that could overflow the fixed frame.
- Provide CommonState recovery for loading, dependency unavailable, denied, empty, stale, and blocked states.

## Phase 2: Task Strategy

- Implement helpers before page wiring.
- Add focused helper/component tests before broad app tests.
- Update backend home envelope tests where admin JSON changes.
- Generate QA docs and validation artifacts before marking queue validation complete.
- Record curl_testing.md coverage decision or update when admin JSON behavior changes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected |
|-----------|------------|------------------------------|
| None | The implementation composes existing APIs and React surfaces. | No new backend route family or persistence layer was needed. |
