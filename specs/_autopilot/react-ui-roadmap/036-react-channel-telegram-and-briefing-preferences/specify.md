# Spec 036 - React Channel, Telegram, And Briefing Preferences: Specify

Roadmap source: `react_ui.md`

## Deterministic Targets

- Feature directory: `specs/036-react-channel-telegram-and-briefing-preferences`
- Git branch: `codex/036-react-channel-telegram-and-briefing-preferences`
- QA id: `qa036`
- QA database: `multi_agent_platform_qa036`

SPECIFY_FEATURE_DIRECTORY=specs/036-react-channel-telegram-and-briefing-preferences
GIT_BRANCH_NAME=codex/036-react-channel-telegram-and-briefing-preferences

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

Create a feature specification for React Channel, Telegram, and Briefing
Preferences. Platform admins, authorized tenant admins, and authorized tenant
users need an intuitive UI for channel readiness, Telegram tenant enablement,
safe secret-reference configuration, webhook validation, natural-language
aliases such as `Morning briefing`, protected alias readiness, linked Telegram
identities, one-time link tokens, delivery attempts, webhook diagnostics,
user-facing run status links, and Daily Intelligence Briefing preference
profiles. Preference profiles must cover location, timezone, news topics, VIP
sender hints, workday hours, commute mode, default account references, output
style, and optional scheduled briefing time. The UI must not display real bot
tokens, webhook secrets, full Telegram user or chat identifiers, link tokens
after creation, private messages, raw preference values in admin summaries, raw
prompts, run results, or unauthorized tenant data.

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
