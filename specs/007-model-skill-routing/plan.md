# Implementation Plan: Model Routing And Skill Configuration

**Branch**: `007-model-skill-routing` | **Date**: 2026-04-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-model-skill-routing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a versioned configuration subsystem that resolves model, prompt, skill,
tool, outbound-domain, secret-reference, and credential policy decisions for
workflow execution. Administrators can define one active tenant-scoped default
LLM, workflow/agent/step model overrides, prompt references, explicit skill
bindings, deny-by-default tool policies, outbound egress policies, safe secret
references, and tool credential requirements. The runtime pins run-level
resolvable versions at acceptance and pins step/tool-specific decisions at
first use, records safe audit metadata for allow and deny outcomes, supports
rollback by reactivating prior versions, and exposes FastAPI plus minimal admin
web views for previewing resolution, reviewing history, and changing model or
tool access safely.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, existing
local-principal auth mode, LangChain 1.2.15, LangGraph 1.1.9,
langgraph-checkpoint-postgres 3.0.5, httpx for policy validation fixtures,
pytest, pytest-asyncio, Ruff, mypy, uv  
**Storage**: PostgreSQL for model provider catalog entries, versioned model
routing records, prompt version references, skill bindings, allowed tool
policies, outbound domain policies, secret-reference versions, credential
requirements, activation pointers, resolution previews, runtime pinned
configuration snapshots, policy decisions, migration records, and
configuration audit records; existing secret manager stores raw secret values;
object storage is not used by this feature except through existing artifact
metadata for exported review evidence  
**Testing**: pytest unit tests for routing precedence, prompt resolution,
policy intersection, domain pattern matching, credential requirement
satisfaction, rollback activation, safe audit summaries, Pydantic schemas, and
deterministic resolution snapshots; FastAPI contract tests for admin
configuration, preview, history, provenance, rollback, and policy decision
endpoints; PostgreSQL-backed integration tests for active-version uniqueness,
transactional activation, run acceptance pinning, first-use pinning,
concurrent activation, resumed-run stability, and tenant fail-closed behavior;
coverage enforcement at >=90 percent for the submitted configuration,
resolution, policy, provenance, and admin API behavior  
**Target Platform**: Linux container deployment target for FastAPI API and
background workers; local development on macOS/Linux; PostgreSQL-backed
workflow execution under the existing platform bootstrap model  
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
server-rendered admin web views, durable workflow runtime services,
configuration audit surfaces, and operator-facing documentation  
**Performance Goals**: Under a development-test fixture with 3 tenants, 100
workflow/agent/step overrides per tenant, 300 skill/tool/outbound/credential
policy versions per tenant, 100 active or paused runs per tenant, and latest-100
history pages, resolve a model and prompt preview p95 <150ms; evaluate skill,
tool, domain, and credential policies p95 <50ms after policy set load; pin
run-level configuration during run acceptance within 500ms excluding workflow
bundle load; and add <100ms p95 for first-use policy decisions before external
tool or model invocation  
**Constraints**: Exactly one active tenant-scoped global default model per
tenant; model precedence is step, agent, workflow, then tenant default; prompt
precedence is step, agent, then workflow only; every active configuration
change creates an immutable version with actor, reason, prior version, scope,
and activation metadata; tool, skill, domain, and credential access is
deny-by-default and allowed only when every applicable active policy permits
the request; raw secrets and credential values never appear in workflow
definitions, policies, provenance, logs, traces, or audits; existing tenant and
role authorization applies to all config mutation, preview, history, runtime
resolution, and provenance reads; resumed runs retain pinned versions unless
an explicit audited migration is performed; >=90 percent unit-test coverage,
README update, PR review notes, and testing instructions are required  
**Scale/Scope**: Initial scope supports one active global model default per
tenant, low hundreds of workflow/agent/step overrides per tenant, hundreds of
skill bindings and policy versions per tenant, thousands of historical
configuration versions, hundreds of active or paused runs per tenant, and
runtime decisions pinned per model-backed step or external tool attempt

