# Implementation Plan: Skill Registry Lifecycle Browser Workflows

**Branch**: `014-skill-registry-lifecycle-v2` | **Date**: 2026-04-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-skill-registry-lifecycle-v2/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Close the Spec 014 UI workflow gap by making every primary skill lifecycle
action executable from the existing server-rendered admin browser UI. The
implementation is additive: reuse the existing FastAPI admin skill registry
router, Starlette/Jinja2 admin shell templates, local-principal/Auth0
authorization, skill registry service/schema patterns, audit/redaction helpers,
and current skill registry templates, then add guided browser forms and POST
handlers for package creation, manifest entry/upload, validation, publication,
tenant grants, tenant discovery, installation, credential reference
configuration, smoke-test/readiness evidence, binding eligibility preview,
stale-revision recovery, and redaction-safe tenant isolation checks.

JSON API endpoints remain available for automation, diagnostics, and
integration tests, but they are no longer the primary QA path for
non-technical users. The QA UI walkthrough must use browser actions for all
feature lifecycle actions; terminal commands are limited to environment setup,
server startup, diagnostics, and automated evidence collection.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, python-multipart form/file handling if not already present through
FastAPI, existing skill registry services/schemas/templates, existing admin
shell navigation, existing secret providers and delegated credential metadata,
existing model_skill_config resolver and policy preview APIs, existing
audit/redaction helpers, existing reliability job controls, prometheus-client,
pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: Reuse existing Spec 014 PostgreSQL tables for skill packages,
manifest candidates or validation evidence, immutable package versions, tenant
availability grants, tenant installations, credential readiness, smoke-test
evidence, binding eligibility projections, revision tokens, and audit records;
reuse object/artifact storage only for existing package artifacts, safe docs,
fixtures, pinned manifests, validation evidence, and oversized smoke-test
reports. No new migration is required unless implementation discovers the
current schema lacks persisted manifest candidate revisions or browser form
idempotency evidence.
**Testing**: pytest unit tests for form models, page view models, validation
mapping, redaction, and stale conflict handling; pytest-asyncio/httpx
integration tests for GET/POST browser flows, authorization, tenant scope,
status codes, redirects, and template rendering; existing API contract tests
remain; docs tests verify the QA UI guide has zero curl/SQL/direct API commands
for primary feature actions; optional Playwright screenshot smoke test for the
complete browser walkthrough.
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
shared admin shell, local-principal test login, and worker process for queued
smoke tests.
**Project Type**: Multi-tenant Python web service with server-rendered admin
UI and JSON admin APIs.
**Performance Goals**: Browser GET pages p95 <= 250 ms for scoped package,
version, installation, and available-version views excluding artifact reads;
form POST acceptance p95 <= 500 ms for package, grant, install, credential,
eligibility preview, and smoke-test enqueue actions; inline manifest parse and
schema validation p95 <= 3 s for QA-sized manifests; smoke-test run/rerun POST
must enqueue and return without synchronously waiting for final execution.
**Constraints**: Browser UI must not render raw package payloads, raw
credential values, provider tokens, unsafe docs, unsafe fixtures, or
cross-tenant data. YAML and JSON manifest entry/upload must be parsed through
structured parsers and validated against the existing v1 manifest schema.
Published versions and tenant installation versions remain immutable. Candidate
edits, grants, credential configuration, readiness/smoke actions, and
binding-related mutable actions use optimistic revision tokens. Cross-tenant
direct links render absent/not found without existence hints; same-tenant role
failures render access denied. All mutation forms must work without custom
JavaScript beyond optional refresh/polling enhancements.
**Scale/Scope**: One focused UI increment across the existing skill registry
admin surface: about 10 browser routes, 8-10 templates/partials, form/view
models, scoped POST handlers, targeted tests, and QA guide updates. Backend
lifecycle services, schemas, repositories, audit, redaction, policy, and
worker behaviors are reused where possible.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Browser POST handlers delegate to existing persisted service operations, idempotency behavior, queued smoke-test jobs, and audit records rather than holding transient browser state as authority. |
| Immutable State And Memory | PASS | Publication and installation remain immutable; browser actions only create new candidate revisions, published versions, grants, readiness evidence, and audit records. |
| Contract-First Agent Coordination | PASS | UI route/form contracts are documented, API contracts remain available, and manifest validation continues to use the existing v1 schema. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal auth, admin role checks, tenant scope handling, CSRF/session protections where available, and safe local QA principals remain authoritative. |
| Operability Is A Product Requirement | PASS | Validation findings, readiness evidence, smoke-test job status, binding preview outcomes, stale conflict rejections, denials, redactions, and screenshot QA evidence are explicit plan outputs. |
| Spec-Driven Delivery | PASS | This plan produces V2 research, data model notes, contracts, and quickstart before task generation and implementation. |
| Test And Documentation Discipline | PASS | Browser route, template, authorization, stale conflict, redaction, docs, and screenshot-backed QA tests are required while preserving the 90 percent coverage gate. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `api/routers/admin_skill_registry.py`, `api/ui/skill_registry.py`, `api/schemas/skill_registry.py`, `web_admin/templates/skill_registry/`, existing service/repository adapters only as needed, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant scope is explicit in discovery, install, credential, smoke-test, readiness, eligibility, and audit UI flows; queued smoke-test actions reuse existing fair scheduling and reliability controls. |
| Version-Pinned Execution | PASS | Browser publication, installation, and binding preview display exact semantic versions, installation versions, manifest digests, artifact digests, and pinned binding semantics. |
| Secret Hygiene And Controlled Tool Access | PASS | Credential forms use tenant-authorized pickers and delegated safe metadata only; no arbitrary reference id text boxes or raw secret fields are allowed in the final UI. |
| Tiered Storage For Large Payloads | PASS | The UI uploads or references manifests and artifacts through existing artifact/evidence storage boundaries; PostgreSQL remains metadata/source-of-truth storage. |
| Human Approval Is Durable State | PASS | Platform publish/grant and tenant readiness actions are explicit persisted admin decisions with audit evidence; no new runtime approval flow is introduced. |

