# Spec-Kit Breakdown 2: Admin Operations Expansion

## 1. Purpose

This document defines the next set of specs needed after `001` through `009`
so the requested admin scenarios can function end to end. It is aligned with
`docs/Architecture2.md` and assumes the existing codebase remains a modular
Python/FastAPI backend with server-rendered admin pages, async SQLAlchemy,
Alembic, PostgreSQL, Auth0/local-principal auth, tenant isolation, audit,
reliability controls, and uv-based quality gates.

Each spec below includes prompts for:

- `/speckit.specify`
- `/speckit.plan`
- `/speckit.tasks`

The prompts are intentionally detailed so junior developers can see the exact
behavior expected and senior developers can review architecture, boundaries,
failure modes, and test strategy.

## 2. Current Specs To Reuse

| Existing spec | Reuse in this expansion |
| --- | --- |
| `001-platform-foundation` | App bootstrap, settings, secret providers, storage, health, workers, quality gates |
| `002-platform-auth-access` | Auth0/local auth, platform and tenant roles, role grants, access audits |
| `003-workflow-studio-registry` | Draft workflow schema, agent/sub-agent roles, validation, publish bundles, sharing |
| `004-durable-orchestration-runtime` | Durable runs, checkpoints, workers, approvals, lineage, side-effect intents |
| `005-immutable-memory` | Agent memory scoping and append-only runtime memory behavior |
| `006-user-interaction-channels` | Web/API/Telegram runtime channels, link tokens, notifications, artifacts |
| `007-model-skill-routing` | Versioned model routing, prompt references, skill bindings, tool/outbound/credential policy |
| `008-production-audit-debugging` | Timelines, traces, replay, exports, redaction, model/tool trace types |
| `009-reliability-scale-hardening` | Backpressure, retries, breakers, quotas, fairness, operational state |

Do not duplicate these systems. New specs should extend them at documented
boundaries.

## 3. Recommended New Spec Sequence

| Spec ID | Name | Primary requested scenarios | Why it comes here |
| --- | --- | --- | --- |
| `010` | Admin Console Shell | All admin web scenarios | Gives every later admin page a common navigation, scope, layout, and auth pattern |
| `011` | Model Provider Connections And Gateway | OpenAI/local LLM setup, test runs, token usage foundation | Real provider connectivity must exist before meaningful agent testing or usage metering |
| `012` | Prompt Library And Agent Runtime Profiles | Agent/sub-agent setup | Fills the prompt-reference and agent-configuration gap left by specs `003` and `007` |
| `013` | Workflow Builder UX And Publish Gates | Agent/sub-agent workflow web UI | Productizes existing workflow registry for platform and tenant admins |
| `014` | Skill Registry And Installation | Create/install skills | Provides real skill package lifecycle behind existing skill bindings |
| `015` | Agent And Workflow Test Bench | Test agents/sub-agents | Runs sandbox tests against drafts, providers, prompts, and skills |
| `016` | Token Usage And Cost Analytics | Usage by users, agents, sub-agents | Uses centralized provider gateway records to build trusted usage views |
| `017` | Telegram Configuration Console | Configure/test Telegram | Moves Telegram setup from environment-only behavior into governed web config |
| `018` | User And Tenant Membership Administration | Add users | Productizes principal identities, invitations, memberships, and role grants |
| `019` | Operations Console Logs And Performance | Logs and system status | Unifies audit, reliability, metrics, health, and performance dashboards |

## 4. Cross-Cutting Requirements For Every New Spec

- Use Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x async ORM, Alembic,
  PostgreSQL 16+, pytest, pytest-asyncio, httpx, Ruff, mypy, and uv.
- Preserve the modular-monolith architecture. Add packages only when they own a
  clear bounded context.
- Register every new API and HTML route in `auth/policy.py` with explicit
  platform-admin, tenant-admin, tenant-user, or auditor behavior.
- Use secret references for provider keys, Telegram tokens, skill credentials,
  delegated credentials, and any future sensitive integration material.
- Add safe audit records for all admin mutations, denied attempts, connection
  tests, provider calls, skill installs, test runs, user grants, exports, and
  operational control changes.
