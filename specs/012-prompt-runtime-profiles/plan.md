# Implementation Plan: Prompt Library And Agent Runtime Profiles

**Branch**: `012-prompt-runtime-profiles` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-prompt-runtime-profiles/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add governed prompt library and agent runtime profile management to the
existing multi-agent platform. The design introduces durable prompt lineages,
editable prompt drafts, immutable published prompt versions, safe fixture
previews, retirement semantics, tenant allowlist grants, agent runtime
profiles, immutable profile versions, repository/service layers, admin JSON
APIs, and browser-first admin views. It integrates with workflow registry
validation, Spec 007 model-skill prompt references, existing memory policy,
existing audit/redaction helpers, and run-level version pinning so published
workflow bundles and accepted runs preserve exact prompt/profile provenance.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation plus deterministic
local-principal test mode, existing workflow registry services, existing
model_skill_config prompt reference behavior, existing memory policy models,
existing audit/debugging capture and redaction helpers, LangChain 1.2.15,
LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5, prometheus-client,
pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: PostgreSQL for prompt lineages, prompt draft heads, immutable
prompt draft revisions, prompt variables, sanitized fixture value sets,
validation/render-test evidence, immutable published prompt versions,
prompt audit records, platform-to-tenant prompt grants, agent runtime
profiles, profile draft revisions, immutable profile versions, profile grants,
profile validation evidence, active profile pointers, workflow validation
references, published bundle pins, and run provenance metadata. Raw secrets,
credential values, unauthorized run content, and unsafe rendered previews are
never persisted.
**Testing**: pytest unit tests for template parsing, variable schema
validation, safe fixture rejection, render previews, immutable lifecycle
guards, profile validation, tenant allowlist checks, profile precedence,
repository constraints, and audit redaction; FastAPI contract tests for JSON
APIs and shared-shell browser views; PostgreSQL-backed integration tests for
Alembic migrations, optimistic concurrency, publish/activate transactions,
retirement, workflow registry validation hooks, Spec 007 prompt reference
creation/validation, run-acceptance and first-use pinning, authorization, and
audit persistence; browser-flow tests for non-developer prompt/profile admin
workflows; docs tests for README, quickstart, PR notes, testing instructions,
and UI guide. Observability validation covers structured logs, trace
correlation, Prometheus metrics, safe admin timeline/debug evidence, fail-closed
audit persistence for security-critical mutations, and tests proving protected
prompt, fixture, credential, and run content never appears in telemetry
payloads. Coverage is enforced at >=90 percent for submitted code.
**Target Platform**: Linux container deployment for the existing FastAPI API,
server-rendered admin console, and background workers; local macOS/Linux
development; PostgreSQL-backed workflow execution under the existing bootstrap
model.
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
server-rendered admin web views, durable workflow runtime workers, PostgreSQL
persistence, and operator-facing documentation.
**Performance Goals**: Prompt and profile list pages p95 <= 200 ms with
indexed tenant/status/search filters for 10k prompt versions and 5k profile
versions; template validation p95 <= 100 ms for prompts up to 64 KB and 100
declared variables; safe fixture preview p95 <= 150 ms without external calls;
workflow validation profile/prompt checks add p95 <= 50 ms per 100 referenced
agents when using active pointer projections; run-acceptance pinning writes
the prompt/profile portion of the execution bundle in one transaction.
**Constraints**: Prompt syntax is limited to `{{variable_name}}` placeholders;
variable names must match `[A-Za-z_][A-Za-z0-9_]*`; expressions, filters,
loops, conditionals, and executable template code are rejected. Published
prompt versions and active profile versions are immutable. Tenant admins can
only manage tenant-scoped assets in their tenant. Platform-scoped prompt
versions and profile versions are tenant-selectable only through explicit
per-version tenant allowlist grants. Browser UI delivery is required and must
be usable by non-developer administrators. Raw secrets, credential values,
provider tokens, unauthorized run content, unsafe fixture values, and unsafe
rendered prompts are prohibited from previews, logs, and audits.
**Scale/Scope**: Initial scope supports platform and tenant prompt libraries,
tenant-specific and platform-fallback agent/sub-agent runtime profiles,
published prompt/profile grants to explicit tenants, browser authoring and
history, API contracts, workflow registry validation hooks, Spec 007 prompt
reference integration, and runtime bundle pinning. Full collaborative editing,
rich template languages, live run-data previews, model calls during preview,
profile benchmarking automation, and cross-tenant inheritance of future
platform versions are out of scope.