Post-Phase-1 re-check: the research, data model, UI contract, and quickstart
keep all constitution gates in `PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/014-skill-registry-lifecycle-v2/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── admin-skill-registry-browser-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/
│   │   └── admin_skill_registry.py      # existing API routes plus UI GET/POST handlers
│   ├── schemas/
│   │   └── skill_registry.py            # existing API schemas plus browser form parsing models if shared
│   └── ui/
│       └── skill_registry.py            # page models, form models, safe view mapping
├── admin/
│   └── skill_registry/
│       ├── service.py                   # reused lifecycle operations; small adapters only if needed
│       ├── validation.py                # reused validation findings
│       ├── readiness.py                 # reused credential/readiness summaries
│       ├── smoke_runner.py              # reused queued evidence model
│       ├── eligibility.py               # reused binding decision model
│       └── audit.py                     # reused safe audit helper
└── web_admin/
    └── templates/
        └── skill_registry/
            ├── package_list.html
            ├── package_create.html
            ├── package_detail.html
            ├── package_candidate_form.html
            ├── package_version_detail.html
            ├── tenant_grant_form.html
            ├── available_versions.html
            ├── installation_list.html
            ├── installation_detail.html
            ├── installation_configure.html
            └── components/
                ├── form_errors.html
                ├── validation_findings.html
                ├── readiness_panel.html
                ├── smoke_test_history.html
                ├── policy_eligibility.html
                ├── stale_conflict.html
                └── audit_timeline.html

tests/
├── integration/
│   └── api/
│       └── test_admin_skill_registry_ui.py
├── unit/
│   └── api/
│       ├── test_skill_registry_ui_models.py
│       └── test_admin_skill_registry_router.py
└── docs/
    └── test_skill_registry_docs.py

specs/014-skill-registry-lifecycle/
└── qa014_ui.md                           # updated after implementation to browser-first V2 walkthrough
```

**Structure Decision**: Keep the browser workflows inside the existing
FastAPI/admin shell code path. Do not create a separate frontend or duplicate
lifecycle services. The plan allows a migration only if implementation proves
candidate revision persistence or browser form idempotency cannot be expressed
with existing tables.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves the V2 UI gap around seven design decisions. See
[research.md](./research.md).

Key decisions:

- Add browser POST handlers over existing service methods, keeping JSON APIs
  available but secondary for non-technical QA.
