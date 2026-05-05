# Research: React Admin Migration Hardening And Jinja Retirement

## Decision: Treat Spec 037 As Additive Hardening First

**Rationale**: The safest final migration is to prove parity, direct-link behavior, rollback, redaction, tenant isolation, accessibility, and performance before deleting legacy UI. Specs 026-036 introduced React routes while preserving Jinja fallbacks; Spec 037 should codify decisions and retire only explicitly proven duplicated UI.

**Alternatives considered**:

- Delete all legacy templates immediately. Rejected because several direct-link and support workflows need a two-release fallback window.
- Keep all legacy UI indefinitely. Rejected because it leaves duplicated maintenance and no migration completion signal.

## Decision: Use Backend-Owned Parity Matrix Contracts

**Rationale**: The browser should not infer route eligibility, retirement status, tenant scope, or rollback behavior. A Pydantic-backed projection can normalize route decisions and generate TypeScript contracts for React.

**Alternatives considered**:

- Maintain parity only in docs. Rejected because docs alone do not support contract tests or browser validation.
- Derive all route decisions in TypeScript. Rejected because authorization and migration decisions belong on the backend.

## Decision: React Home Shows Migration Hardening Evidence

**Rationale**: `/admin/app` is the natural final React landing surface after the migration. Rendering the migration hardening dashboard there gives reviewers an immediate parity overview while keeping domain navigation intact.

**Alternatives considered**:

- Leave `/admin/app` as a shell-only page. Rejected because Spec 037 needs a visible final migration review surface.
- Add a separate-only route and keep home empty. Rejected because the generated QA037 smoke route targets `/admin/app`.

## Decision: Keep Legacy Direct Links With Safe Redirect Or Notice

**Rationale**: Existing runbooks, bookmarks, and support links may target old Jinja URLs. Direct links should redirect, alias, or show a deprecation notice while preserving tenant id, route parameters, and query filters.

**Alternatives considered**:

- Return 404 for retired routes. Rejected because it breaks operators and weakens rollback.
- Silently rewrite links in navigation only. Rejected because direct links would still be brittle.

## Decision: Local QA Performance Budgets

**Rationale**: Deterministic QA should prove route bootstrap under 500 ms, primary journey interactivity under 2 seconds, and compressed asset size within the documented QA037 budget or with mitigation notes. Current React build evidence from Spec 036 sits below a practical compressed budget.

**Alternatives considered**:

- Use production-only load testing. Rejected because local QA needs repeatable acceptance evidence.
- Ignore asset budget. Rejected because final migration can otherwise hide frontend growth.

## Decision: Accessibility Scope

**Rationale**: The final suite must cover keyboard navigation, focus management, landmarks, labels, contrast-sensitive state, and text non-overlap in desktop and mobile-sized viewports. Automated checks are paired with manual screenshot review because visual overlap and hidden-token concerns need human confirmation.

**Alternatives considered**:

- Rely on screenshot checks only. Rejected because keyboard and label regressions can be invisible.
- Require a full external accessibility certification. Rejected as outside local QA scope.

## Decision: Rollback By Flag Plus Asset Version

**Rationale**: Operators need a reversible admin UI migration without touching backend domain state. The rollback runbook should identify the route-selection flag, React asset version, direct-link behavior, and fallback pages.

**Alternatives considered**:

- Rollback by database migration. Rejected because Spec 037 should not mutate domain data.
- Rollback by deleting React routes. Rejected because route availability and static assets are safer to switch than remove.
