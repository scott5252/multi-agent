# Implementation Plan: Modern Admin Shell And Design System

**Branch**: `codex/027-modern-admin-shell-and-design-system` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/027-modern-admin-shell-and-design-system/spec.md`

## Summary

Build on the Spec 026 React admin foundation by replacing the minimal shell with
a reusable modern admin shell and local design system. The implementation keeps
backend navigation and scope contracts authoritative, adds React primitives and
common states for later domain pages, introduces safe command/search and saved
filter presentation metadata where available, and validates accessibility,
responsive behavior, redaction, and dual-auth-mode access.

## Technical Context

**Language/Version**: Python 3.12; TypeScript 5.8; React 19; Node `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, Jinja2, Vite, React Router, Testing Library, Vitest, Playwright, optional `lucide-react` icons  
**Storage**: PostgreSQL for existing saved filters, audit, tenants, and admin domain state; no new durable tables expected  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Vitest, Testing Library, Playwright QA scripts, Ruff, mypy  
**Target Platform**: FastAPI-served admin web application with built React assets under `/admin/static/react`  
**Project Type**: Web app with Python backend contracts and TypeScript frontend workspace  
**Performance Goals**: Shell bootstrap and rendering stay bounded to existing navigation/scope data; browser shell remains responsive at desktop and mobile viewports  
**Constraints**: Backend remains authoritative for authorization, scope, navigation, saved-filter links, command/search metadata, audit, and redaction; Jinja routes remain available  
**Scale/Scope**: Shared shell components for all future React admin domain pages; no domain page migration in Spec 027

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Tenant isolation remains backend-enforced; browser components only render authorized contract data.
- Redaction rules remain fail-closed; command/search, notifications, and saved filter labels use safe summaries only.
- No production provider, Telegram, connector, credential, Auth0, or external tool calls are required for local/CI validation.
- Existing Jinja routes remain reversible fallbacks.
- Tests cover backend contracts/routes, frontend components, keyboard/responsive behavior, QA docs, and Playwright evidence.
- The implementation can preserve at least 90 percent coverage through focused tests plus the existing full suite.

**Gate Status**: PASS. No constitution violation is required for the planned shell/design-system work.

## Project Structure

### Documentation (this feature)

```text
specs/027-modern-admin-shell-and-design-system/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── react-admin-shell.openapi.yaml
├── tasks.md
├── qa027.md
├── qa027_ui.md
├── qa027_user_guide.md
├── .env.qa027
└── pr_notes.md
```

### Source Code (repository root)

```text
frontend/admin/
├── package.json
├── src/
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts
│   │   └── generated/reactAdminApi.ts
│   ├── components/
│   │   ├── shell/
│   │   ├── primitives/
│   │   ├── states/
│   │   └── savedFilters/
│   ├── styles/
│   │   ├── admin.css
│   │   └── tokens.css
│   └── test/
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_react.py
└── web_admin/templates/admin_react/app.html
tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
└── unit/api/test_admin_react_schema.py
```

**Structure Decision**: Extend the Spec 026 frontend/admin workspace and backend React admin schema/router rather than creating a second app. Add shared components under `frontend/admin/src/components/` and keep backend contract extensions in the existing React admin schema/router boundary.

## Phase 0: Research

Research outputs are captured in [research.md](./research.md).

Key decisions:

- Use local React primitives plus `lucide-react` icons instead of a large headless UI framework for Spec 027.
- Keep command/search metadata limited to authorized navigation destinations and safe labels until deeper object search has a separate backend policy.
- Add design tokens in CSS custom properties owned by `frontend/admin`.
- Keep saved-filter UI presentation read-only or link-based unless an existing backend action already validates mutations.
- Validate mobile and keyboard behavior with Playwright screenshots and component tests.

## Phase 1: Design

Design outputs:

- [data-model.md](./data-model.md)
- [contracts/react-admin-shell.openapi.yaml](./contracts/react-admin-shell.openapi.yaml)
- [quickstart.md](./quickstart.md)

Contract additions remain additive to Spec 026:

- Shell chrome metadata.
- Common state descriptors.
- Command/search destination summaries.
- Saved-filter chip summaries.
- Notification summaries.
- Design token version metadata.

## Phase 1 Constitution Re-check

- Backend remains authoritative for all protected metadata.
- React routes do not retire Jinja routes.
- Contract additions use safe summaries and generated TypeScript validation.
- QA remains deterministic through `.env.qa027`, local-principal login, and Auth0-shaped route tests.

**Gate Status**: PASS.

## Complexity Tracking

No constitution violations are introduced.