**Tenant Limits And Fairness**: All prompt/profile APIs require explicit
tenant or platform scope and use indexed filters. Tenant profile resolution
checks tenant active profile first, then authorized platform active profile.
Preview and validation operations are bounded, side-effect-free, rate-limited
through existing admin controls, and auditable. No workflow queue fairness
changes are required; run acceptance records pinned profile/prompt ids before
runtime execution.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Prompt drafts, immutable versions, render tests, profile versions, grants, validation evidence, active pointers, workflow bundle pins, run pins, and audit records are persisted transactionally before becoming authoritative. |
| Immutable State And Memory | PASS | Published prompt versions and active profile versions are immutable snapshots; editable state is represented by new draft revisions and derived active pointers. Memory policy is referenced as governed profile metadata, not mutable runtime memory. |
| Contract-First Agent Coordination | PASS | Prompt schemas, runtime profile contracts, API contracts, admin web view contracts, workflow validation hooks, and Spec 007 reference flow are defined before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal authorization gates all API and browser actions with deterministic local principals for tests and fail-closed tenant checks. |
| Operability Is A Product Requirement | PASS | Lifecycle actions emit safe audit records, validation evidence, trace ids, history pages, provenance links, PR notes, testing instructions, and browser QA guidance. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks trace to prompt/profile authoring, workflow validation, runtime pinning, UI, tests, docs, and review evidence. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage plus unit, integration, contract, browser, migration, auth, audit, docs, README, PR notes, and testing instruction coverage. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across prompt/profile domain services, repositories, migrations, validation/rendering helpers, workflow/config integration, routers, web views, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Scope and tenant id are explicit in every persistent record and API. Platform assets require explicit per-version tenant grants before tenant selection or review. |
| Version-Pinned Execution | PASS | Published workflow bundles pin prompt reference ids and profile version ids; run acceptance pins all workflow-declared agent/profile/prompt references, with first-use pinning only for dynamic agents not declared upfront. |
| Secret Hygiene And Controlled Tool Access | PASS | Fixture values are sanitized before storage; previews use fixture values only; audit summaries omit raw prompts when unsafe and never include secrets, credentials, or unauthorized run content. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores compact prompt/profile records and validation metadata; large external artifacts are not introduced. Future bulky reports use existing artifact metadata/object storage patterns. |
| Human Approval Is Durable State | PASS | No new runtime approval path is introduced. Admin publish, retire, activate, and grant actions are durable authorized state transitions with audit evidence. |

Post-Phase-1 re-check: design artifacts preserve every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/012-prompt-runtime-profiles/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- prompt-runtime-profiles.openapi.yaml
|   +-- admin-web-views.md
|   +-- runtime-profile-resolution.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- admin_prompts.py               # prompt JSON APIs and shared-shell web routes
    |   |   +-- admin_agent_profiles.py        # profile JSON APIs and shared-shell web routes
    |   +-- schemas/
    |   |   +-- prompts.py                     # prompt request/response schemas and safe errors
    |   |   +-- agent_profiles.py              # profile request/response schemas and safe errors
    |   +-- ui/
    |       +-- prompts.py                     # prompt view models for non-developer admin flows
    |       +-- agent_profiles.py              # profile view models for non-developer admin flows
    +-- admin/
    |   +-- workflow_registry/
    |       +-- validation.py                  # prompt/profile draft and publish hooks
    +-- prompts/
    |   +-- __init__.py
    |   +-- models.py                          # prompt domain value objects and enums
    |   +-- template.py                        # placeholder parser and safe renderer
    |   +-- fixture_safety.py                  # fixture validation and redaction categories
    |   +-- validation.py                      # prompt validation rules
    |   +-- service.py                         # lineage, draft, publish, retire, grants
    |   +-- workflow_hooks.py                  # workflow draft and bundle validation adapters
    |   +-- audit.py                           # safe prompt audit summaries
    +-- agents/
    |   +-- __init__.py
    |   +-- models.py                          # profile domain value objects and enums
    |   +-- validation.py                      # profile validation rules
    |   +-- resolution.py                      # tenant-over-platform profile resolution
    |   +-- service.py                         # profile draft, validate, activate, retire, grants
    |   +-- model_skill_integration.py         # profile prompt references and model-skill hooks
    +-- config/
    |   +-- service.py                         # validate prompt reference targets against library
    |   +-- resolver.py                        # consume pinned prompt/profile ids in provenance
    +-- runtime/
    |   +-- versioning.py                      # include prompt/profile ids in execution bundle
    |   +-- orchestration/
    |       +-- service.py                     # run acceptance and dynamic first-use pinning
    +-- memory/
    |   +-- policy.py                          # profile memory policy compatibility checks
    +-- audit/
    |   +-- classification.py                  # prompt fixture/content redaction categories
    |   +-- capture.py                         # lifecycle and denied-attempt audit events
    +-- db/
    |   +-- models/
    |   |   +-- prompts.py                     # prompt tables and constraints
    |   |   +-- agent_profiles.py              # profile tables and constraints
    |   +-- repositories/
    |       +-- prompts.py                     # prompt transactional repositories and queries
    |       +-- agent_profiles.py              # profile transactional repositories and queries
    +-- web_admin/
        +-- static/
        |   +-- prompt_runtime.js              # progressive validation/preview enhancements
        |   +-- workflow_studio.css            # shared admin-shell styling extensions
        +-- templates/
            +-- prompts/
            |   +-- index.html
            |   +-- edit.html
            |   +-- detail.html
            |   +-- history.html
            |   +-- preview.html
            +-- agent_profiles/
                +-- index.html
                +-- edit.html
                +-- detail.html
                +-- history.html
                +-- resolve.html
