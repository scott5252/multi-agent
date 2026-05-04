# Spec 033 - React Agent And Workflow Test Bench: Specify

Roadmap source: `react_ui.md`

## Deterministic Targets

- Feature directory: `specs/033-react-agent-and-workflow-test-bench`
- Git branch: `codex/033-react-agent-and-workflow-test-bench`
- QA id: `qa033`
- QA database: `multi_agent_platform_qa033`

SPECIFY_FEATURE_DIRECTORY=specs/033-react-agent-and-workflow-test-bench
GIT_BRANCH_NAME=codex/033-react-agent-and-workflow-test-bench

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

## Specify Prompt

Create a feature specification for a React Agent and Workflow Test Bench.
Platform and tenant admins must be able to define reusable test suites and
cases, select safe execution modes, launch tests against prompts, profiles,
workflow drafts, subworkflows, or published workflows, inspect results,
understand pass/fail diagnostics, review redacted traces and artifacts, and
see publish-gate evidence tied to the current workflow draft revision or
published target version. The UI must make testing understandable for
non-technical admins without exposing raw prompts, completions, secrets, tools,
raw connector payloads, or unauthorized tenant data.

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
