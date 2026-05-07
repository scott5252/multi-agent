# Feature Specification: Jinja Infrastructure Decommission

**Feature Branch**: `codex/047-jinja-infrastructure-decommission`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Remove the remaining Jinja runtime infrastructure after Specs 038 through 046, prove no runtime path imports or renders Jinja, keep safe non-Jinja redirects for old browser URLs, and document the React-only browser UI."

## Clarifications

### Session 2026-05-07

- Q: Should the final feature delete the entire server-side template tree? -> A: (autopilot) Yes. Specs 039 through 046 have bounded domain parity evidence, so `web_admin/templates` is removed and React/static HTML helpers serve browser pages.
- Q: Should Vite output under `web_admin/static/react` remain? -> A: (autopilot) Yes. Built React assets and the manifest remain because they are the browser UI delivery mechanism.
- Q: How should old browser URLs behave after infrastructure removal? -> A: (autopilot) Keep non-Jinja redirect or safe compatibility handlers for one release and test representative old URLs for tenant-safe direct-link behavior.
- Q: Can `jinja2` be removed from project dependencies? -> A: (autopilot) Yes, after runtime import scanners and the full quality suite prove no source path imports `jinja2`, `Jinja2Templates`, `TemplateResponse`, or `workflow_ui_templates`.
- Q: What does rollback mean after full removal? -> A: (autopilot) Rollback is redeploying the previous release; no runtime toggle re-enables Jinja in this codebase.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Serve Browser UI Without Jinja Runtime (Priority: P1)

An authenticated platform or tenant user opens React admin, migration, local login, or user-facing run browser links and receives React-hosted HTML or a safe non-Jinja redirect without any template provider, template directory, or Jinja dependency loaded at runtime.

**Why this priority**: The final roadmap step is incomplete if any runtime path can still render server-side templates.

**Independent Test**: Run import and route scanner tests over `src/multi_agent_platform`, open representative admin and `/runs` links through backend tests, and verify no runtime source imports `jinja2`, `Jinja2Templates`, `TemplateResponse`, or `workflow_ui_templates`.

**Acceptance Scenarios**:

1. **Given** the application container is built, **When** tests inspect the container, **Then** it has no template renderer member and starts without importing Starlette templating.
2. **Given** `/admin/app`, `/admin/app/migration`, `/auth/local-login`, `/runs`, `/runs/new`, and `/runs/{run_id}` are opened, **When** the request is authenticated or safely denied, **Then** each path returns React HTML, local static HTML, redirect, or safe problem without rendering a template.
3. **Given** the source tree is scanned, **When** scanner tests inspect Python runtime files, **Then** no forbidden Jinja runtime import or template response symbol appears.

---

### User Story 2 - Remove Dead Templates, Static Assets, And Dependency Entries (Priority: P2)

A maintainer can inspect the repository and see that server-side template files, legacy Jinja-only static files, obsolete template provider wiring, and dependency entries are gone while React build artifacts remain.

**Why this priority**: Dependency and dead-file removal prevents accidental reintroduction and simplifies future browser work.

**Independent Test**: Verify `web_admin/templates` is absent, legacy static JS/CSS assets are absent, `pyproject.toml` and `uv.lock` no longer include `jinja2`, and Vite manifest/assets still serve React.

**Acceptance Scenarios**:

1. **Given** the repository after implementation, **When** file scanners inspect `src/multi_agent_platform/web_admin`, **Then** no server-side templates or legacy static assets remain outside `static/react`.
2. **Given** dependency metadata is inspected, **When** `pyproject.toml` and `uv.lock` are searched, **Then** `jinja2` is absent from direct project requirements.
3. **Given** React assets are built, **When** `/admin/app/manifest.json` is requested, **Then** the response remains safe and never exposes local paths.

---

### User Story 3 - Show Final Decommission Evidence In React (Priority: P3)

An operator opens the migration dashboard and sees a React-only decommission summary with zero blocked server-rendered surfaces, final redaction and tenant sweeps, rollback guidance, and direct-link evidence.

**Why this priority**: Operators need a browser-verifiable handoff that the migration is complete and that rollback is operational, not a hidden code-only change.

**Independent Test**: Run React component tests and Playwright against `/admin/app/migration`, expecting React-only decommission language and no stale fallback guidance.

**Acceptance Scenarios**:

1. **Given** `/admin/app/migration` is opened as a platform admin, **When** the dashboard loads, **Then** it states the browser UI is React-only and no retained Jinja fallback remains.
2. **Given** tenant users open the migration dashboard, **When** data is scoped, **Then** they see only authorized route evidence without unauthorized tenant labels.
3. **Given** docs and QA artifacts are reviewed, **When** redaction sweeps run, **Then** they contain no raw secrets, raw prompts, raw payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

