# Implementation Plan: Admin Workflow Studio And Registry

**Branch**: `003-workflow-studio-registry` | **Date**: 2026-04-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-workflow-studio-registry/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add an admin-only workflow registry to the FastAPI platform that lets tenant
admins and platform admins author workflow drafts, validate nested agent and
subworkflow designs, and publish immutable workflow version bundles for later
runtime use. The design uses Pydantic-first authoring documents, PostgreSQL
metadata for drafts and lineage, compiled published bundle artifacts for
runtime-ready metadata, and a FastAPI-served admin Web UI whose forms expose
field-level help through icon-triggered pop-up modals next to every editable
input.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x, Alembic, PostgreSQL 16+, psycopg 3, Jinja2 templates for the embedded
admin Web UI, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: PostgreSQL for workflow lineages, active drafts, immutable draft
revisions, validation results, registry metadata, sharing grants, and audit
events; existing artifact/storage providers for compiled published bundle JSON
and any oversized validation reports; existing skill catalog and versioning
metadata are consumed by reference only  
**Testing**: pytest unit tests for schemas, validation, compiler, repository,
and UI metadata; FastAPI integration tests for JSON APIs and HTML UI routes;
OpenAPI contract validation; coverage enforcement at >=90 percent for relevant
workflow-registry code  
**Target Platform**: Linux container deployment target for the FastAPI API and
embedded admin Web UI; local development on macOS/Linux; authenticated admin
traffic served through the same FastAPI application as the control-plane APIs  
**Project Type**: Multi-tenant backend platform with embedded admin Web UI and
JSON admin APIs  
**Performance Goals**: Draft load/list p95 <200ms; draft save p95 <250ms for a
50-node workflow document; validation p95 <2s for a workflow with 100 nodes, 30
contracts, and 10 subworkflow references; publish p95 <5s including compile and
artifact write; registry detail retrieval p95 <300ms  
**Constraints**: Admin-only access; single active editable draft per workflow
lineage; optimistic concurrency on every save and publish; platform-scoped
assets are reusable cross-tenant only through explicit sharing grants; exact
skill, contract, and subworkflow version pinning on publish; field-help icon
buttons and pop-up modal guidance next to every editable input; no workflow
execution or run creation in this feature; >=90 percent unit-test coverage and
README update required  
**Scale/Scope**: Initial scope supports hundreds of workflow lineages per
tenant, thousands of published versions platform-wide, up to 100 authored nodes
or roles per workflow, up to 20 concurrent admin authoring sessions, and low
dozens of publish events per day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Draft revisions, validation results, registry records, sharing grants, and published bundle metadata are persisted in PostgreSQL before they are treated as authoritative. |
| Immutable State And Memory | PASS | Mutable authoring lives only in the active draft head; every save creates an immutable revision snapshot and every publish creates an immutable version bundle plus digest. |
| Contract-First Agent Coordination | PASS | Contracts are modeled as Pydantic-first schemas with JSON Schema export, explicit compatibility checks, and publish-time exact pinning into the compiled bundle. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0 and local-principal admin auth flows gate every API and UI route; tenant scope and platform-scope sharing rules fail closed and remain auditable. |
| Operability Is A Product Requirement | PASS | The plan adds structured save/validate/publish events, validation timing metrics, bundle compilation traces, registry lineage visibility, and UI-oriented operator guidance. |
| Spec-Driven Delivery | PASS | The clarified spec, research, data model, quickstart, API contract, and UI contract are all produced before task generation. |
| Test And Documentation Discipline | PASS | The plan includes >=90 percent unit coverage for new code, contract tests, manual UI verification, README changes, quickstart updates, and PR evidence requirements. |
| Clear Ownership And Small Safe Changes | PASS | The work is split across admin services, API schemas and routers, DB models and repositories, runtime bundle helpers, Web UI templates, and targeted tests so later tasks stay reviewable. |
| Tenant Isolation And Fair Scheduling | PASS | Every draft, version, validation result, and sharing grant carries explicit scope metadata; platform-scoped reuse is governed by explicit grants; registry endpoints remain scope-aware. |
| Version-Pinned Execution | PASS | Publish compiles exact workflow, subworkflow, contract, and skill versions and resolves skill-linked runtime refs so later run bundles are deterministic and pinned from the start. |
| Secret Hygiene And Controlled Tool Access | PASS | Drafts and bundles store only skill/version/tool-policy references and never secret material; delegated credentials remain out of scope and no new secret path is introduced. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores transactional metadata and draft snapshots; canonical compiled bundle JSON and oversized reports are stored through the artifact provider with PostgreSQL metadata anchors. |
| Human Approval Is Durable State | PASS | Approval gates are modeled as durable design-time schema now, and the compiled bundle carries the metadata the future runtime will need for persisted wait states without inventing transient paths. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/003-workflow-studio-registry/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-registry.openapi.yaml
│   └── admin-workflow-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── multi_agent_platform/
    ├── admin/
    │   ├── service.py
    │   └── workflow_registry/
    │       ├── service.py                    # new
    │       ├── validation.py                 # new
    │       ├── compiler.py                   # new
    │       ├── sharing.py                    # new
    │       └── field_help.py                 # new
    ├── api/
    │   ├── main.py
    │   ├── routers/
    │   │   ├── admin_access.py
    │   │   ├── admin_workflows.py            # new JSON admin API
    │   │   └── admin_workflow_ui.py          # new HTML admin pages
    │   ├── schemas/
    │   │   ├── auth.py
    │   │   ├── workflow_registry.py          # new
    │   │   └── workflow_editor.py            # new
    │   └── ui/
    │       └── admin_workflows.py            # new view-model assembly
    ├── bootstrap/
    │   └── container.py
    ├── db/
    │   ├── models/
    │   │   ├── access_control.py
    │   │   └── workflow_registry.py          # new
    │   ├── repositories/
    │   │   ├── access_control.py
    │   │   └── workflow_registry.py          # new
    │   └── session.py
    ├── runtime/
    │   ├── versioning.py
    │   └── workflow_bundle.py                # new
    ├── tenancy/
    │   ├── context.py
    │   ├── guards.py
    │   └── middleware.py
    └── web_admin/
        ├── templates/
        │   └── workflows/
        │       ├── index.html                # new
        │       ├── draft_editor.html         # new
        │       ├── version_detail.html       # new
        │       └── components/
        │           ├── field_help_modal.html # new
        │           └── validation_panel.html # new
        └── static/
            ├── workflow_studio.js            # new
            └── workflow_studio.css           # new