- Keep raw prompts, model responses, secrets, provider tokens, credential
  values, Telegram chat contents, and memory content out of logs, usage tables,
  and generic audit views unless an existing authorized content view explicitly
  permits it.
- Include Alembic migrations for persistent state and rollback-aware reviewer
  notes for migration-sensitive features.
- Add unit, integration, contract, docs, and performance tests where the spec
  changes behavior at those layers.
- Maintain at least 90 percent coverage for the submitted scope and keep
  `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
  passing.
- Update `README.md`, feature docs under `docs/`, PR review notes, and testing
  instructions for every implemented spec.

## 5. Spec Prompts

### Spec 010: Admin Console Shell

#### Goal

Create a shared server-rendered admin console shell with navigation, scope
awareness, page layout, common UI components, and route authorization patterns
for all platform and tenant admin workflows.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add a shared admin console shell for the multi-agent
platform. The shell must provide platform and tenant admin navigation,
tenant scope display, authorization-aware menu items, common page layout,
shared error and empty states, safe flash messages, breadcrumbs, saved
filters where useful, and links to existing workflow, model-skill, run
inspection, and reliability pages. It must remain server-rendered with
Jinja templates and small JavaScript files under the existing web_admin
structure. The shell must not replace existing routes; it must wrap and
organize them. Require platform-admin and tenant-admin behavior to be
explicit, denied navigation to fail closed, access decisions to be
audited, at least 90 percent coverage for submitted code, docs, PR review
notes, testing instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the admin console shell using the current FastAPI,
Jinja2, Auth0/local-principal, tenancy, and web_admin patterns. Define
new routes, templates, UI helper modules, navigation item metadata,
tenant-scope rendering, authorization-aware menu filtering, empty/error
states, saved filter persistence if needed, and docs tests. Reuse
existing templates for workflow registry, model-skill config, run
inspection, and reliability controls. Include data models only if saved
preferences or filters are persisted. Include accessibility,
server-rendered testing, authorization tests, docs updates, and how
future admin specs plug pages into the shell.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the admin console shell plan into file-specific TDD
tasks. Include tests for route authorization, navigation filtering by role
and tenant scope, template rendering, empty/error states, links to
existing admin pages, saved filters if included, and access-decision audit
records. Include implementation tasks for api/routers/admin_console.py,
api/ui/admin_console.py, web_admin layout templates, static JS/CSS if
needed, auth policy entries, docs, PR review notes, testing
instructions, and README updates. Mark [P] only for isolated template or
docs tasks.
```

### Spec 011: Model Provider Connections And Gateway

#### Goal