- Model browser forms as typed Pydantic/form parsing objects that map to
  existing request/service schemas and return safe template contexts.
- Accept YAML or JSON manifest paste/upload through structured parsers, then
  store/render only safe candidate summaries, revisions, digests, and findings.
- Use existing admin shell authorization and tenant-scope rules; cross-tenant
  direct links get not-found/absent states while same-tenant role failures get
  denied states.
- Use hidden revision tokens on mutable forms and render stale conflicts with
  a reload/retry path, never applying stale writes.
- Render credential reference configuration through tenant-authorized pickers
  and predefined delegated metadata fields, not free-form secret identifiers.
- Reuse existing smoke-test jobs and readiness evidence, rendering queued,
  running, final, blocked, and failed states through refresh or optional
  polling.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) documents UI-facing entities and confirms
  reuse of the existing Spec 014 lifecycle storage, with migration/data
  considerations only for candidate revisions and form idempotency if needed.
- [contracts/admin-skill-registry-browser-ui.md](./contracts/admin-skill-registry-browser-ui.md)
  defines the browser routes, forms, POST actions, validation behavior,
  authorization behavior, stale conflict behavior, tenant scope behavior, and
  redaction contract.
- [quickstart.md](./quickstart.md) defines the browser-first reviewer flow and
  states that API endpoints remain available but are no longer the primary QA
  path for non-technical users.

## Browser UI Routes And Actions

All routes live under `/admin/skill-registry/ui` and use the existing admin
shell navigation.

- `GET /packages`: platform package list with create action, filters, empty
  state, and redaction notice.
- `GET /packages/new` and `POST /packages`: package create form and handler
  for slug, display name, description, steward/owner, lifecycle intent, and
  safe documentation summary.
- `GET /packages/{slug}`: package detail with candidate entry point, published
  versions, grant summaries, audit timeline, safe package metadata, and stale
  conflict banners when redirected after conflicts.
- `GET /packages/{slug}/candidate` and
  `POST /packages/{slug}/candidate`: manifest candidate paste/upload form for
  YAML or JSON, structured parse/schema validation, safe summary, candidate
  revision, parse/schema errors, and inline findings.
- `POST /packages/{slug}/candidate/validate`: validates the current candidate
  through existing validation services and renders blocking, warning, and
  informational findings inline.
- `POST /packages/{slug}/candidate/publish`: publishes an immutable package
  version only when validation has passed and is current; otherwise renders the
  blocked reason and recovery action.
- `GET /packages/{slug}/versions/{version}`: immutable version provenance,
  validation evidence, safe manifest summary, tenant grant summary, smoke-test
  expectations, and redaction-safe export text.
- `GET /packages/{slug}/versions/{version}/grants` and
  `POST /packages/{slug}/versions/{version}/grants`: tenant availability grant
  form supporting one or more selected tenants; removing a grant blocks future
  discovery/install only and does not disable existing pinned installations.
- `GET /available-versions?tenant_id=...`: tenant admin page listing granted
  skill versions with safe summaries, credential requirements, smoke-test
  expectations, compatibility, and install actions.
- `POST /installations`: tenant install action for a granted immutable version,
  redirecting to installation detail with exact package/install version and
  readiness state.
- `GET /installations?tenant_id=...`: tenant-scoped installation list with
  readiness, credential status, smoke-test status, binding eligibility,
  quarantine/withdrawal indicators, and empty state.
- `GET /installations/{installation_id}`: tenant installation detail with exact
  package version, installation version, revision token, readiness findings,
  credential status, smoke-test evidence, binding eligibility panel, and audit.
- `GET /installations/{installation_id}/credentials` and
  `POST /installations/{installation_id}/credentials`: credential reference
  configuration using tenant-authorized picker options and safe delegated
  metadata fields; submits revision token and renders stale conflicts inline.
- `POST /installations/{installation_id}/smoke-tests`: enqueue run/rerun for
  declared smoke tests when policy allows; returns queued/running status page
  with refresh or polling affordance.
- `POST /installations/{installation_id}/eligibility-preview`: binding
  eligibility preview for selected authorized profile or workflow-role context,
  rendering allowed/denied reasons and pinned version evidence.

## Form Models And Validation Handling

- `SkillPackageCreateForm`: slug, display name, description, steward/owner,
  lifecycle intent, safe docs summary, idempotency key.
