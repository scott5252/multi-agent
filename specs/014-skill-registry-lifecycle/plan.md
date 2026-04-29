# Implementation Plan: Skill Registry And Installation Lifecycle

**Branch**: `014-skill-registry-lifecycle` | **Date**: 2026-04-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-skill-registry-lifecycle/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a governed skill registry that lets platform admins publish immutable,
platform-approved declarative skill package versions and lets tenant admins
install authorized versions, configure secret references or delegated
credential requirements, run declared smoke tests, and expose ready
installations to existing Spec 007 skill-binding policy. The implementation is
additive inside the current FastAPI control plane: SQLAlchemy/Alembic models
store lifecycle state and compact evidence, object storage holds immutable
package artifacts and oversized validation reports, existing secret providers
and model-skill policy records remain authoritative, and admin web/API views
surface publication, tenant installation, readiness, quarantine, upgrade, and
audit evidence without storing raw secrets or credential values.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing secret providers, existing delegated credential metadata,
existing model_skill_config skill bindings, allowed tool policies, outbound
domain policies, credential requirement policies, existing workflow registry
publish validation hooks, existing object storage providers, existing audit
and redaction helpers, existing reliability quotas/retries/breakers,
prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: PostgreSQL for `skill_packages`, `skill_package_versions`,
tenant availability grants, `skill_installations`,
`skill_installation_tests`, credential readiness references,
quarantine decisions, installation upgrade lineage, binding eligibility
projections, and `skill_audit_records`; object/artifact storage for immutable
package artifacts, safe documentation payloads, fixture bundles, pinned
manifest snapshots, validation evidence, and oversized smoke-test reports
anchored by PostgreSQL metadata and digests
**Testing**: pytest unit tests, pytest-asyncio integration tests,
FastAPI/httpx API tests, server-rendered admin UI tests, OpenAPI contract
tests, manifest schema fixtures, migration tests, object-storage/reliability
failure tests, workflow publish validation integration tests, docs tests,
reviewer QA scripts, Ruff, mypy, and coverage gate at 90 percent for submitted
code
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, shared workers, and configured object storage provider
**Project Type**: Multi-tenant Python web service with server-rendered admin
UI, JSON admin APIs, durable lifecycle workflows, and policy integration with
runtime configuration
**Performance Goals**: Authorized package discovery p95 <= 200 ms for scoped
results; package and installation detail p95 <= 250 ms excluding artifact
downloads; manifest validation p95 <= 3 s for static checks; validation or
smoke-test job acceptance p95 <= 500 ms; smoke-test runner starts within 30 s
when up to 100 tenants each have no more than 2 active validation jobs, 2 active
smoke-test jobs, 25 queued lifecycle jobs, and fixture/evidence artifact I/O
within the configured per-tenant throughput budget; workflow publish validation
adds <= 500 ms p95 for installed-skill eligibility checks
**Constraints**: V1 manifests are declarative and may only reference existing
approved tool/MCP integrations; arbitrary executable package code and
standalone external HTTP service entrypoints are rejected; raw package secrets,
raw credential values, provider tokens, unsafe package payloads, and
cross-tenant data cannot be stored or rendered; published package versions and
tenant installation versions are immutable; mutable readiness, credential
configuration, smoke-test promotion, and binding eligibility changes require
optimistic concurrency tokens; quarantine must block new installs, readiness
promotion, new bindings, and runtime use without deleting history; all package
artifact writes are content-addressed, checksum-verified, idempotent, and
audited
**Scale/Scope**: Hundreds of package slugs, low thousands of package versions,
tens of thousands of tenant installations platform-wide, low dozens of smoke
tests per installation, hundreds of tenants, and concurrent platform/tenant
admins using package, installation, readiness, and audit pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Package validation, publication, availability changes, tenant installs, credential readiness, smoke-test execution, quarantine, and audit records persist authoritative state with idempotency keys and retry-safe job records. |
| Immutable State And Memory | PASS | Published package versions, artifact digests, manifest snapshots, safe docs, fixtures, tenant installation versions, smoke-test evidence, and binding references are immutable; upgrades create new installation versions. |
| Contract-First Agent Coordination | PASS | Manifest schema, admin APIs, smoke-test runner input/output, Spec 007 binding eligibility, and workflow publish validation contracts are explicit and versioned. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal authorization, tenant scope checks, and admin shell protections govern all platform and tenant routes while preserving deterministic test principals. |
| Operability Is A Product Requirement | PASS | Validation findings, smoke-test evidence, readiness findings, policy preview outcomes, quarantine decisions, metrics, traces, safe audit events, and reviewer QA evidence are planned before implementation. |
| Spec-Driven Delivery | PASS | This plan produces research, data model, contracts, and quickstart artifacts before task generation and implementation. |
| Test And Documentation Discipline | PASS | Unit, integration, migration, contract, rendered UI, policy, docs, and reviewer QA tests are required with >=90 percent submitted-code coverage plus README and user docs updates. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to additive registry lifecycle modules, DB models/repositories, admin/API surfaces, object-storage integration, policy adapters, smoke-test runner, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | Discovery, installation, smoke tests, credential readiness, binding eligibility, audit review, exports, and worker admission carry tenant scope and use existing reliability controls. |
| Version-Pinned Execution | PASS | Runtime and workflow publish validation consume exact installed skill installation versions and package artifact/manifest digests; bindings never float to newer versions automatically. |
| Secret Hygiene And Controlled Tool Access | PASS | Manifests declare credential requirements and tool/network permissions; tenant installs store only secret references or delegated credential metadata and reuse Spec 007 tool/domain/credential policy evaluation. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores lifecycle metadata and compact evidence; package artifacts, safe docs, fixture bundles, and oversized validation/smoke reports use object storage with PostgreSQL metadata. |
| Human Approval Is Durable State | PASS | No runtime approval flow is introduced; delegated credential approvals and admin quarantine/resolution actions are persisted and audited as durable state. |