Allow platform admins to configure, validate, and test OpenAI and local
open-source LLM connections, then expose a runtime gateway that workers and
test runs use for all model invocations.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add model provider connection management and a runtime
model gateway. Platform admins must be able to configure OpenAI LLM
connections and local open-source LLM connections, including provider
type, display name, base URL when applicable, model ids, capability
metadata, cost metadata, timeout policy, tenant visibility, and secret
references for credentials. The system must test connections through safe
probes, store last test result and health state, and create or update
tenant-visible model provider catalog entries that model routing can
select. Runtime workers and test bench runs must call a ModelGateway
abstraction instead of provider SDKs directly. The gateway must capture
latency, normalized errors, model selection trace metadata, token usage
metadata when available, retry/breaker inputs, and safe audit summaries.
Raw API keys, provider tokens, prompts, completions, and local endpoint
secrets must never be logged or stored in connection records. Require
platform-admin-only mutation by default, tenant-scoped read visibility, at
least 90 percent coverage, docs, PR review notes, testing instructions,
and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Design model provider connections and ModelGateway using
Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, httpx,
existing secret providers, existing model_skill_config catalog entries,
existing audit/debugging traces, and existing reliability breakers/retries.
Include provider adapter interfaces for OpenAI and local
OpenAI-compatible or adapter-specific endpoints, connection records, test
result records, health snapshots, catalog synchronization, secret
reference resolution, safe test probes, runtime invocation contracts,
timeout and retry behavior, breaker scope naming, usage metadata
extraction, tenant visibility rules, and migration strategy. Include admin
web views under the shared admin shell, API contracts, unit tests,
integration tests with mocked providers, contract tests, performance tests
for gateway latency overhead, docs, PR notes, and reviewer QA.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Generate test-first, file-specific tasks for model
provider connections and ModelGateway. Include tasks for
db/models/model_provider_connections.py,
db/repositories/model_provider_connections.py, model_providers adapter
interfaces, OpenAI adapter, local LLM adapter, connection validation,
secret-reference checks, provider test probes, catalog entry
synchronization, runtime gateway invocation, usage metadata extraction
hooks, audit trace creation, reliability breaker integration, admin API
routes, admin UI templates, auth policy entries, the next Alembic
migration for this spec, docs, PR review notes, testing instructions, and
README updates. Tests must cover success and failure probes, invalid
secret refs, unauthorized tenant access, local endpoint timeout, provider
unavailable, catalog inactive state, safe redaction, gateway usage
capture, and no direct provider calls from workers outside the gateway.
```

### Spec 012: Prompt Library And Agent Runtime Profiles

#### Goal

Add prompt authoring/versioning and agent runtime profiles so admins can define
the instructions, prompt versions, memory policy, model routing scope, and
skill expectations used by agents and sub-agents.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add a prompt library and agent runtime profile
management for the multi-agent platform. Platform and tenant admins must
be able to create prompt lineages, draft prompt versions, validate
template variables, publish immutable prompt versions, preview safe prompt
rendering with fixture values, and retire prompt versions from new use
without breaking historical runs. Admins must also be able to create
agent runtime profiles that bind an agent key or sub-agent key to
purpose, prompt version references, model routing scope hints, memory
scope policy, skill installation requirements, tool policy expectations,
output contract expectations, and test-suite requirements. The feature
must integrate with existing workflow registry validation and model-skill
routing prompt references. Raw secret values, credential values, and
unauthorized run content must never be embedded in prompt previews or
audit records. Require platform and tenant scope rules, immutable
versions, at least 90 percent coverage, docs, PR notes, testing
instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan prompt library and agent runtime profiles using
FastAPI, Pydantic, SQLAlchemy, Alembic, existing workflow registry,
existing model-skill config prompt reference behavior, existing memory
policy, and existing audit/redaction helpers. Define prompt_lineages,
prompt_versions, prompt_render_tests, prompt_audit_records,
agent_runtime_profiles, agent_profile_versions, and related repositories.
Include prompt template validation, variable schema, safe fixture
previews, immutable publish lifecycle, retirement behavior, agent profile
versioning, validation hooks for workflow drafts, admin web views, API
contracts, authorization rules, docs, and test strategy. Explain how
prompt version ids flow into Spec 007 prompt references and how published
workflow bundles pin prompt/profile versions.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break prompt library and agent profile work into ordered
TDD tasks with exact paths. Include tests for prompt draft creation,
template validation, variable mismatch, safe preview redaction, publish
immutability, retire behavior, tenant isolation, agent profile creation,
memory policy validation, skill requirement validation, workflow draft
validation integration, model-skill prompt reference integration, admin UI
rendering, API contracts, migration, docs, PR review notes, testing
instructions, and README updates. Include implementation tasks under
prompts/, agents/, api/routers/admin_prompts.py,
api/routers/admin_agent_profiles.py, api/schemas/prompts.py,
api/schemas/agent_profiles.py, db/models/prompts.py,
db/models/agent_profiles.py, repositories, web_admin templates, and auth
policy entries.
```

### Spec 013: Workflow Builder UX And Publish Gates

#### Goal

Upgrade the existing workflow registry UI into a guided builder for platform
and tenant admins to define agents, sub-agents, contracts, graph nodes, joins,
approvals, prompts, skills, and publish readiness.

#### `/speckit.specify` Prompt