**Tenant Limits And Fairness**: Resolution, preview, history, and policy
evaluation run inside tenant-scoped query bounds. Admin preview and history
endpoints enforce existing tenant quotas and bounded page sizes. Runtime
first-use evaluation must not bypass orchestration concurrency controls, and
fairness metrics track per-tenant resolver latency, denial counts, and policy
evaluation volume.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Configuration versions, activation changes, run-level pins, first-use decisions, migrations, denials, side-effect intents, lease retries, compensation state, and audits are persisted transactionally before they become authoritative for execution. |
| Immutable State And Memory | PASS | Every configuration change creates a new immutable version; active pointers are projections over append-only history rather than rewriting past records. |
| Contract-First Agent Coordination | PASS | Admin APIs, runtime resolution protocol, policy decision payloads, and minimal admin view contracts define request/response schemas, precedence, error categories, and provenance semantics before implementation. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal authorization gates configuration, preview, history, runtime resolution, policy enforcement, and provenance reads while retaining deterministic local principals for tests. |
| Operability Is A Product Requirement | PASS | Plan defines safe audit events, structured logs, metrics, traces, workflow timeline events, lineage/replay metadata, history pages, decision records, denial reasons, rollback evidence, and reviewer quickstart flows. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks trace directly to model routing, skill binding, policy enforcement, provenance, and review requirements. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, deterministic resolver tests, policy deny tests, rollback tests, README guidance, testing instructions, and PR review notes. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across configuration domain services, DB models/repositories, API schemas/routers, runtime integration, admin views, observability, migration, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | All records carry tenant scope; cross-tenant ids fail closed; previews and runtime evaluation use caller/run tenant context; policy resolution remains indexed and bounded by tenant, quotas, page sizes, and orchestration concurrency controls. |
| Version-Pinned Execution | PASS | Run acceptance persists run-level resolvable versions and first use persists step/tool-specific model, prompt, skill, tool, outbound, secret, and credential versions. |
| Secret Hygiene And Controlled Tool Access | PASS | Raw secrets stay in the secret manager; persisted records contain references, metadata, hashes, and safe summaries only; all tools require explicit skill, tool, outbound, and credential authorization. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores transactional configuration and audit metadata; no new blob storage path is introduced; exported review evidence remains under existing artifact policy. |
| Human Approval Is Durable State | PASS | Configuration rollback and in-flight run migration require explicit authorized requests and durable audit/migration records; any human approval for migration is persisted before runtime behavior changes. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/007-model-skill-routing/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- model-skill-routing.openapi.yaml
|   +-- runtime-resolution-protocol.md
|   +-- admin-web-views.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- admin_model_skill_config.py     # admin CRUD, preview, history, rollback, provenance APIs
    |   +-- schemas/
    |       +-- model_skill_config.py           # request/response and error schemas
    +-- bootstrap/
    |   +-- container.py                        # wire config resolver and repositories
    +-- config/
    |   +-- __init__.py
    |   +-- model_skill.py                      # domain models and value objects
    |   +-- resolver.py                         # deterministic model/prompt/policy resolution
    |   +-- policy.py                           # tool, domain, credential intersection evaluators
    |   +-- service.py                          # admin and runtime facade
    |   +-- validation.py                       # publication/start validation rules
    |   +-- rollback.py                         # activation rollback/migration helpers
    |   +-- provenance.py                       # pinning and decision summaries
    +-- db/
    |   +-- models/
    |   |   +-- model_skill_config.py           # configuration, active pointers, decisions, audits
    |   +-- repositories/
    |       +-- model_skill_config.py           # transactional storage
    +-- runtime/
    |   +-- orchestration/
    |       +-- service.py                      # call resolver at acceptance and first use
    +-- web_admin/
    |   +-- static/
    |   |   +-- model_skill_config.js           # preview/history interactions
    |   +-- templates/
    |       +-- model_skill_config/
    |           +-- index.html
    |           +-- detail.html
    |           +-- history.html
    |           +-- run_provenance.html
    +-- observability/
        +-- logging.py
        +-- metrics.py
        +-- tracing.py