Post-Phase-1 re-check: the research, data model, contracts, and quickstart keep
all constitution gates in `PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/014-skill-registry-lifecycle/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── skill-registry.openapi.yaml
│   ├── admin-skill-registry-ui.md
│   ├── manifest-schema.md
│   └── policy-and-smoke-runner.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── skill_registry/
│       ├── artifact_store.py           # content-addressed package artifact writes/reads
│       ├── audit.py                    # safe skill lifecycle audit helper
│       ├── eligibility.py              # Spec 007 and workflow publish eligibility adapter
│       ├── fairness.py                 # tenant quotas, throughput budgets, and fair scheduling
│       ├── jobs.py                     # persisted validation/smoke job leases, retries, idempotency
│       ├── manifest.py                 # Pydantic manifest schema and validation rules
│       ├── metrics.py                  # Prometheus metrics for lifecycle and reliability events
│       ├── observability.py            # structured log/trace helpers and safe labels
│       ├── quarantine.py               # package/installation quarantine decisions
│       ├── readiness.py                # installation readiness and findings
│       ├── service.py                  # package, version, availability, install lifecycle
│       ├── smoke_runner.py             # isolated declared smoke-test orchestration
│       ├── validation.py               # package candidate validation pipeline
│       └── validation_runner.py        # isolated package validation job runner
├── api/
│   ├── routers/
│   │   └── admin_skill_registry.py     # JSON APIs and server-rendered pages
│   ├── schemas/
│   │   └── skill_registry.py           # request/response schemas
│   └── ui/
│       └── skill_registry.py           # admin page view models
├── db/
│   ├── models/
│   │   └── skill_registry.py           # new SQLAlchemy lifecycle tables
│   └── repositories/
│       └── skill_registry.py           # scoped queries and optimistic writes
├── runtime/
│   └── skill_registry.py               # runtime eligibility and quarantine checks
└── web_admin/
    └── templates/
        └── skill_registry/
            ├── package_list.html
            ├── package_detail.html
            ├── package_version_detail.html
            ├── package_candidate_form.html
            ├── installation_list.html
            ├── installation_detail.html
            ├── installation_configure.html
            └── components/
                ├── readiness_panel.html
                ├── validation_findings.html
                ├── smoke_test_history.html
                └── policy_eligibility.html

alembic/versions/
└── 0014_skill_registry_lifecycle.py

tests/
├── contract/
│   └── test_skill_registry_contract.py
├── integration/
│   ├── api/
│   │   ├── test_admin_skill_registry_api.py
│   │   └── test_admin_skill_registry_ui.py
│   ├── skill_registry/
│   │   ├── test_skill_installation_lifecycle.py
│   │   ├── test_skill_policy_integration.py
│   │   ├── test_skill_validation_runner.py
│   │   ├── test_skill_smoke_runner.py
│   │   └── test_skill_workflow_publish_validation.py
│   └── migrations/
│       └── test_skill_registry_migration.py
├── unit/
│   ├── admin/
│   │   ├── test_skill_manifest.py
│   │   ├── test_skill_package_validation.py
│   │   ├── test_skill_registry_fairness.py
│   │   ├── test_skill_registry_jobs.py
│   │   ├── test_skill_registry_observability.py
│   │   ├── test_skill_readiness.py
│   │   ├── test_skill_quarantine.py
│   │   └── test_skill_artifact_store.py
│   └── api/
│       ├── test_skill_registry_schemas.py
│       └── test_skill_registry_ui_models.py
└── docs/
    └── test_skill_registry_docs.py

docs/
├── skill-registry.md
├── skill-registry-testing.md
└── skill-registry-pr-notes.md
README.md
```