```text
/speckit.specify Upgrade the admin workflow studio into a guided workflow
builder web UI. Platform and tenant admins must be able to define agent
and sub-agent workflows through forms and graph-oriented views without
editing raw JSON. The builder must support workflow metadata, roles,
sub-agent roles, prompt/profile references, model routing preview links,
skill installation references, contracts, nodes, edges, join policies,
approval gates, reusable subworkflow references, validation findings,
draft revisions, and publish actions. Publication must be blocked when
required validation, prompt versions, provider routing, skill
installations, or required test-suite results are missing or failing. The
feature must extend the existing workflow registry storage and published
bundle model rather than create a separate workflow store. Require
server-rendered admin pages, small JS only where useful,
tenant/platform authorization, audit records, at least 90 percent
coverage, docs, PR notes, testing instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the workflow builder UX using existing
admin/workflow_registry services, workflow_registry schemas, web_admin
templates, static workflow_studio assets, prompt library, agent
profiles, skill registry, model provider routing previews, and future
test bench status. Define UI pages, API endpoints, editor metadata, graph
preview representation, field-level validation mapping, publish gate
service, draft revision handling, optimistic concurrency behavior,
authorization, audit events, and docs. Include how the builder validates
references across prompts, provider catalog, installed skills,
subworkflows, contracts, approval gates, and test bench results. Include
unit, integration, server-rendered UI, contract, docs, and reviewer QA
tests.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Convert the workflow builder UX plan into file-specific
tasks. Include tests first for form schema round trips, field-level
validation findings, graph preview data, optimistic concurrency,
prompt/profile refs, model routing preview links, skill installation refs,
publish gate blocking, successful publish, unauthorized tenant/platform
access, and template rendering. Include implementation tasks in
admin/workflow_registry, api/routers/admin_workflow_ui.py,
api/ui/admin_workflows.py, api/schemas/workflow_editor.py,
web_admin/templates/workflows, web_admin/static/workflow_studio.js/css,
auth policy entries, docs, PR review notes, testing instructions, and
README updates.
```

### Spec 014: Skill Registry And Installation

#### Goal

Create a first-class skill package registry, installation lifecycle, and
testing path behind existing skill bindings and tool policies.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add a skill registry and installation lifecycle for
agent skills. Platform admins must be able to create platform-approved
skill packages, publish immutable skill package versions, and make them
available to tenants. Tenant admins must be able to install authorized
skill versions into their tenant, run declared smoke tests, configure
required secret references or delegated credential requirements, and bind
installed skills to agent profiles or workflow roles through existing
skill-binding policies. Skill manifests must declare slug, semantic
version, description, entrypoint type, tool declarations, action
categories, network requirements, credential requirements, runtime
permissions, test fixtures, compatibility metadata, and safe
documentation. Installed skill versions must be immutable; upgrades
require a new installation version and explicit rebinding or workflow
publish. Raw package secrets and credential values must never be stored.
Require sandboxed validation, tenant isolation, audit records, at least 90
percent coverage, docs, PR notes, testing instructions, and README
updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan skill registry and installation using FastAPI,
SQLAlchemy, Alembic, object storage for package artifacts, existing secret
providers, existing model-skill skill bindings, allowed tool policies,
outbound domain policies, credential requirements, audit, and reliability
controls. Define skill_packages, skill_package_versions,
skill_installations, skill_installation_tests, skill_audit_records,
manifest schema, package artifact storage, validation rules, installation
rules, smoke test runner, policy integration, upgrade/rollback behavior,
admin web views, API contracts, authorization, and test strategy. Include
how installed skills become eligible for Spec 007 skill bindings and
workflow publish validation.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break skill registry and installation into ordered TDD
tasks. Include tests for manifest validation, invalid permissions, package
artifact storage, platform skill publication, tenant installation,
required secret refs, delegated credential requirements, smoke test
pass/fail, installation immutability, upgrade path, skill binding
eligibility, unauthorized cross-tenant install denial, audit redaction,
and docs. Include implementation tasks under skills/,
api/routers/admin_skills.py, api/schemas/skills.py, db/models/skills.py,
db/repositories/skills.py, web_admin/templates/skills, object storage
integration, auth policy entries, migration, PR review notes, testing
instructions, and README updates.
```

### Spec 015: Agent And Workflow Test Bench

#### Goal

Allow platform and tenant admins to test individual agents, sub-agents,
subworkflows, and full workflows before publication or after configuration
changes.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add an agent and workflow test bench for platform and
tenant admins. Admins must be able to create test suites and test cases
with fixture inputs, expected contract shapes, deterministic assertions,
optional evaluator prompts, model/provider mode, tool/skill mode, and
pass/fail thresholds. Admins must run tests against prompt versions, agent
runtime profiles, workflow drafts, published subworkflows, or full
published workflows. Test runs must support safe execution modes: mock
model, mock tools, real model with side effects disabled, and approved
real dependency probes. Test results must show step traces,
model/provider choices, prompt/profile versions, skill versions, token
usage, latency, contract validation results, redacted transcripts,
artifacts, and pass/fail status. Workflow publication may require
selected test suites to pass. Require tenant isolation, safe redaction,
audit records, at least 90 percent coverage, docs, PR notes, testing
instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the agent and workflow test bench using existing
workflow registry drafts and bundles, runtime orchestration, model
gateway, prompt library, agent profiles, skill registry, audit/debugging,
usage ledger hooks, and object storage. Define agent_test_suites,
agent_test_cases, agent_test_runs, agent_test_run_steps,
agent_test_assertions, sandbox execution semantics, safe modes, fixture
storage, evaluator strategy, publish gate integration, result UI, API
contracts, authorization, retention, and performance constraints. Include
tests for draft tests, sub-agent tests, workflow tests, mock vs real
provider modes, side-effect blocking, redaction, usage capture, publish
gating, and failure diagnostics.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Generate file-specific test-first tasks for the test
bench. Include tests for suite/case CRUD, fixture validation, sandbox run
creation, mock model execution, real gateway execution with mocked
provider, tool side-effect blocking, skill policy enforcement, contract
assertion pass/fail, evaluator assertion pass/fail, redacted transcript
artifact storage, usage capture as test mode, publish gate integration,
unauthorized access denial, and UI rendering. Include implementation tasks
under testing/agent_bench, api/routers/admin_agent_tests.py,
api/schemas/agent_tests.py, db/models/agent_tests.py, repositories,
runtime sandbox integration, web_admin/templates/agent_tests, auth policy
entries, migration, docs, PR notes, testing instructions, and README
updates.
```