alembic/versions/
+-- 0012_prompt_runtime_profiles.py
tests/
+-- contract/
|   +-- test_prompt_library_contract.py
|   +-- test_prompt_lifecycle_contract.py
|   +-- test_agent_profiles_contract.py
|   +-- test_runtime_profile_resolution_contract.py
|   +-- test_prompt_runtime_profiles_contract.py
+-- integration/
|   +-- api/
|   |   +-- test_admin_prompts_api.py
|   |   +-- test_admin_prompts_ui.py
|   |   +-- test_admin_agent_profiles_ui.py
|   |   +-- test_prompt_runtime_browser_flows.py
|   |   +-- test_agent_profile_browser_flows.py
|   +-- db/
|   |   +-- test_prompt_runtime_profiles_migration.py
|   +-- model_skill_config/
|   |   +-- test_prompt_reference_library_integration.py
|   +-- runtime/
|   |   +-- test_prompt_profile_pinning.py
|   +-- workflows/
|       +-- test_prompt_profile_workflow_validation.py
+-- unit/
    +-- api/
    |   +-- test_prompt_runtime_common_schemas.py
    |   +-- test_prompt_runtime_ui_models.py
    +-- auth/
    |   +-- test_prompt_runtime_policy.py
    +-- db/
    |   +-- test_prompt_models.py
    |   +-- test_agent_profile_models.py
    |   +-- test_prompt_repository.py
    |   +-- test_agent_profile_repository.py
    +-- prompts/
        +-- test_template.py
        +-- test_fixture_safety.py
        +-- test_preview.py
        +-- test_prompt_service.py
        +-- test_publication.py
        +-- test_retirement.py
        +-- test_tenant_isolation.py
        +-- test_validation.py
    +-- agents/
        +-- test_profile_service.py
        +-- test_prompt_reference_validation.py
        +-- test_memory_policy_validation.py
        +-- test_profile_validation.py
        +-- test_profile_resolution.py
    +-- audit/
        +-- test_prompt_runtime_audit.py
+-- performance/
    +-- prompt_runtime/
        +-- test_prompt_runtime_latency.py
+-- docs/
    +-- test_prompt_runtime_profiles_docs.py
