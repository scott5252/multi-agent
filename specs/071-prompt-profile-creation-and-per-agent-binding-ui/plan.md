# Implementation Plan: Prompt Profile Creation And Per-Agent Binding UI

**Branch**: `codex/071-prompt-profile-creation-and-per-agent-binding-ui` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/071-prompt-profile-creation-and-per-agent-binding-ui/spec.md`

**Note**: This plan is filled for the autonomous workflow setup roadmap and uses the generated Spec 071 prompt bundle.

## Summary

Spec 071 adds prompt/runtime profile creation, selection, validation, publication/activation, and per-agent binding controls to the React Workflow Registry builder. The implementation will reuse existing prompt runtime and agent profile backend services where they already own durable prompt/profile state, extend generated React contract output to include those schemas, add workflow-builder lookups and React client helpers for safe prompt/profile catalogs, and persist role bindings through the Spec 069 full workflow document save contract.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv  
**Storage**: Existing PostgreSQL prompt lineage/draft/version, agent runtime profile draft/version, model-skill config, workflow registry, audit, and workflow document tables; no new migration planned unless implementation discovers missing durable idempotency or binding evidence fields  
**Testing**: pytest/httpx integration and unit tests, generated TypeScript freshness check, Vitest/Testing Library, Playwright UI runner, QA docs validation, multi-agent curl regression  
**Target Platform**: FastAPI control-plane app with React Admin UI served by backend static assets  
**Project Type**: Web application with backend domain services and React Admin frontend  
**Performance Goals**: Prompt/profile catalog and workflow builder bootstrap must remain bounded to visible tenant/platform records and avoid N+1 queries in QA fixture sizes; UI interactions should complete without visible layout shift at desktop and mobile viewports  
**Constraints**: Raw prompt content may appear only inside authorized edit controls; provider credentials, provider payloads, raw completions, private data, raw test transcripts, stack traces, local paths, and unauthorized tenant labels must never reach safe display surfaces, screenshots, logs, docs, exports, or audit summaries  
**Scale/Scope**: Spec 071 covers prompt/profile create/select/validate/publish/activate and role binding for workflow setup. Test evidence creation remains Spec 072 and end-to-end runtime launch remains Spec 073.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. Prompt/profile records are durable backend domain state; workflow role bindings save through durable workflow draft revisions with idempotency and stale recovery inherited from Spec 069.
- **II. Immutable State And Memory**: PASS. Published prompt versions and activated profile versions are immutable references; mutable browser draft state is not runtime truth.
- **III. Contract-First Agent Coordination**: PASS. Prompt/profile references are explicit workflow document contracts and generated React contracts.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0 production behavior and local-principal QA remain required for protected prompt/profile actions.
- **V. Operability Is A Product Requirement**: PASS. Validation, readiness, stale, conflict, denied, and blocked states are first-class UI and QA evidence.
- **VI. Spec-Driven Delivery**: PASS. Spec, plan, data model, contracts, tasks, QA docs, and validation are required before moving to Spec 072.
- **VII. Test And Documentation Discipline**: PASS. Plan requires backend, frontend, QA docs, Playwright, generated type, and curl regression coverage.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Work is scoped to prompt/profile contracts, workflow builder lookups/UI, API client helpers, tests, docs, and QA seed data.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Catalog visibility and mutation eligibility remain backend-owned with tenant/platform grants.
- **X. Version-Pinned Execution**: PASS. Workflow roles store immutable prompt/profile version references suitable for later runtime bundle pinning.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. The feature excludes real provider calls and keeps credentials/provider payloads out of UI and artifacts.
- **XII. Tiered Storage For Large Payloads**: PASS. No large payload storage change; prompt template size remains bounded by existing prompt contracts.
- **XIII. Human Approval Is Durable State**: PASS. No new approval/resume semantics are introduced in Spec 071.

## Project Structure

### Documentation (this feature)

```text
specs/071-prompt-profile-creation-and-per-agent-binding-ui/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── prompt-profile-binding-ui.md
├── tasks.md
├── qa071.md
├── qa071_ui.md
├── qa071_user_guide.md
└── .env.qa071
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_prompts.py
│   ├── routers/admin_agent_profiles.py
│   ├── routers/admin_react.py
│   └── schemas/
│       ├── prompts.py
│       ├── agent_profiles.py
│       └── admin_workflow_builder.py
├── admin/
│   ├── governance.py
│   ├── workflow_builder.py
│   └── workflow_registry/
│       ├── validation.py
│       └── reference_validation.py
├── db/repositories/
│   ├── prompts.py
│   ├── agent_profiles.py
│   └── workflow_registry.py
├── prompts/
└── agents/

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/
│   ├── governance/
│   └── workflows/
│       ├── WorkflowPromptProfileBinder.tsx
│       ├── workflowPromptProfileBinding.ts
│       └── WorkflowBuilderPage.tsx
└── test/

tests/
├── contract/
├── integration/
└── unit/

scripts/
├── frontend/generate_admin_react_types.py
└── qa/seed_workflow_prompt_profile_qa071.py
```

**Structure Decision**: Extend existing prompt/runtime backend domains and the existing React Workflow Registry builder. Do not create a second prompt/profile app or alternate workflow editor.

## Phase 0 Research

Research output is captured in [research.md](./research.md).

## Phase 1 Design

Design output is captured in [data-model.md](./data-model.md), [contracts/prompt-profile-binding-ui.md](./contracts/prompt-profile-binding-ui.md), and [quickstart.md](./quickstart.md).

## Post-Design Constitution Check

- **Durability and versioning**: PASS. Binding references stay in workflow draft documents and point at immutable prompt/profile versions.
- **Tenant isolation**: PASS. Prompt/profile catalogs and mutations are filtered by backend authorization and scope grants.
- **Secret and raw prompt hygiene**: PASS. Raw prompt content is limited to authorized editor forms and omitted from screenshots and safe summaries.
- **Testing and documentation**: PASS. The design requires QA docs, Playwright desktop/mobile flows, focused backend/frontend tests, generated types, and curl review.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
