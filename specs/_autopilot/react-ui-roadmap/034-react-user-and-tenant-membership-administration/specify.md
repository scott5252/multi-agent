# Spec 034 - React User And Tenant Membership Administration: Specify

Roadmap source: `react_ui.md`

## Deterministic Targets

- Feature directory: `specs/034-react-user-and-tenant-membership-administration`
- Git branch: `codex/034-react-user-and-tenant-membership-administration`
- QA id: `qa034`
- QA database: `multi_agent_platform_qa034`

SPECIFY_FEATURE_DIRECTORY=specs/034-react-user-and-tenant-membership-administration
GIT_BRANCH_NAME=codex/034-react-user-and-tenant-membership-administration

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

Create a feature specification for React User and Tenant Membership
Administration. Platform admins need a clear user directory, invitation flow,
principal linking/provisioning, platform role assignment, tenant role
assignment, suspension/reactivation, grant revocation, membership status
management, and access history across tenants. Tenant admins need a safer
tenant-scoped view for inviting users, assigning permitted roles, revoking
memberships, and viewing user status for their tenant only. The UI must avoid
raw identifiers as the primary experience and must preserve safe email
handling, idempotent invites, next-request role effect, tenant isolation, and
audit records.

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