**Structure Decision**: Keep the registry inside the existing FastAPI
control-plane service and shared admin shell. New code is additive under
`admin/skill_registry`, `api/routers`, `api/schemas`, `api/ui`,
`db/models`, and `db/repositories`; existing `config/model_skill` records,
secret providers, workflow publish validation, artifact storage,
audit/redaction, and reliability services remain the authoritative owners for
their domains.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves the lifecycle architecture around eight design decisions.
See [research.md](./research.md).

Key decisions:

- Use a declarative v1 skill package format that references existing approved
  tool/MCP integrations only.
- Persist package/version/installation lifecycle state in PostgreSQL and store
  immutable package artifacts, docs, fixtures, and oversized evidence in object
  storage with pinned digests.
- Validate manifests, docs, fixtures, network requirements, credential
  requirements, tool declarations, compatibility, and requested runtime
  permissions before publication.
- Model tenant installs as immutable installation versions with mutable
  readiness projections guarded by optimistic concurrency tokens.
- Run package validation and tenant smoke tests through isolated,
  policy-constrained jobs using declared fixtures and existing reliability
  admission, retry, breaker, and audit controls.
- Package validation uses a persisted validation job runner with
  policy-constrained access to declared manifest, safe documentation, fixtures,
  approved tool/MCP references, and declared network requirements. Undeclared
  network access, raw credential access, cross-tenant data access, and
  persistent side effects outside declared validation scope fail closed and
  produce blocking findings.
- Integrate with Spec 007 by making only ready, non-quarantined, tenant-visible
  installed skill versions eligible for skill-binding creation, policy preview,
  runtime resolution, and workflow publish validation.
- Treat upgrades as new installation versions; rollback means explicitly
  reactivating or rebinding an older installed version that is still eligible.
- Provide platform and tenant admin web views plus JSON APIs over safe
  summaries, never raw package secrets or credential values.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines `skill_packages`,
  `skill_package_versions`, package artifacts, manifests, availability grants,
  `skill_installations`, credential readiness, smoke test results,
  quarantine decisions, upgrade lineage, binding eligibility, and
  `skill_audit_records`.
- [contracts/skill-registry.openapi.yaml](./contracts/skill-registry.openapi.yaml)
  defines admin APIs for platform package publication, tenant discovery,
  installation, credential configuration, smoke tests, readiness, quarantine,
  binding eligibility, workflow publish validation, and audit review.
- [contracts/admin-skill-registry-ui.md](./contracts/admin-skill-registry-ui.md)
  defines server-rendered platform and tenant admin pages, safety states,
  conflict behavior, redaction, and accessibility expectations.
- [contracts/manifest-schema.md](./contracts/manifest-schema.md) defines the
  declarative manifest schema, validation rules, digest behavior, and rejected
  entrypoint shapes.
- [contracts/policy-and-smoke-runner.md](./contracts/policy-and-smoke-runner.md)
  defines smoke-test runner inputs/outputs, reliability controls, Spec 007
  policy integration, upgrade/rollback behavior, runtime guardrails, and
  workflow publish validation.