README.md
docs/quickstart.md
docs/prompt-runtime-profiles.md
docs/prompt-runtime-profiles-pr-notes.md
docs/prompt-runtime-profiles-testing.md
```

**Structure Decision**: Keep prompt authoring and agent profile behavior in
focused `multi_agent_platform.prompts` and `multi_agent_platform.agents`
packages. Keep persistence in SQLAlchemy models/repositories, browser views in
the existing shared admin shell, and integration hooks in the existing workflow
registry, model_skill_config, memory, runtime versioning, and audit modules.

## Prompt And Profile Design

- **Prompt library**: `prompt_lineages` identify a governed prompt family in
  platform or tenant scope. `prompt_versions` store immutable published
  snapshots. Editable authoring is handled through current draft heads and
  immutable draft revisions rather than in-place edits.
- **Template validation**: `prompts.template` parses literal
  `{{variable_name}}` placeholders only, rejects invalid names and any template
  syntax outside the approved placeholder form, and compares usage against the
  declared variable schema.
- **Variable schema**: declarations include name, purpose, required flag,
  allowed value category, sample guidance, and safety classification. Publish
  requires declarations and usage to align.
- **Safe fixture previews**: fixture sets are sanitized before persistence and
  preview. Preview uses fixture values only, performs no model calls and no live
  run-data lookups, stores safe render-test metadata, and audits only safe
  summaries.
- **Immutable lifecycle**: publishing creates a new prompt version with content
  digest, variable declarations, validation evidence, author, reason, and
  scope. Retirement blocks new selection but leaves historical review and
  existing pins intact.
- **Runtime profiles**: profiles bind exactly one agent key or sub-agent key in
  a scope to purpose, prompt version references, model routing hints, memory
  scope policy, skill requirements, tool policy expectations, output contracts,
  and test-suite requirements.
- **Profile versioning**: activating a validated draft creates an immutable
  profile version and updates a conflict-protected active pointer. Tenant
  active profiles take precedence over authorized platform profile versions for
  the same key; platform profiles are fallback only.
- **Allowlist grants**: platform prompt/profile versions become tenant-visible
  only through explicit per-version tenant grants. Grants never inherit to
  future versions or entire lineages.
- **Workflow validation hooks**: workflow drafts and publications validate
  prompt references and agent/sub-agent keys against active authorized prompt
  versions and runtime profile versions. Blocking findings include missing,
  retired, unauthorized, wrong-scope, stale, incompatible, or conflicting
  references.
- **Spec 007 prompt reference flow**: Prompt library publishes the canonical
  `prompt_version_id` and digest. Spec 007 `PromptReferenceVersion` rows keep
  their existing workflow/agent/step scope behavior and point to an active,
  authorized `prompt_versions.prompt_version_id`. Spec 007 validation calls the
  prompt library repository before creating or activating prompt references.
- **Published workflow bundle pins**: workflow publication stores prompt
  reference version ids plus resolved prompt version ids/profile version ids in
  the compiled bundle summary. Run acceptance persists those ids in the pinned
  execution bundle. Dynamically selected agents that were not declared upfront
  create first-use pins with audit evidence before model or tool side effects.

## Admin UI Plan

The UI must be the primary path for non-developer administrators. Add two
shared-shell navigation entries: **Prompt Library** and **Agent Profiles**.

- Prompt Library list: searchable, filterable table with scope, lineage,
  latest draft state, latest published version, retired status, validation
  state, tenant grant summary, updated timestamp, and clear actions.
- Prompt authoring: guided form with sections for overview, prompt content,
  variable declarations, fixture sets, validation results, preview, publish,
  grant, retire, and history. The form uses labels, help text, inline errors,
  disabled action states, and plain-language remediation.
- Prompt preview: side-by-side template and rendered fixture preview with
  safety badges, missing-variable warnings, redaction notices, and no raw
  protected content in audit payloads.
- Agent Profiles list: searchable, filterable table with agent key, agent kind,
  scope, active version, validation state, prompt references, model/memory/tool
  summary, tenant grants, and updated timestamp.
- Profile authoring: guided sections for purpose, prompt references, model
  routing hints, memory policy, skill requirements, tool expectations, output
  contracts, test-suite requirements, validation, activation, grant, retire,
  and history.
- History and audit: timeline views show actor, timestamp, action, reason,
  prior/new version, safe validation summary, grant changes, and provenance
  links without exposing unauthorized content.
- Workflow integration: workflow studio validation surfaces prompt/profile
  blocking findings in plain language and links authorized users to the
  relevant prompt/profile detail page.
- Accessibility: all flows remain usable without optional JavaScript; JS only
  enhances fixture table editing, validation preview refresh, and unsaved-change
  prompts. Buttons and forms expose disabled reasons instead of hiding needed
  context.

## API And Authorization

- Platform admins can create, publish, retire, activate, grant, and
  audit platform-scoped prompt/profile versions.
- Tenant admins can create, publish, retire, activate, and audit
  tenant-scoped prompt/profile versions within their tenant.
- Tenant users can view/select platform-scoped versions only when a specific
  published prompt version or active profile version has an active grant for
  their tenant.
- Unauthorized records use safe not-found or safe forbidden responses according
  to existing admin policy and never include cross-scope identifiers that reveal
  protected assets.
- Denied validation, preview, publish, retire, activate, grant, and selection
  attempts emit safe audit records if audit persistence is available; security
  critical mutation fails closed when audit persistence is unavailable.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