### Spec 016: Token Usage And Cost Analytics

#### Goal

Record and display model token usage by tenant, user, workflow, agent,
sub-agent, run, step, provider, and model.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add token usage and cost analytics for model-backed
agents and sub-agents. The platform must record normalized usage events
for every model invocation routed through ModelGateway, including tenant,
initiating principal, workflow run, run step, workflow lineage/version,
agent key, sub-agent key when applicable, provider key, model id, prompt
version, execution mode, input tokens, output tokens, cached tokens when
available, reasoning tokens when available, total tokens, provider
billable units, latency, cost estimate, pricing version, and whether
values are estimated or confirmed. Platform admins must view all usage;
tenant admins must view their tenant; future tenant users may view only
their own usage if exposed. Dashboards must support filters, time ranges,
rollups, drilldowns, and CSV exports. Raw prompts, completions, secrets,
memory content, and unauthorized run content must not be stored in usage
records. Require audit records for exports and denied access, at least 90
percent coverage, docs, PR notes, testing instructions, and README
updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan token usage analytics using ModelGateway usage
metadata, SQLAlchemy, Alembic, PostgreSQL rollups, existing
audit/redaction, object storage exports, and admin web views. Define
llm_usage_events, llm_usage_rollups, llm_pricing_versions,
usage_export_requests, aggregation jobs or query-time rollups, pricing
metadata, late usage reconciliation, test vs production mode separation,
tenant/user/agent filters, API contracts, UI pages, authorization, export
retention, and performance tests. Include how usage events link to
runtime runs, run steps, model selection traces, prompt versions, and
agent/sub-agent keys without storing prompt or response content.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break token usage analytics into TDD tasks. Include tests
for usage event normalization, provider-specific missing usage fields,
estimated vs confirmed usage, run/step/user/agent attribution, tenant
isolation, dashboard filters, rollup correctness, pricing version
calculation, CSV export authorization, redaction, late reconciliation,
and performance of time-range queries. Include implementation tasks under
usage/, api/routers/admin_usage.py, api/schemas/usage.py,
db/models/usage.py, repositories, ModelGateway integration,
web_admin/templates/usage, auth policy entries, migration, docs, PR
review notes, testing instructions, and README updates.
```

### Spec 017: Telegram Configuration Console

#### Goal

Allow platform and tenant admins to configure Telegram connections from the web
UI and test the connection.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add a Telegram configuration console for the
multi-agent platform. Platform admins must be able to create global
Telegram bot configurations using secret references for bot tokens,
webhook secret policy, webhook URL, allowed tenants, enabled commands,
notification defaults, provider rate-limit settings, and operational
status. Tenant admins must be able to enable tenant Telegram access,
configure tenant-level notification defaults, inspect link status, and
test the connection when platform policy permits. The console must support
safe tests for bot identity, webhook reachability/status, webhook secret
validation, link-token creation, and optional test notification to a
linked chat. Runtime Telegram commands, link tokens, and workflow
interactions must continue to use the existing channel service. Raw bot
tokens and chat-sensitive content must never be logged or stored. Require
tenant/platform authorization, audit records, at least 90 percent
coverage, docs, PR notes, testing instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the Telegram configuration console using existing
channels/telegram.py, channel service, telegram_webhook router, settings
guardrails, secret providers, audit, reliability breakers, and admin
console shell. Define channel_connection_configs,
telegram_connection_tests, telegram_webhook_status_records, service APIs,
webhook validation behavior, token secret reference rules, tenant
enablement, test-send behavior, route/UI design, authorization,
migration, and test strategy. Explain how environment settings and
database-backed configuration interact, including precedence and
production safety.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Generate test-first tasks for Telegram configuration.
Include tests for platform bot config creation, invalid token secret ref
denial, tenant enablement, webhook secret validation, bot identity probe
success/failure, webhook status probe, link-token test, optional
test-send safe summary, runtime service using active config,
environment/database precedence, unauthorized cross-tenant access,
redaction, and audit records. Include implementation tasks in
channels/configuration.py, api/routers/admin_channel_config.py,
api/schemas/channel_config.py, db/models/channel_config.py, repositories,
web_admin/templates/channels, auth policy entries, migration, docs, PR
notes, testing instructions, and README updates.
```

