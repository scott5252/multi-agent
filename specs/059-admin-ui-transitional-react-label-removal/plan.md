# Implementation Plan: Admin UI Transitional React Label Removal

**Branch**: `codex/059-admin-ui-transitional-react-label-removal` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/059-admin-ui-transitional-react-label-removal/spec.md`

## Summary

Remove migration-era "React" wording from production-visible admin UI copy while
preserving internal implementation identifiers and developer-only evidence
context. Add route-visible text scanning and QA059 evidence so the final admin
experience reads as the product "Admin" across shell, navigation, breadcrumbs,
document titles, command/search labels, empty/error states, redirects,
representative pages, QA screenshots, and docs.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, React 19, React Router, Vite, Vitest, Playwright  
**Storage**: PostgreSQL 16+ for durable tenant-scoped data; filesystem artifact storage for QA evidence  
**Testing**: Ruff, mypy, pytest with coverage, Vitest, TypeScript typecheck, Vite build, Spec QA, Playwright, multi-agent curl regression  
**Target Platform**: FastAPI-served React admin browser UI  
**Project Type**: Web application with backend-owned JSON contracts and React frontend  
**Performance Goals**: Visible-text scanner remains bounded to admin route contracts and representative page responses; no new unbounded database scans  
**Constraints**: Preserve authorization, tenant isolation, redaction, audit, live-data behavior, compatibility redirects, and generated contract ownership  
**Scale/Scope**: Production-visible admin shell, primary admin routes, representative domain pages, fallback/redirect states, QA docs, and screenshots

## Constitution Check

- Library-First And CLI-Transparent: PASS. The work uses existing backend builders, route contracts, scripts, and QA runners.
- Test-First Source Of Truth: PASS. Route, scanner, frontend, docs, Playwright, and curl validation are required.
- Agent And Skill Contracts Are Immutable Interfaces: PASS. No tool contracts or governed connector behavior changes are planned.
- Observability Is A Product Requirement: PASS. QA059 produces scanner reports, screenshots, verifier output, and status evidence.
- Security, Privacy, And Tenant Isolation Are Non-Negotiable: PASS. The feature changes visible terminology only and keeps redaction/authorization behavior intact.
- Operability Is A Product Requirement: PASS. The scanner and QA docs make the cleanup reviewable and repeatable.
- Versioning And Migration Discipline: PASS. No database migration is expected; generated contracts are refreshed only if schema changes require it.

## Project Structure

### Documentation

```text
specs/059-admin-ui-transitional-react-label-removal/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── transitional-label-gate.openapi.yaml
│   └── transitional-label-gate-ui.md
├── qa059.md
├── qa059_ui.md
├── qa059_user_guide.md
└── pr_notes.md
```

### Source

```text
src/multi_agent_platform/
├── admin/
│   └── migration_hardening/
│       ├── live_data_inventory.py
│       └── react_migration_hardening.py
├── api/
│   ├── routers/admin_react.py
│   └── schemas/
└── web_admin/static/react/

frontend/admin/src/
├── App.tsx
├── routes.tsx
├── components/
├── styles/
└── test/

scripts/qa/
├── seed_transitional_labels_qa059.py
└── verify_transitional_labels_qa059.py

tests/
├── contract/
├── docs/
├── integration/
├── unit/
└── performance/
```

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design And Contracts

- [data-model.md](data-model.md)
- [contracts/transitional-label-gate.openapi.yaml](contracts/transitional-label-gate.openapi.yaml)
- [contracts/transitional-label-gate-ui.md](contracts/transitional-label-gate-ui.md)
- [quickstart.md](quickstart.md)

## Phase 2: Task Planning

Tasks will be generated in `tasks.md` with file-specific backend, frontend,
scanner, docs, and validation work.

## Risk Register

- User-facing and internal "React" strings overlap heavily; mitigate with an explicit allowlist and scanner categories.
- Browser titles and fallback HTML can bypass normal React component tests; mitigate with route and Playwright assertions.
- Docs need technical implementation context; mitigate by requiring product-facing sections to say "Admin" and allowing "React" only in implementation notes.
- The final live-only scanner still has one deferred Spec 059 marker; this spec must remove or reclassify it so the final gate is clean.

## Post-Design Constitution Check

PASS. The design keeps the change terminology-focused, requires automated and
browser validation, and preserves existing security, tenancy, audit, and live
data contracts.