- [quickstart.md](./quickstart.md) defines local-principal reviewer flows,
  lifecycle QA, quarantine checks, optimistic concurrency checks, policy and
  workflow publish checks, audit checks, and automated validation commands.

## API Endpoints

The feature adds typed admin JSON APIs under `/admin/skill-registry`:

- Platform package and version management:
  `GET/POST /packages`, `GET /packages/{slug}`,
  `POST /packages/{slug}/versions/validate`,
  `POST /packages/{slug}/versions/publish`,
  `GET /packages/{slug}/versions/{version}`,
  `POST /packages/{slug}/versions/{version}/availability`,
  `POST /packages/{slug}/versions/{version}/withdraw`, and
  `POST /packages/{slug}/versions/{version}/quarantine`.
- Tenant discovery and installation:
  `GET /available`, `POST /installations`,
  `GET /installations`, `GET /installations/{installation_id}`,
  `POST /installations/{installation_id}/credentials`,
  `POST /installations/{installation_id}/smoke-tests`,
  `POST /installations/{installation_id}/readiness`,
  `POST /installations/{installation_id}/quarantine`, and
  `POST /installations/{installation_id}/upgrade`.
- Policy and publish integration:
  `GET /installations/{installation_id}/binding-eligibility`,
  `POST /installations/{installation_id}/binding-preview`,
  and `POST /workflow-publish/validate-installed-skills`.
- Evidence and audit:
  `GET /installations/{installation_id}/tests`,
  `GET /audit`, and export endpoints that use existing safe export/redaction
  helpers.

## Admin Web Views

- **Platform package list** (`/admin/skill-registry/ui/packages`): filter by
  slug, owner, lifecycle state, validation status, quarantine state, tenant
  availability, and latest semantic version.
- **Package detail**: safe package summary, version lineage, validation
  history, tenant grants, documentation status, artifact digests, quarantine
  decisions, and audit links.
- **Package candidate form**: upload/register artifact metadata, manifest,
  safe docs, fixtures, requested permissions, declared tools, compatibility,
  and publication notes.
- **Package version detail**: immutable manifest summary, artifact provenance,
  validation evidence, availability grants, install counts, withdrawal state,
  and quarantine state.
- **Tenant installation list** (`/admin/skill-registry/ui/installations`):
  tenant-scoped installs with readiness, smoke-test status, credential status,
  binding eligibility, quarantine, upgrade availability, and pinned version.
- **Tenant installation detail**: installation version, package provenance,
  credential readiness, smoke-test evidence, readiness findings, policy
  preview, binding links, upgrade lineage, and safe audit summaries.
- **Configure credentials and tests**: forms for secret references or
  delegated credential requirements, smoke-test execution, stale token
  conflicts, and readiness promotion.

## Authorization

- Platform package creation, validation, publication, tenant availability,
  withdrawal, and package-version quarantine require platform admin roles.
- Tenant discovery, installation, credential configuration, smoke testing,
  readiness promotion, and binding preview require tenant admin scope for the
  selected tenant.
- Platform admins may inspect all safe summaries and quarantine tenant
  installations; tenant admins may inspect only their tenant's installations,
  tests, credentials, bindings, and audit records.
- Workflow publish validation uses the workflow author's tenant and existing
  workflow registry authorization. Cross-tenant or unavailable installed skill
  references fail closed and produce safe audit records.

## Policy Integration And Runtime Eligibility

Installed skills become eligible for Spec 007 skill bindings only when all
conditions are true:

1. The tenant installation pins a published package version available to the
   tenant when installed.
2. The installation readiness state is `ready`, with required credentials,
   compatibility, permissions, and smoke tests satisfied.
3. Neither the package version nor the tenant installation is quarantined, and
   the package version is not blocked for runtime use.
4. Manifest-declared tools and action categories match existing allowed tool
   policy vocabulary and approved tool/MCP integration references.
5. Required outbound domains and credential requirements are satisfiable by
   active Spec 007 outbound domain policies, secret reference versions, and
   delegated credential links for the binding scope.
6. Binding creation or workflow publish supplies the current optimistic
   concurrency token and receives an allow result from the existing
   model_skill_config policy preview service.

