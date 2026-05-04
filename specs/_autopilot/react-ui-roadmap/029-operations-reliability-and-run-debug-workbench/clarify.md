# Spec 029 - Operations, Reliability, And Run Debug Workbench: Clarify

Roadmap source: `react_ui.md`

## Deterministic Targets

- Feature directory: `specs/029-operations-reliability-and-run-debug-workbench`
- Git branch: `codex/029-operations-reliability-and-run-debug-workbench`
- QA id: `qa029`
- QA database: `multi_agent_platform_qa029`

## Global Prompt Prefix

Use the current multi-agent platform repository context. Preserve the
constitution, specs 001 through 025, existing FastAPI backend services,
PostgreSQL storage model, Auth0 production authentication, local-principal
test mode, tenant isolation, audit fail-closed behavior, redaction rules,
runtime version pinning, secret hygiene, object-storage boundaries, QA docs,
Playwright evidence, and at least 90 percent relevant coverage. This includes
graph execution and join policies, governed tool execution, Telegram alias and
delivery idempotency, Daily Briefing preference privacy, repository-backed test
evidence publish gates, and live model credential resolution.

The UI target is a modern React.js + TypeScript + Vite admin experience for
non-technical platform and tenant administrators. React must improve clarity,
guided workflows, responsiveness, accessibility, empty/error/loading states,
safe confirmations, progressive disclosure, and cross-linking. Do not duplicate
security or domain business rules in the browser. Existing domain services and
explicit JSON/API contracts remain authoritative.

Keep each feature independently testable, additive, and reversible. Existing
Jinja admin routes may remain available as fallbacks until the migration parity
spec retires them. Any route that handles protected data must fail closed if
authorization, tenant scoping, or audit persistence cannot be proven.

Every `/speckit.specify` output must make dual-auth-mode validation a
mandatory acceptance criterion: the feature must be testable with Auth0-backed
production-style principals and with `AUTH_MODE=local_principal`. Every
`/speckit.tasks` output must include explicit test tasks for both modes, using
backend route tests for Auth0 claim/principal resolution and browser
Playwright flows for local-principal login unless a safer feature-specific
validation path is documented.

## Clarify Prompt

Run clarification for the operations workbench. Focus on platform-only versus
tenant-limited scope, default time range, refresh behavior, chart/table density,
log filtering, cross-links to run/reliability/provider/usage pages, export
workflow, and how degraded dependencies appear. Recommended defaults:
platform-admin and auditor full access, tenant admin limited only where
existing policies allow, default last 60 minutes, manual refresh plus safe
short polling for health panels, filters matching Specs 019 through 025 where
applicable, and degraded cards instead of hidden sections.

## Autonomous Clarification

Use the recommended defaults in the roadmap and established repo patterns for low-risk answers. Record every auto-selected answer in spec.md with `(autopilot)`. Stop for security, tenant, audit, credential, destructive data, production resource, external side-effect, or irreversible migration ambiguity.

## Roadmap Execution Notes

- Create one Spec Kit feature at a time. Do not run all specs in parallel.
- After each implementation, run its generated QA guide and Playwright UI
  walkthrough before starting the next spec.
- Keep the React UI additive until Spec 037 proves parity.
- Treat dual-auth-mode coverage as mandatory for every implementation spec:
  each feature must prove Auth0-backed principal behavior and
  `AUTH_MODE=local_principal` behavior for its React routes and protected
  actions.
- Prefer backend-owned JSON contracts and generated TypeScript types over
  hand-maintained browser models.
- Prefer explicit user journeys and guided actions over exposing raw IDs,
  JSON, and domain jargon as the primary interface.
- Treat security, tenant isolation, audit, and redaction uncertainty as a stop
  condition, not a styling issue.