### Spec 018: User And Tenant Membership Administration

#### Goal

Allow platform and tenant admins to add users, invite users, assign tenant
roles, suspend users, and manage memberships without direct database access.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add user and tenant membership administration. Platform
admins must be able to list users, create invitations, link or provision
Auth0-backed principal identities, assign platform roles, assign tenant
roles, suspend or reactivate users, revoke grants, and inspect user
access history across tenants. Tenant admins must be able to invite users
to their own tenant, assign permitted tenant roles, revoke tenant
memberships, and view user status for their tenant only. The platform
must store principal metadata, invitations, memberships, and role grants,
but production authentication remains Auth0-backed and the platform must
not store user passwords. Local-principal mode must remain available for
development and test. All role changes must take effect on the next
protected action and create audit records. Require idempotent invites,
safe email handling, tenant isolation, at least 90 percent coverage,
docs, PR notes, testing instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan user and tenant membership administration using
existing access_control models, role_grants, Auth0/local-principal auth,
admin_access router, access audit, FastAPI, SQLAlchemy, Alembic, and
admin console shell. Define user_invitations, tenant_memberships,
user_admin_audit_records if needed, service/repository APIs, Auth0
invitation or lookup integration boundary, idempotency keys, role
assignment rules, suspension behavior, grant revocation behavior, tenant
admin limits, platform admin capabilities, UI pages, API contracts,
migration, and test strategy. Include how existing PrincipalIdentity and
RoleGrant records are reused rather than replaced.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break user administration into file-specific TDD tasks.
Include tests for user list visibility, platform invite, tenant invite,
existing Auth0 subject linking, placeholder principal creation,
idempotent invite replay, role grant creation, role grant revocation,
suspension/reactivation, tenant admin cannot assign platform roles,
cross-tenant denial, next-request role change behavior, audit records,
local-principal dev behavior, UI rendering, and API contracts. Include
implementation tasks under users/, api/routers/admin_users.py,
api/schemas/users.py, db/models/user_management.py, repositories,
extensions to admin/service.py or new user service, auth policy entries,
migration, docs, PR review notes, testing instructions, and README
updates.
```

### Spec 019: Operations Console Logs And Performance

#### Goal

Provide platform admins with a unified operations console for logs, health,
dependency status, runtime performance, model provider status, channel status,
usage throughput, reliability state, and safe exports.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add an operations console for platform administrators.
Platform admins must be able to view system health, dependency readiness,
worker capacity, queue pressure, database pool pressure, object-storage
status, model-provider health, Telegram/channel status, reliability
breaker state, retry/dead-letter state, request latency, run lifecycle
throughput, model latency, token throughput, error rate, and redacted
structured logs. The console must support filtering logs and operational
events by trace id, tenant id, run id, component, severity, status,
dependency, and time range. It must link from operational records to run
inspection, reliability controls, provider connection tests, and usage
dashboards when authorized. It must provide redacted export artifacts and
audit every export or denied access. Tenant admins may receive limited
tenant-scoped operational views only if explicitly included; platform logs
are platform-admin or auditor only. Require safe redaction, retention
awareness, performance tests, at least 90 percent coverage, docs, PR
notes, testing instructions, and README updates.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the operations console using existing
observability/logging.py, observability/metrics.py, runtime health
services, audit inspection, reliability controls, model provider health
snapshots, Telegram config status, usage rollups, object storage export
providers, and admin console shell. Define operations service APIs,
dashboard DTOs, optional persisted operational_status_snapshots or saved
filters, structured log index strategy, metrics read strategy,
health/dependency aggregation, redacted export flow, UI pages, API
contracts, authorization, migration if needed, performance constraints,
and docs. Include how the console avoids raw secrets, raw prompts, model
responses, credential values, and unauthorized tenant data.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Generate ordered, test-first tasks for the operations
console. Include tests for health aggregation, dependency status mapping,
worker/queue metrics, DB pool pressure display, model provider status
display, Telegram status display, reliability state links, usage
throughput panels, log filtering by
trace/run/tenant/component/severity/time, redaction, export
authorization, tenant-scope denial, platform-admin access, auditor
read-only access, UI rendering, and performance of bounded time-range
queries. Include implementation tasks under operations/,
api/routers/admin_operations.py, api/schemas/operations.py, optional
db/models/operations.py and repositories, web_admin/templates/operations,
auth policy entries, docs, PR review notes, testing instructions, and
README updates.
```