Workflow publish validation must reject workflow roles that reference missing,
non-ready, stale, quarantined, unauthorized, or policy-incompatible
installations. Published workflows and runtime configuration pin exact
installation ids, installation versions, package slug/version, and manifest
digest evidence.

## Upgrade, Rollback, And Quarantine

- Upgrades create a new immutable tenant installation version from a newer
  package version and link it to the prior installation through upgrade
  lineage.
- Existing bindings remain pinned to their original installed skill version
  until an authorized admin creates a new Spec 007 skill binding, updates an
  agent profile, or publishes a workflow that references the new installation.
- Rollback means explicitly rebinding or republishing to a prior eligible
  installation version. Historical installation records are never mutated.
- Withdrawing a package version blocks new installations but does not remove
  existing installs or bindings unless a separate quarantine/runtime block is
  active.
- Quarantine can target package versions or tenant installations. It blocks new
  installs, readiness promotion, new bindings, workflow publish, and runtime
  use for affected installations while preserving safe history and audit
  evidence.

## Observability And Reliability

- Emit metrics for validation attempts, validation duration, publication
  outcomes, artifact write/read failures, tenant install attempts, smoke-test
  runs, readiness promotions, binding eligibility denials, quarantine actions,
  and workflow publish validation denials.
- Add structured logs and traces keyed by `trace_id`, tenant, package slug,
  semantic version, installation id/version, validation job id, and smoke-test
  run id, excluding raw package payloads and credentials.
- Use existing reliability admission and quotas for validation and smoke-test
  jobs, artifact-store concurrency counters for artifact I/O, retry schedules
  for retryable object storage or runner failures, and circuit breakers for
  unhealthy tool/MCP integration probes.
- Validation and smoke-test admission enforce tenant-scoped quotas before work
  is accepted: each tenant receives a configurable concurrent validation-job
  limit, concurrent smoke-test-job limit, queued-job limit, and artifact
  throughput budget.
- Shared validation and smoke-test workers use fair scheduling across tenants by
  selecting runnable jobs in tenant round-robin order, then oldest-created job
  within that tenant, while preserving per-tenant lease and retry rules.
- Quota and fairness decisions emit metrics and safe audit summaries for
  accepted, queued, throttled, rejected, retried, and expired jobs, keyed by
  tenant, job type, decision, and reason without package payloads or credential
  values.
- Validation and smoke-test runs persist job records before execution with
  tenant scope, idempotency key, requested package or installation version,
  lease owner, lease expiry, retry count, and terminal outcome.
- Artifact writes use content-addressed idempotency: retrying the same digest
  must not create duplicate package artifacts, documentation payloads, fixtures,
  or evidence objects.
- Retryable object-storage or runner failures remain pending with safe failure
  summaries; non-retryable failures transition to failed and block publication
  or readiness without mutating immutable package or installation versions.
- Compensation for partially completed external side effects is record-based:
  orphaned artifact objects are ignored unless referenced by committed
  PostgreSQL metadata, and failed jobs emit audit records plus retry or cleanup
  evidence.
- Persist safe audit records for every lifecycle mutation, denied access,
  stale token rejection, validation/smoke-test outcome, quarantine decision,
  restricted-content redaction, binding attempt, and workflow publish
  validation outcome.

## Test Strategy

- Unit tests cover manifest validation, semantic version uniqueness, slug
  normalization, rejected entrypoints, permission and domain checks, artifact
  digest computation, readiness state transitions, quarantine effects,
  eligibility checks, and safe audit payloads.
- Integration tests cover Alembic migrations, package publication, tenant
  availability, tenant install, credential-reference readiness, delegated
  credential readiness, smoke-test runs, readiness promotion, upgrade, rollback
  by explicit rebinding, quarantine, audit review, and failure recovery.
- API and UI tests cover platform and tenant authorization, safe not-found
  behavior, optimistic concurrency 409 responses, redaction, form errors,
  filtered lists, details, exports, and accessibility-visible safety states.
- Contract tests validate OpenAPI examples, manifest schema examples, runner
  input/output fixtures, Spec 007 binding preview requests, and workflow
  publish validation failures.
- Reviewer evidence must include `uv run ruff check .`,
  `uv run ruff format --check .`, `uv run mypy src`, and
  `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.