alembic/versions/
tests/
├── contract/
│   └── test_workflow_registry_contract.py    # new
├── integration/
│   ├── api/
│   │   ├── test_admin_workflows_api.py       # new
│   │   └── test_admin_workflow_ui.py         # new
│   └── admin/
│       └── test_publish_compilation.py       # new
├── unit/
│   ├── admin/
│   │   ├── test_workflow_registry_service.py # new
│   │   ├── test_validation.py                # new
│   │   ├── test_compiler.py                  # new
│   │   └── test_field_help.py                # new
│   ├── api/
│   │   ├── test_workflow_registry_schemas.py # new
│   │   └── test_admin_workflow_ui_models.py  # new
│   └── db/
│       └── test_workflow_registry_models.py  # new
README.md
docs/quickstart.md
docs/admin-workflow-studio.md             # new
```

**Structure Decision**: Keep the workflow registry inside the existing Python
distribution and FastAPI application so the new admin JSON APIs, rendered Web
UI, authorization checks, audit flow, and future runtime bundle handoff all use
the same container, tenancy, and settings model. The Web UI is implemented as
FastAPI-served admin pages plus a small static JavaScript layer rather than a
new standalone frontend stack, which reduces repo-wide tooling churn while still
supporting an intuitive guided authoring experience and field-help modals.

## Failure Recovery And Durability Decisions

- **Checkpoint Boundaries**: Every draft save writes a new immutable draft
  revision plus updates the active draft head in one PostgreSQL transaction.
  Validation results are written against a specific draft revision and are
  superseded when a newer revision or revalidation occurs. Publish writes the
  compiled bundle artifact first using a content-addressed key, then records the
  immutable workflow version bundle, registry metadata, and dependency digest in
  a single PostgreSQL transaction.
- **Retry Strategy**: Draft saves do not auto-retry stale revision conflicts;
  the UI must refresh and reapply. Validation requests are idempotent per draft
  revision and may be retried safely. Publish retries are keyed by draft,
  revision, validation result, and target lineage so duplicate publish requests
  do not create multiple versions.
- **Compensation Strategy**: If artifact upload succeeds but the database
  publish transaction fails, the content-addressed artifact remains orphan-safe
  and can be reclaimed by later cleanup because no registry record points to it.
  If a publish transaction succeeds but post-commit notifications fail, the
  bundle remains authoritative and observability should surface the notification
  failure without mutating the published bundle.
- **Idempotency Strategy**: Draft saves use `base_revision_number` optimistic
  concurrency guards. Validation uses `workflow_draft_revision_id` as the stable
  deduplication boundary. Publish uses a deterministic idempotency key derived
  from `workflow_draft_id`, `workflow_draft_revision_id`, and
  `validation_result_id`.

## Tenant Isolation And Fair Use Decisions

- **Tenant Context Propagation**: Tenant and platform scope continue to flow
  from the existing authenticated `ScopeContext`. Every workflow lineage, draft,
  validation result, published bundle, and sharing grant stores `scope_type` and
  `tenant_id` when applicable.
- **Isolation Controls**: Tenant-scoped drafts and versions are only visible to
  the owning tenant’s admins. Platform-scoped assets are not discoverable to
  tenants by default; explicit sharing grants control visibility and reference
  eligibility. Publish, validate, and registry-detail endpoints all recheck
  scope ownership even when a draft or version identifier is known.
- **Quota And Fairness Controls**: The feature does not introduce runtime worker
  scheduling, but it records tenant ownership on every validation and publish
  event so future admin quotas can be added without reshaping schemas. Metrics
  should track validation and publish volume per tenant to surface noisy-admin
  behavior if it appears.

## Subworkflow And Parent-Child Lineage Decisions

- **Subworkflow Boundaries**: A `subworkflow_ref` always targets an exact
  published workflow version bundle, never a draft. Parent workflows treat
  subworkflows as immutable reusable dependencies with explicit input and output
  contract bindings.
- **Parent-Child Run Model**: Execution is out of scope, but the compiled bundle
  must record enough dependency metadata for the future runtime to create
  parent-child lineage records: `root_workflow_version_id`,
  `parent_node_key`, `subworkflow_version_id`, and join-policy semantics for the
  subworkflow boundary.
- **Replay And Debug Visibility**: Registry detail views and operator queries
  must be able to show a published version’s predecessor, successor, source
  draft revision, and exact subworkflow dependency chain so later runtime issues
  can be traced back to the authored design.

## Version Bundle And Contract Decisions

- **Pinned Bundle Contents**: Every published bundle stores the exact workflow
  lineage and version sequence, source draft revision digest, exact contract
  schema digests, exact subworkflow version ids, exact skill version ids,
  resolved prompt-template/model-config/tool-policy refs from the skill catalog,
  join-policy definitions, approval-gate definitions, compiler version, and
  bundle SHA-256 digest.
- **Resume Policy**: This feature does not resume live workflow runs, but it
  prepares a `RunVersionBundle` blueprint so the future runtime can clone the
  published bundle into a per-run pinned record without additional mutable
  lookups. New publishes affect only new run creations once execution exists.
- **Contract Compatibility Plan**: Draft contracts are authored as named
  Pydantic models with exported JSON Schema and semantic version labels. The
  validator treats optional additive fields and documentation-only changes as
  backward-compatible, but rejects type changes, field removals, optional-to-
  required changes, enum narrowing, or changed approval decision payloads as
  breaking. Published bundles pin exact contract digests even when a compatible
  successor exists.

## Secret Management And Tool Policy Decisions

- **Secret Manager Integration**: Workflow drafts and compiled bundles do not
  store secrets or delegated credentials. Skill bindings and future tool use are
  represented only by approved skill version ids and resolved tool-policy refs.
- **Delegated Credential Handling**: User-linked delegated credentials remain a
  runtime concern and are not authorable in this feature. Approval gates and
  skill bindings may reference required credential classes in help text or
  validation rules, but not specific secret references.
- **Tool Access Policy**: Publish-time compilation must resolve the tool-policy
  refs attached to the exact skill versions referenced in the bundle so future
  runtime enforcement can stay pinned and auditable.

## Artifact Storage Decisions

- **Transactional Metadata**: PostgreSQL stores workflow lineage metadata,
  active draft heads, immutable revision snapshots, validation status, publish
  status, sharing grants, dependency digests, and audit correlations.
- **Blob Storage**: The canonical compiled bundle JSON is stored through the
  existing artifact provider and referenced from PostgreSQL metadata. Oversized
  validation reports may also be stored as artifacts while keeping summarized
  blocking and advisory findings in PostgreSQL JSONB.
- **Retention And Access**: Published compiled bundle artifacts use an
  audit-grade retention class and are never mutated in place. Draft snapshots
  remain transactional PostgreSQL data because they are frequently loaded,
  replaced, and validated during authoring.

## Approval And Resume Decisions

- **Approval Triggers**: Approval gates are authored as explicit workflow nodes
  and validated for approver scope, decision schema, and outgoing transitions,
  but they do not create live approval requests in this feature.
- **Persisted Wait State**: No runtime wait state is introduced yet. The
  published compiled bundle carries approval metadata that the future execution
  feature will map into persisted `waiting_for_input` records.
- **Audit Trail**: Authoring and publishing approval-gate definitions create
  audit events, including gate ids, approver scope, and schema digests, so later
  runtime incidents can trace back to the published design.

## Observability Requirements

- **Logs**: Structured events for draft creation, save conflict, validation
  start and finish, publish attempt, publish success or failure, sharing-grant
  change, and field-help metadata resolution. Logs include `trace_id`,
  `request_id`, `tenant_id`, `scope_type`, `workflow_lineage_id`, `draft_id`,
  and `workflow_version_bundle_id` when available.
- **Metrics**: Counters and histograms for draft saves, stale save rejections,
  validation duration, validation blocking-issue count, publish duration,
  publish failures by reason, bundle artifact bytes, and sharing-grant creation
  or revocation.
- **Traces**: FastAPI request traces should include DB access, validation
  pipeline spans, bundle compilation spans, and artifact-provider spans so slow
  validation or publish paths are visible.
- **Timeline And Replay**: Registry detail surfaces must show a draft’s revision
  history, validation history, and published lineage chain. Later runtime
  tooling can join that lineage to run-level timelines using the pinned bundle
  ids.
- **Operational Runbooks**: Add an admin workflow studio runbook that explains
  stale save conflicts, failed validation diagnostics, publish artifact
  mismatches, and sharing-grant troubleshooting.

## Test Strategy

- **Unit Tests**: Cover nested Pydantic authoring schemas, contract version
  compatibility checks, graph validation, join-policy validation, approval-gate
  validation, optimistic concurrency enforcement, publish compiler output,
  bundle digest generation, sharing-grant policy, and field-help metadata
  generation. Maintain >=90 percent unit coverage for the workflow registry code
  paths.
- **Integration And Contract Tests**: Validate JSON API routes for draft CRUD,
  validation, publish, sharing grants, registry listing, and editor metadata.
  Validate the OpenAPI contract and server-rendered UI routes for admin access,
  editor rendering, validation summary display, and field-help modal markup.
- **Failure And Recovery Tests**: Exercise stale save rejection, publish with a
  superseded validation result, contract-breaking changes against a pinned
  subworkflow reference, sharing-grant revocation, orphan-safe artifact upload
  handling, and unauthorized cross-tenant access attempts.
- **Operational Validation**: Run the quickstart flow in local-principal mode to
  create a draft, open field-help modals, validate, publish, and inspect the
  compiled bundle metadata. Capture metrics/log evidence for one publish path
  and one failed validation path.

## Documentation Tasks

- **README.md Updates**: Document the workflow studio lifecycle, single-active-
  draft rule, optimistic concurrency behavior, publish immutability, sharing
  grants for platform-scoped assets, and how to run the admin workflow
  quickstart.
- **Quickstart Updates**: Add a feature quickstart for local-principal admin
  access, draft authoring, validation, publishing, and UI field-help modal
  verification.
- **Feature Docs**: Add `docs/admin-workflow-studio.md` covering authoring
  sections, validation rule categories, compatibility rules, bundle compilation,
  and UI behavior for help modals next to each input.
- **PR Evidence Requirements**: Require coverage summaries, contract-test
  results, one successful publish trace/log excerpt, screenshots of the draft
  editor and field-help modal behavior, and manual validation notes for stale
  save conflicts.

## Security Review Notes

- **Auth/Authz Impact**: All JSON API and HTML UI routes inherit the existing
  admin authorization model. Platform-admin-only sharing and publish controls
  must be verified separately from tenant-admin draft editing rights.
- **Tenant/Security Boundaries**: Cross-tenant reuse of platform-scoped assets
  is allowed only through explicit sharing grants. Tenant-scoped assets must
  never leak through registry listing, detail, or editor lookup endpoints.
- **Secret/Tool Risk Review**: Skill bindings may expose resolved tool-policy
  references in published bundles, but no secret values or delegated credential
  identifiers may be stored in authoring documents or UI payloads.
- **Additional Review Needed**: Review HTML escaping and help-modal rendering to
  prevent stored XSS from workflow descriptions, contract examples, or help
  content; review publish digest logic to ensure bundle tampering is detectable.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution exceptions are required for this feature.