## 6. Delivery And Review Guidance

Implement specs in the recommended order unless a later spec is deliberately
split behind stable stubs. A useful rule:

- Do not build agent test bench behavior before `ModelGateway`, prompt
  versions, and skill installation exist.
- Do not build token usage dashboards before model calls are centralized.
- Do not expand Telegram runtime commands while working on configuration; reuse
  existing runtime command handling and make the configuration source governed.
- Do not bypass `auth/policy.py` for admin pages. Missing policy entries should
  fail closed.
- Do not store raw provider prompts, responses, Telegram tokens, API keys,
  credentials, or skill secret material while adding observability.

Suggested acceptance gate for each implemented spec:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Each spec PR should include:

- linked spec directory,
- summary of functional behavior,
- architecture impact notes,
- database migration notes,
- auth and tenant-scope notes,
- audit/redaction notes,
- test evidence and coverage,
- manual QA steps,
- rollback or operational notes,
- README and docs delta.

## 7. Developer Readiness Checklist

Before a junior developer picks up a task, the generated `tasks.md` should
identify:

- exact file paths,
- prerequisite tasks,
- expected test file,
- input and output schemas,
- authorization rule,
- safe error category,
- audit event expected,
- fixture data needed.

Before a senior developer approves a generated plan, confirm:

- the bounded context is not duplicating an existing subsystem,
- migrations preserve existing records and indexes,
- provider/channel calls go through testable adapters,
- secrets are always references,
- tenant isolation is enforced in API, service, repository, and UI layers,
- publication gates and runtime behavior are deterministic,
- dashboards and exports are redacted,
- performance constraints are measurable,
- docs and reviewer instructions are enough to validate the feature without
  verbal explanation.