- `ManifestCandidateForm`: manifest text, optional upload, format, artifact
  digest/reference, approved integration refs, revision token, validation
  reason, idempotency key.
- `TenantGrantForm`: selected tenant ids, grant reason, revision token.
- `InstallSkillForm`: tenant id, slug, semantic version, optional previous
  installation id, idempotency key.
- `CredentialReferenceConfigForm`: revision token plus one row per manifest
  requirement, each backed by allowed picker options or predefined delegated
  metadata fields.
- `SmokeTestActionForm`: revision token, fixture keys, action reason,
  idempotency key.
- `BindingEligibilityPreviewForm`: revision token, selected authorized profile
  or workflow-role context.

Form errors render next to fields, page-level errors render in a shared
`form_errors.html` partial, and service failures map to safe states:
validation failed, publication blocked, denied, not found, stale conflict,
quarantined, withdrawn, smoke-test failed, and empty.

## Authorization And Tenant Scope

- Platform-only routes/actions: package create, candidate validate/publish,
  tenant grant management, package/version withdrawal, package/version
  quarantine, and platform-wide safe summaries.
- Tenant admin routes/actions: available versions for the selected tenant,
  tenant installation, credential configuration, smoke-test run/rerun,
  readiness review, and binding eligibility preview for authorized tenant
  contexts.
- Cross-tenant direct links return not found or absent states with no existence
  hint and safe audit evidence.
- Same-tenant role failures return access denied without raw payloads,
  credential data, or cross-tenant information.
- Platform admins may view cross-tenant grant/install summaries only through
  safe, separated summaries and never raw tenant credential evidence.

## Optimistic Concurrency

Mutable browser forms include the current candidate, grant, installation, or
readiness revision token. Stale submissions are rejected with no state change,
write safe audit evidence, and render an in-browser conflict state with:

- what changed in plain language,
- confirmation that the submitted change was not applied,
- a link/button to reload the latest safe state,
- a retry path that resubmits only after the page carries the latest revision.

## Security Review And Observability

Security review must verify that every browser GET/POST route enforces the
existing Auth0/local-principal role model, tenant scope, CSRF/session protections
where available, safe redirect behavior, no arbitrary credential-reference
entry, and fail-closed handling for cross-tenant direct links.

Observability must reuse existing audit/redaction helpers and emit structured
lifecycle evidence for package creation, candidate submission, validation,
publication, grant changes, installation, credential configuration,
smoke-test enqueue/status, eligibility preview, stale conflict rejection,
authorization denial, and redaction decisions. New browser mutation paths should
preserve request, tenant, actor, route, outcome, and safe error context without
raw manifests, secrets, provider tokens, unsafe fixtures, or cross-tenant data.

## Tests

- Unit: form parsing, YAML/JSON structured parsing errors, page model mapping,
  validation finding grouping, redaction helpers, stale conflict model,
  credential picker option filtering, binding preview display model.
- Integration: full platform browser flow package create -> manifest
  paste/upload -> validate -> blocked publish -> successful publish -> grant;
  full tenant browser flow available versions -> install -> configure
  credentials -> smoke-test enqueue/status -> readiness -> binding preview.
- Authorization: platform-only actions denied to tenant admins; Acme sees
  granted versions/installations; Globex sees empty or not found for Acme-only
  data; same-tenant insufficient role sees denied.
- Concurrency: stale candidate, grant, credential, smoke-test/readiness, and
  binding-preview submissions reject with 409-safe UI and no state change.
- Redaction: rendered pages and screenshot evidence omit raw package payloads,
  raw credential values, provider tokens, unsafe docs, unsafe fixtures, and
  cross-tenant data.
- Docs/QA: `qa014_ui.md` contains no curl, SQL, or direct API command for
  primary feature actions, while retaining terminal commands only for setup,
  server startup, diagnostics, and automated evidence collection.

## Migration And Data Considerations

Prefer reuse of existing services, schemas, repositories, and tables. Add a
database migration only if the current implementation lacks a durable place
for browser manifest candidate revisions, validation run linkage, grant-form
revision tokens, or browser idempotency keys. If a migration is needed, make it
additive and backfill-safe; do not alter published package version or tenant
installation immutability.