### Edge Cases

- Missing React assets still return a small non-Jinja HTML fallback that does not expose local paths.
- Missing authentication still returns existing auth-required behavior before route data is loaded.
- Cross-tenant migration or run links remain safe 403/redirect paths and do not disclose unauthorized data.
- Local login remains available in `AUTH_MODE=local_principal` without referencing deleted CSS.
- Old route compatibility handlers are retained only as redirects or safe problem responses, not template renderers.
- Dependency removal must not delete Vite React assets, static manifest serving, or generated TypeScript contracts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST remove server-side template container wiring and MUST NOT expose a `workflow_ui_templates` or equivalent renderer on the application container.
- **FR-002**: Runtime Python source under `src/multi_agent_platform` MUST NOT import `jinja2`, `starlette.templating.Jinja2Templates`, use `TemplateResponse`, or call a template renderer.
- **FR-003**: `src/multi_agent_platform/web_admin/templates` MUST be removed and scanner tests MUST fail if any server-side template file is reintroduced there.
- **FR-004**: Legacy static files used only by retired Jinja pages MUST be removed while `src/multi_agent_platform/web_admin/static/react` remains intact.
- **FR-005**: `pyproject.toml` and `uv.lock` MUST remove the direct `jinja2` dependency after scanners prove no runtime import remains.
- **FR-006**: Local login MUST remain a safe non-Jinja HTML route without referencing deleted static CSS or exposing unsafe redirect targets.
- **FR-007**: The React migration dashboard MUST present final decommission evidence rather than retained fallback guidance and MUST remain accessible at `/admin/app/migration`.
- **FR-008**: Representative old browser URLs from admin workspaces and user-facing `/runs` MUST remain covered by tests as redirects, aliases, React hosts, or safe non-Jinja responses.
- **FR-009**: Backend tests MUST prove Auth0-shaped and local-principal authorization behavior for React app, migration, direct-link, and local-login paths.
- **FR-010**: Frontend tests and Playwright validation MUST prove local-principal users can use the React-only admin and run journeys after template removal.
- **FR-011**: Docs, README, quickstarts, QA guides, and migration notes MUST describe the browser UI as React-only and must not present Jinja fallback as available in the current release.
- **FR-012**: QA artifacts, screenshots, exported evidence, logs, and docs MUST not expose raw secrets, credential values, raw prompts, raw completions, raw run payloads, memory contents, private messages, raw tool payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

### Key Entities *(include if feature involves data)*

- **Decommission Evidence**: Safe summary of final scanner, route, dependency, docs, redaction, tenant isolation, and Playwright proof.
- **Runtime Import Scan**: Deterministic scan over runtime source files that fails on Jinja runtime symbols.
- **Compatibility Redirect**: Legacy browser route response that preserves safe tenant/query context without rendering a template.
- **React Host Fallback**: Minimal non-Jinja HTML returned when built assets are missing.
- **Dependency Metadata**: `pyproject.toml` and `uv.lock` project requirement state after dependency removal.
- **Rollback Plan**: Operational guidance that rollback means redeploying the previous release rather than toggling a template renderer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Scanner tests find zero runtime references to `jinja2`, `Jinja2Templates`, `TemplateResponse`, or `workflow_ui_templates`.
- **SC-002**: File scanners find zero files under `src/multi_agent_platform/web_admin/templates` and zero legacy static assets outside `static/react`.
- **SC-003**: `pyproject.toml` and `uv.lock` contain no direct project `jinja2` requirement.
- **SC-004**: Backend tests cover representative React app, migration, local login, and `/runs` compatibility paths with local-principal and Auth0-shaped principals.
- **SC-005**: Frontend tests and Playwright evidence show React-only migration and user-facing run journeys after infrastructure removal.
- **SC-006**: QA docs, route evidence, and screenshots pass redaction and tenant isolation sweeps.
- **SC-007**: Full Spec QA, ruff, format check, mypy, generated React contract check, frontend typecheck/test/build, and Playwright validation pass for `qa047`.

## Assumptions

- Specs 039 through 046 have already completed all bounded surface removals and validation.
- React static assets remain the browser UI delivery mechanism and are not considered legacy static files.
- Direct-link compatibility is preserved through non-Jinja redirects and safe problem responses for at least one release.
- No database migration is required because this feature removes presentation infrastructure only.
- Final rollback guidance is operational redeploy, not an in-process feature flag that reintroduces server-side templates.