alembic/versions/
+-- 0007_model_skill_routing.py              # new migration
tests/
+-- contract/
|   +-- test_model_skill_config_contract.py
+-- integration/
|   +-- api/
|   |   +-- test_admin_model_skill_config_api.py
|   |   +-- test_admin_model_skill_config_ui.py
|   +-- db/
|   |   +-- test_model_skill_config_migration.py
|   +-- runtime/
|       +-- test_config_pinning_runtime.py
+-- unit/
|   +-- api/
|   |   +-- test_model_skill_config_schemas.py
|   +-- config/
|   |   +-- test_domain_policy_matching.py
|   |   +-- test_policy_intersection.py
|   |   +-- test_prompt_resolution.py
|   |   +-- test_resolver_determinism.py
|   |   +-- test_rollback.py
|   |   +-- test_secret_reference_summaries.py
|   |   +-- test_validation.py
|   +-- db/
|       +-- test_model_skill_config_models.py
README.md
docs/quickstart.md
docs/model-skill-routing.md                 # new operator/reviewer guide
```

**Structure Decision**: Keep model routing and policy resolution inside the
existing Python/FastAPI backend. Add a focused `multi_agent_platform.config`
subsystem for domain models, validation, deterministic resolution, rollback,
and provenance; DB models/repositories own durable version history; routers
and admin templates remain thin over the configuration service; runtime
orchestration consumes the resolver facade rather than reading policy tables
directly.

## Configuration Scope And Precedence Decisions

- **Scope identity**: Versioned configuration records use
  `(tenant_id, scope_type, workflow_lineage_id, workflow_version_bundle_id,
  agent_key, step_key)` as nullable scoped identifiers. Tenant default records
  have no workflow, agent, or step key. Workflow overrides identify a workflow
  lineage or published bundle. Agent overrides include `agent_key`; step
  overrides include both `agent_key` when known and `step_key`.
- **Model precedence**: Runtime and preview resolution use strict precedence:
  step override, agent override, workflow override, then tenant global default.
  The resolver returns the winning version id, source scope, model provider,
  model id, model capability metadata, and all active candidates considered.
- **Prompt precedence**: Prompt references resolve independently from model
  records and use only step prompt reference, agent prompt reference, then
  workflow prompt reference. Tenant defaults never supply prompts. A missing
  prompt is a blocking validation failure for model-backed execution.
- **Deny by default**: Missing active skill bindings, missing active tool
  policies, missing outbound policies for network-capable tools, or missing
  credential requirements for credentialed tools deny execution before model
  or tool side effects occur.
- **Cumulative intersection**: For skills, tools, outbound domains, and
  credentials, every applicable active policy must allow the requested use.
  The decision record stores the evaluated policy version ids and safe reason
  for any denial.
- **Applicable policies**: Policies can be scoped to tenant, workflow, agent,
  step, skill, tool, operation category, domain pattern, credential scope, and
  environment. A policy applies when all non-null scope selectors match the
  request context. Broader policies do not get overridden by narrower policies;
  they remain cumulative constraints.

## Validation And Publishing Decisions

- **Admin write validation**: Create/update requests validate tenant scope,
  actor role, required reason, known model provider, active provider/model
  availability, prompt version reference shape, skill slug/version, tool id,
  operation category, domain pattern syntax, credential scope, secret-reference
  status, and absence of raw secret-like values.
- **Activation validation**: Activation runs in one transaction. It creates a
  new immutable version when needed, deactivates the previous active pointer
  for the same singleton scope when the config kind is exclusive, writes a
  configuration audit record, and updates an active projection.
- **Tenant default uniqueness**: A partial unique index enforces one active
  tenant-scoped global model default per tenant. Workflows can have at most one
  active model override per equivalent scope, and prompt references follow the
  same singleton active-scope rule.
- **Publish/start validation**: Workflow publishing and runtime start preview
  fail if any model-backed path cannot resolve a valid model and prompt, if any
  referenced skill has no binding, if required tools lack cumulative allows, if
  outbound policies fail closed, or if credential requirements cannot be
  satisfied by active secret/delegated credential references.
- **Safe errors**: API and runtime errors use stable categories such as
  `missing_global_default`, `invalid_model_reference`, `missing_prompt_version`,
  `skill_not_bound`, `tool_denied`, `domain_denied`,
  `credential_unsatisfied`, `secret_reference_invalid`, and
  `authorization_failed`. Error payloads include ids and redacted summaries,
  not prompts, secrets, or credential values.

## Persistence And Versioning Decisions

- **Immutable versions**: Each configuration category has a version table with
  `version_id`, `tenant_id`, scope selectors, payload JSON, status,
  `version_sequence`, `previous_version_id`, `created_by_principal_id`,
  `created_at`, `activation_reason`, `effective_from`, optional
  `effective_until`, and redacted metadata. Existing versions are not updated
  except for retention/archival markers explicitly allowed by platform policy.
- **Active projections**: Active pointer tables provide fast lookup by tenant,
  config kind, and scope hash. They reference immutable version ids and are
  rebuilt from history if needed. The version record remains the source for
  audit and provenance.
- **Run-level pinning**: At run acceptance, the runtime asks the resolver for
  all configuration versions that are resolvable without step/tool-specific
  request data. The resulting `ResolvedExecutionConfiguration` is persisted
  with the runtime execution bundle and contains model defaults/overrides,
  prompt refs visible from the accepted workflow, skill bindings, tool policy
  versions, outbound policy versions, secret-reference versions, and credential
  requirement versions.
- **First-use pinning**: When a model-backed step, skill access, tool call,
  outbound domain check, secret reference, or credential requirement is first
  evaluated, the runtime records the exact winning or denying version set in a
  `RuntimePolicyDecision` row before invoking the model or external tool.
- **Resume stability**: Resumed runs reuse run-level pins and previously
  recorded first-use decisions. If a decision has not been used yet, the
  resolver evaluates against the run's pinned candidate set rather than the
  latest active configuration unless an audited migration explicitly updates
  that run.

## Runtime Resolution And Rollback Decisions

- **Resolver contract**: Runtime code passes tenant id, workflow version bundle
  id, workflow lineage id, run bundle id, run id, agent key, step key, tool id,
  action category, destination host, credential context, trace id, and
  idempotency key where applicable. The resolver returns an allowed/denied
  decision plus version ids, source scopes, safe reason, and audit metadata.
- **Side-effect boundary**: Model calls and network-capable tool calls may only
  execute after their decisions are persisted. Denied decisions are persisted
  before returning control to the runtime.
- **Rollback behavior**: Rollback does not mutate or delete a bad version.
  Authorized admins reactivate a prior version for the same tenant/config/scope
  through a `rollback` action that creates an audit record, changes the active
  projection, and requires a reason. Future runs use the reactivated version;
  in-flight runs keep pinned versions unless an explicit run migration is
  approved and recorded.
- **Run migration**: Migration is separate from rollback. It records the old
  and new pinned version sets, actor, reason, approval reference when needed,
  affected run ids, and a compatibility check result. Migration cannot expose
  secrets and cannot change decisions already used by completed step/tool
  attempts.
- **Concurrent changes**: Activation and rollback require expected active
  version ids. Stale admin requests return conflict responses with current
  safe metadata for authorized users.

## Failure Recovery, Retry, And Compensation Decisions

- **Checkpoint boundaries**: The runtime checkpoints before accepting a run,
  after persisting run-level configuration pins, before each model or tool side
  effect, after each runtime policy decision is persisted, and after each
  side-effect result is recorded.
- **Lease and retry behavior**: Model and network-capable tool attempts use the
  existing orchestration lease model plus an idempotency key derived from run id,
  step key, tool/action, and pinned decision id. Retries first reload the
  persisted decision and side-effect intent before invoking external work.
- **Compensation behavior**: Model calls are treated as non-compensating
  external observations; retries must not change pinned versions.
  Network-capable tools must record side-effect intent state so failed attempts
  can be retried, marked failed, or surfaced for operator review without
  silently repeating completed effects.

## Secret, Credential, And Outbound Policy Decisions

- **Secret references**: Configuration stores `secret_reference_id`,
  provider key, version metadata, status, allowed scopes, and safe summaries
  only. Raw secret values remain in the secret manager and are resolved at use
  time through existing secret provider abstractions.
- **Secret rotation**: Rotating a secret value behind an existing external
  reference does not rewrite historical run provenance. If the reference
  metadata or allowed scope changes, a new secret-reference version is created.
- **Delegated credentials**: Tool credential requirements can point to platform
  secret references or delegated credential links. Resolution verifies tenant,
  principal/run authorization, status, expiry, revocation, tool/action scope,
  and least-privilege constraints before tool execution.
- **Outbound domains**: Domain policies store normalized host patterns and
  optional port/scheme constraints. Matching lowercases and IDNA-normalizes the
  request host, rejects embedded credentials, treats wildcards as single-label
  unless configured otherwise, and denies ambiguous or malformed destinations.
- **Credential failures**: Missing, inactive, expired, revoked, cross-tenant,
  or out-of-scope credentials return `credential_unsatisfied` and never expose
  provider error bodies or secret material.

## Observability And Audit Decisions

- **Configuration audit**: Every create, activate, deactivate, rollback, and
  migration writes a `ConfigurationAuditRecord` with tenant, actor, role,
  action, config kind, affected scope, prior version, new version, reason,
  trace id, request id, and redacted diff summary.
- **Runtime decision audit**: Every allow or deny decision stores tenant, run,
  step, agent, decision category, outcome, evaluated policy version ids,
  winning model/prompt source when applicable, denial category, safe reason,
  trace id, and retention metadata.
- **Logs, metrics, traces, and timeline events**: Structured logs include ids,
  config kind, outcome, scope hash, and trace id. Metrics, traces, and workflow
  timeline events cover resolver latency, preview latency, activation count,
  rollback count, denied skill/tool/domain/credential counts, missing
  prompt/model counts, runtime first-use decision count, lineage links, replay
  identifiers, tenant id, and config kind with cardinality guards.
- **Admin history**: Minimal web views show active version, prior versions,
  actor, timestamp, reason, affected scope, redacted diff, rollback action
  affordance, and run provenance links for authorized users.

## Test Strategy

- **Deterministic resolver unit tests**: Build table-driven tests for model
  precedence, prompt precedence, absent defaults, inactive model references,
  equal specificity tie rejection, active projection ordering, and stable
  serialization of `ResolvedExecutionConfiguration`.
- **Policy intersection unit tests**: Cover skill bindings, tool action
  categories, overlapping allow policies, explicit deny/missing policy,
  wildcard domain handling, malformed destinations, credential expiry,
  revoked delegated credentials, and secret-reference redaction.
- **Persistence integration tests**: Use PostgreSQL-backed tests for active
  singleton constraints, concurrent activation conflicts, immutable version
  history, rollback active pointer changes, audit rows in the same transaction,
  and no raw secret values in persisted JSON columns.
- **Runtime integration tests**: Start runs with global, workflow, agent, and
  step routing; mutate configuration while queued/running/waiting/resuming;
  verify acceptance pins and first-use pins remain stable; verify denied
  skill/tool/domain/credential decisions persist before side effects.
- **API/admin contract tests**: Exercise CRUD, preview, history, provenance,
  rollback, migration conflict, authorization failure, and minimal web view
  rendering. Contract tests validate OpenAPI examples and stable error
  categories.
- **Coverage gate**: The feature must pass
  `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
  with submitted routing, policy, provenance, and admin API behavior included.

## Documentation And Review Decisions

- **README and docs**: Update `README.md`, `docs/quickstart.md`, and add
  `docs/model-skill-routing.md` with routing precedence, prompt precedence,
  skill/tool/domain/credential policy setup, secret-reference hygiene,
  rollback, migration, admin UI, API endpoints, and reviewer verification.
- **Testing instructions**: Add reviewer instructions for global default,
  workflow/agent/step override, prompt recording, skill allow/deny, tool
  allow/deny, outbound domain denial, credential failure, secret-reference
  audit behavior, rollback, resumed-run pinning, admin views, and provenance
  APIs.
- **PR review notes**: Require notes covering deterministic precedence,
  version pinning, prompt provenance, policy intersection, outbound egress,
  credential requirements, secret handling, audit completeness, authorization,
  migration behavior, rollback limits, and known risks.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
