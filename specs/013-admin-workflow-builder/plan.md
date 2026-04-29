# Implementation Plan: Guided Admin Workflow Builder

**Branch**: `013-admin-workflow-builder` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-admin-workflow-builder/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Upgrade the existing admin workflow registry into a guided workflow builder
that lets platform and tenant admins author workflow metadata, roles,
sub-agent roles, prompt/profile references, model routing previews, skill
installation requirements, contracts, graph nodes and edges, join policies,
approval gates, reusable subworkflows, validation findings, draft revisions,
and publish actions without editing raw JSON. The implementation extends the
current workflow registry schemas, services, server-rendered admin templates,
and `workflow_studio` static assets; it adds reference-readiness adapters and a
publish gate service that validate prompts, active agent profiles, provider
catalog/routing readiness, installed skills, subworkflow bundle pins,
contracts, approval gates, graph policy, and required workflow test-suite status
before atomically creating the existing immutable published bundle.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing workflow registry services/schemas/web_admin templates/static workflow_studio assets, prompt library services, agent runtime profile services, model_skill_config resolver and preview APIs, ModelGateway/provider catalog readiness, existing skill binding policy models, audit/redaction helpers, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: PostgreSQL for existing workflow lineages, active drafts, immutable draft revisions, validation results, published bundle metadata, sharing grants, audit records, prompt/profile references, provider catalog metadata, skill policy metadata, and required workflow test-suite result summaries; object/artifact storage for compiled workflow bundles and oversized validation reports
**Testing**: pytest unit tests, pytest-asyncio integration tests, FastAPI/httpx API tests, server-rendered HTML tests, OpenAPI and UI contract tests, docs tests, reviewer QA scripts, Ruff, mypy, and coverage gate at 90 percent for submitted code
**Target Platform**: Linux web service containers plus local macOS/Linux development, served through the existing FastAPI control-plane application and shared admin shell
**Project Type**: Multi-tenant Python web service with server-rendered admin UI, JSON admin APIs, and durable publication workflow
**Performance Goals**: Registry list p95 <= 200 ms for scoped results; editor metadata and lookup payload p95 <= 250 ms; draft save p95 <= 350 ms for a 100-node workflow; graph preview generation p95 <= 150 ms for 100 nodes and 200 edges; validation p95 <= 3 s for static checks and bounded reference lookups; publish gate and publish confirmation return an accepted or clear retryable outcome within 2 minutes
**Constraints**: Use the existing workflow registry and published bundle model; critical create/save/validate/publish actions must work through server-rendered pages; JavaScript is limited to graph editing, inline validation, unsaved-change/conflict feedback, and preview refresh; all saves include `base_revision_number`; stale saves reject with 409 and no new revision; publication pins exact subworkflow bundle versions and prompt/profile evidence; arbitrary graph cycles are blocked except explicit retry or approval-resume loops with configured bounds; no raw secrets, provider tokens, credentials, unsafe prompt previews, or unauthorized tenant content may be stored or rendered; coverage and documentation evidence are mandatory
**Scale/Scope**: Hundreds of workflow lineages per tenant, thousands of published bundles platform-wide, workflow drafts up to 100 nodes, 200 edges, 50 contracts, 25 roles/sub-agent roles, 25 reusable subworkflow references, 50 prompt/profile pins, and low dozens of concurrent admin authoring sessions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Draft saves, validation runs, publish gate decisions, and publication actions persist authoritative state in PostgreSQL and keep artifact writes idempotent. |
| Immutable State And Memory | PASS | Every save creates an immutable draft revision; publish creates an immutable bundle tied to source revision, validation evidence, exact subworkflow bundle versions, and prompt/profile/provider pins. |
| Contract-First Agent Coordination | PASS | Workflow contracts, graph edge semantics, subworkflow compatibility, approval gate resume contracts, prompt/profile references, and publish gate outputs are defined in schemas and contract artifacts. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal authorization, admin shell scope selection, and tenant/platform role checks govern all UI and API routes. |
| Operability Is A Product Requirement | PASS | Validation findings, publish gate outcomes, revision history, blocked publish reasons, safe audit events, metrics, and reviewer QA evidence are planned before implementation. |
| Spec-Driven Delivery | PASS | This plan produces research, data model, API/UI/publish contracts, and quickstart artifacts before tasks and implementation. |
| Test And Documentation Discipline | PASS | Unit, integration, rendered UI, contract, docs, and reviewer QA tests are required with >=90 percent coverage for submitted code plus README and user docs updates. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to workflow registry schemas/services, reference-readiness adapters, publish gate logic, admin UI templates/static assets, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | Lookup options, references, validations, publish scopes, subworkflows, prompts, profiles, provider catalog entries, skills, test evidence, and audit reads all carry explicit scope and fail closed. |
| Version-Pinned Execution | PASS | Publish pins workflow revision, subworkflow bundle versions, prompt/profile versions, model routing evidence, skill policy versions, and contract compatibility evidence into the existing published bundle summary. |
| Secret Hygiene And Controlled Tool Access | PASS | Builder records store references, safe readiness summaries, and policy metadata only; credential readiness is validated through existing policy/secret-reference services without exposing values. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores transactional metadata and compact findings; compiled bundles and oversized validation reports use artifact storage. |
| Human Approval Is Durable State | PASS | Approval gates include approver scope, reason, resume behavior, timeout, and blocked-state visibility so runtime wait-state behavior is explicit and auditable. |

Post-Phase-1 re-check: the research, data model, contracts, and quickstart keep
all constitution gates in `PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/013-admin-workflow-builder/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-builder.openapi.yaml
│   ├── admin-workflow-builder-ui.md
│   └── publish-gate.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── workflow_registry/
│       ├── service.py                    # extend draft/revision/publish flows
│       ├── validation.py                 # extend structural/reference checks
│       ├── compiler.py                   # include builder pins in bundle
│       ├── field_help.py                 # expand metadata-driven field help
│       ├── graph_preview.py              # new graph projection helpers
│       ├── reference_validation.py       # new prompt/profile/provider/skill checks
│       ├── publish_gate.py               # new publish readiness service
│       └── observability.py              # new metrics/logging helpers
├── api/
│   ├── routers/
│   │   ├── admin_workflows.py            # JSON APIs and publish gate routes
│   │   └── admin_workflow_ui.py          # server-rendered builder pages
│   ├── schemas/
│   │   ├── workflow_registry.py          # extend authoring document schemas
│   │   └── workflow_editor.py            # editor metadata/graph/finding schemas
│   └── ui/
│       └── admin_workflows.py            # builder page view models
├── db/
│   ├── models/
│   │   └── workflow_registry.py          # additive metadata only if needed
│   └── repositories/
│       └── workflow_registry.py          # revision/history/gate queries
├── runtime/
│   └── workflow_bundle.py                # bundle summary/pin representation
└── web_admin/
    ├── templates/
    │   └── workflows/
    │       ├── index.html
    │       ├── draft_editor.html
    │       ├── revision_history.html     # new
    │       ├── publish_gate.html         # new or component
    │       ├── version_detail.html
    │       └── components/
    │           ├── graph_preview.html    # new
    │           ├── reference_picker.html # new
    │           └── validation_panel.html
    └── static/
        ├── workflow_studio.js            # progressive graph/form behavior
        └── workflow_studio.css

tests/
├── contract/
│   └── test_workflow_builder_contract.py
├── integration/
│   ├── api/
│   │   ├── test_admin_workflow_builder_api.py
│   │   └── test_admin_workflow_builder_ui.py
│   └── workflows/
│       └── test_workflow_builder_publish_gate.py
├── unit/
│   ├── admin/
│   │   ├── test_workflow_builder_validation.py
│   │   ├── test_workflow_builder_references.py
│   │   ├── test_publish_gate.py
│   │   ├── test_workflow_builder_observability.py
│   │   └── test_graph_preview.py
│   └── api/
│       ├── test_workflow_builder_schemas.py
│       └── test_admin_workflow_builder_ui_models.py
└── docs/
    └── test_workflow_builder_docs.py

docs/
├── admin-workflow-builder.md
├── admin-workflow-builder-testing.md
└── admin-workflow-builder-pr-notes.md
README.md
```

**Structure Decision**: Keep the builder inside the existing FastAPI service
and shared admin shell. The implementation extends current workflow registry
models and services rather than creating a new store or separate frontend. New
code is organized as additive helper modules around graph projection,
reference validation, and publish gating so existing registry CRUD, artifact
storage, authorization, and audit flows remain authoritative.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves the builder architecture around eight design decisions. See
[research.md](./research.md).

Key decisions:

- Extend `WorkflowDraftDocument` and existing draft revision snapshots rather
  than normalizing a second builder store.
- Render the primary UX with admin shell Jinja2 pages and small
  `workflow_studio` JavaScript enhancements for graph editing and inline
  refresh.
- Expose editor metadata, lookup options, graph preview data, and
  field-to-finding mappings through typed Pydantic schemas.
- Run validation through layered structural, reference-readiness,
  graph-policy, test-evidence, and publish-gate checks.
- Reuse prompt/profile, model routing, provider catalog, skill policy,
  subworkflow, and required workflow test-suite systems as authoritative
  reference owners.
- Preserve optimistic concurrency with required `base_revision_number` and
  non-destructive stale-save conflict UX.
- Make publish gate output the only acceptable publish input for the current
  draft revision.
- Record safe audit events for every draft, validation, publish, denial,
  restore, copy, and conflict action.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines the extended builder document,
  editor metadata, graph preview, validation finding mapping, reference
  readiness snapshot, publish gate result, draft revision behavior, and bundle
  pin summaries.
- [contracts/workflow-builder.openapi.yaml](./contracts/workflow-builder.openapi.yaml)
  defines API endpoints for editor metadata, lookup options, graph preview,
  draft save, validation, revision history, copy/restore, publish gate, and
  publish.
- [contracts/admin-workflow-builder-ui.md](./contracts/admin-workflow-builder-ui.md)
  defines pages, sections, graph representation, field-level validation
  mapping, conflict behavior, accessibility, and no-JS fallback requirements.
- [contracts/publish-gate.md](./contracts/publish-gate.md) defines the service
  boundary for reference validation, blocking reasons, idempotency,
  authorization, audit, and atomic publish behavior.
- [quickstart.md](./quickstart.md) defines local-principal reviewer flows,
  blocked publish checks, optimistic concurrency checks, audit checks, and
  automated validation commands.

## UI Pages

- **Registry list** (`/admin/workflows/ui`): existing list page gains create
  workflow action, status/scope filters, validation badges, publish readiness,
  and links to draft editor, revision history, version detail, prompt/profile,
  provider routing previews, and model/skill configuration history only when
  authorized.
- **Create draft** (`/admin/workflows/new` or modal-backed POST from list):
  guided scope, kind, slug, owner, publication intent, and starter template
  controls. The backend still creates a normal `WorkflowDraft` and first
  `WorkflowDraftRevision`.
- **Draft editor** (`/admin/workflows/drafts/{id}/editor`): sectioned forms for
  overview, roles/sub-agent roles, prompt/profile references, skills,
  contracts, graph, joins, approvals, subworkflows, test requirements,
  validation, and publish gate. The raw JSON textarea becomes a read-only
  advanced inspector, not the primary editor.
- **Graph preview**: an unframed workflow map showing canonical node and edge
  projections, validation badges, cycle annotations, retry/approval-resume loop
  bounds, join requirements, terminal outcomes, and selected node detail.
- **Revision history** (`/admin/workflows/drafts/{id}/revisions/ui`): safe
  diff summaries, actor, timestamp, changed sections, validation state,
  restore/copy actions, and conflict-safe restore behavior.
- **Publish gate**: review page or panel that lists all blocking and advisory
  checks, current revision, validation freshness, reference pins, required test
  evidence, and immutable bundle impact before confirming publish.
- **Published version detail**: existing page gains source draft revision,
  prompt/profile pins, provider routing provenance, skill installations,
  subworkflow bundle pins, contract compatibility status, test evidence, and
  safe audit links.

## API Endpoints

The builder keeps existing registry endpoints and adds typed builder support:

- `GET /admin/workflows/editor-metadata`: field help, section order, field
  schemas, validation mapping, graph node/edge type metadata, and action
  capabilities for the current principal and scope.
- `GET /admin/workflows/editor-lookups`: eligible prompt versions, active
  agent profile versions, model routing preview links, tenant-visible provider
  catalog entries, installed skills/skill bindings, published subworkflow
  bundles, contract templates, approval roles, and required workflow test suites.
- `GET /admin/workflows/drafts/{id}/graph-preview`: canonical graph preview
  projection for the latest draft revision.
- `GET /admin/workflows/drafts/{id}/revisions`: revision history and safe
  changed-section summaries.
- `POST /admin/workflows/drafts/{id}/copy`: create an authorized copy from a
  revision or published bundle into a new lineage/draft.
- `POST /admin/workflows/drafts/{id}/restore`: create a new revision from an
  older revision when `base_revision_number` matches the current head.
- `POST /admin/workflows/drafts/{id}/validate`: run structural and reference
  validation for the latest revision and persist findings.
- `POST /admin/workflows/drafts/{id}/publish-gate`: re-check current revision
  readiness, required validation freshness, references, tests, authorization,
  and bundle pins without mutating active published state.
- `POST /admin/workflows/drafts/{id}/publish`: accept a current publish gate id
  or validation result id, re-check freshness, then atomically create and
  activate the immutable bundle.

Existing `GET/POST /admin/workflows`, `GET/PUT /admin/workflows/drafts/{id}`,
and `GET /admin/workflows/versions/{id}` remain backward-compatible.

## Editor Metadata And Graph Preview

Editor metadata is server-owned so templates, tests, and future UI clients use
the same field definitions. Each field metadata entry includes field path,
label, section, control type, allowed values or lookup source, help definition,
requiredness, authorization policy, and validation code mapping. Lookup options
include safe links and readiness badges but never raw secrets, prompt content,
provider responses, or cross-tenant identifiers the actor cannot view.

Graph preview is derived from the draft document and validation results, not
from browser-only state. The projection contains stable node ids, node type,
display label, section path, contract refs, role/profile refs, skill refs,
subworkflow refs, approval refs, status, validation badges, and directed edge
records with edge type, contract, branch condition, failure path, and loop
metadata. The preview intentionally remains a projection; saves still submit
the typed authoring document with optimistic concurrency.

## Field-Level Validation Mapping

Validation findings use canonical builder paths such as:

- `metadata.display_name`
- `roles[planner].profile_reference.agent_profile_version_id`
- `roles[planner].prompt_references[summary_prompt]`
- `roles[planner].skill_installations[doc-extractor]`
- `contracts[inbound].json_schema`
- `graph.nodes[triage].role_key`
- `graph.edges[triage_to_join].contract_key`
- `join_policies[review_join].quorum_count`
- `approval_gates[manager_review].resume_behavior`
- `subworkflow_refs[extract_docs].workflow_version_bundle_id`
- `test_requirements[smoke_suite].latest_result_id`

Each finding includes severity, blocking flag, category, code, message,
remediation, affected section, field path, optional graph element id,
reference type/id, and authorized deep links. The UI anchors findings to the
nearest section and highlights graph elements when `graph_element_id` is
present.

## Reference Validation And Publish Gate

The publish gate service is the authoritative readiness boundary. It verifies:

- **Prompts**: referenced prompt versions exist, are active for new use,
  authorized for the draft scope, digest-compatible with model-skill prompt
  references, and safe to link for the current actor.
- **Agent profiles**: role and sub-agent keys resolve to active profile
  versions using tenant-over-platform precedence; selected profiles validate
  prompt references, memory policy, skills, tools, output contracts, and test
  requirements.
- **Provider routing**: model routing preview resolves through
  `model_skill_config`, selected provider catalog entries are visible, active,
  healthy enough for policy, and ModelGateway-governed.
- **Installed skills and policies**: required skill bindings are active,
  exact-versioned, visible to the tenant/scope, compatible with role context,
  and have required credential readiness through secret-reference metadata.
- **Subworkflows**: reusable references point to visible published subworkflow
  bundle ids, pin exact versions, and satisfy input/output contract
  compatibility.
- **Contracts**: workflow, handoff, artifact, memory, tool, approval, and
  failure contracts are complete and compatibility-checked against previous
  published versions and selected subworkflows.
- **Approval gates**: approver role/scope, reason, resume behavior, timeout,
  blocked-state visibility, and decision contract are present.
- **Graph policy**: disconnected nodes, missing terminals, incompatible edge
  contracts, invalid joins, arbitrary cycles, and unbounded retry or
  approval-resume loops block publication.
- **Required workflow test-suite status**: required workflow/profile test suites
  have a latest result for the current draft revision or compatible profile
  version, are not stale, and have passing status.

Publish refuses stale, missing, or failed gate evidence and leaves the
previously active bundle unchanged.

## Draft Revisions And Optimistic Concurrency

Draft saves remain whole-document immutable revisions. The save request must
include `base_revision_number`; the service compares it with the current draft
head and returns 409 on mismatch without creating a new revision. The UI shows
a conflict banner, preserves the submitted form in browser state when possible,
offers refresh/copy guidance, and links to revision history. Restore and copy
actions also require a current base revision and create new revisions or
lineages rather than mutating old revision records.

## Publication And Failure Recovery

Publication is a single authoritative operation over the current draft
revision. The service re-checks authorization, validation freshness, publish
gate status, required pins, and artifact persistence. It writes the compiled
bundle artifact using a content-addressed key, then creates
`WorkflowVersionBundle`, updates `WorkflowLineage.latest_published_version_id`,
marks the source draft, and records safe audit evidence in one database
transaction. If artifact upload succeeds but the database transaction fails,
the artifact is orphan-safe because no bundle points to it. If a publish
request is retried with the same current revision and gate id, idempotency
prevents duplicate authoritative bundles.

## Authorization And Audit

All builder routes use `require_authorized_principal`, existing tenant scope
resolution, and workflow scope guards. Tenant admins can only view and select
tenant-owned resources and explicitly granted platform resources. Platform
admins can manage platform-scoped drafts and authorized tenant-scoped review
flows according to existing admin policy. Denied view/edit/validate/publish,
hidden lookup options, and forbidden reference selections fail closed.

Audit events are required for draft creation, save, stale-save conflict,
validation request/outcome, publish gate request/outcome, publish attempt,
blocked publish, successful publish, authorization denial, revision restore,
revision copy, and reference lookup denial. Audit payloads include actor,
scope, tenant, lineage, draft, revision, affected sections, outcome, finding
counts, selected pin ids, trace id, and request id. They do not include raw
prompts, rendered previews, secrets, credentials, provider responses, or
unauthorized content.

## Observability And Operational Debugging

Builder routes and services emit structured logs with trace id, request id,
actor id, scope, tenant id when applicable, workflow lineage id, draft id,
revision id, action, outcome, failure code, and redacted finding counts. Metrics
cover editor metadata, lookups, graph preview, draft save, validation, publish
gate, publish, stale-save conflicts, authorization denials, blocked publish
categories, artifact upload failures, and publish latency.

Operator debugging surfaces are the revision history, validation history,
publish gate result, published version detail, and safe audit records.
Replay/debug review uses persisted draft revisions, validation results, publish
gate digests, bundle pin summaries, and audit events without raw prompts,
secrets, provider payloads, or unauthorized tenant data.

Builder lookup, validation, graph preview, and publish gate endpoints use
existing tenant-scoped authorization plus bounded request sizes. They reuse the
platform reliability admission/backpressure helpers when available for the route;
if those helpers are not available, the builder applies local per-tenant
in-flight limits, maximum graph/document sizes, and deterministic 429/413
responses before starting validation or publish gate work. Rejection and
backpressure outcomes include tenant/scope tags in metrics so noisy-neighbor
behavior can be detected.

## Test Strategy

- **Unit tests**: schema validation, field path mapping, graph cycle policy,
  join/approval rules, reference readiness adapters, publish gate outcomes,
  compiler pin summaries, optimistic concurrency, authorization helper use,
  redaction, structured telemetry, tenant fairness guards, and metrics.
- **Integration tests**: end-to-end create/save/validate/publish gate/publish
  flows, stale save rejection, blocked publish preserving active bundle,
  prompt/profile/provider/skill/subworkflow/test failures, tenant isolation,
  tenant concurrency/backpressure behavior, audit records, artifact failure
  compensation, and revision restore/copy.
- **Server-rendered UI tests**: registry, create draft, editor sections, graph
  preview, field help, validation anchors, publish gate, conflict banner,
  revision history, version detail pins, disabled states, and no-JS fallbacks.
- **Contract tests**: OpenAPI request/response shapes, UI view-model contract,
  publish gate service contract, validation finding mapping, and backward
  compatibility for existing workflow registry endpoints.
- **Backward compatibility tests**: pre-builder draft and published bundle
  fixtures prove existing registry entries retain lineage, version detail, and
  publication behavior after guided builder fields are introduced.
- **Docs tests**: README, user guide, testing guide, and PR notes presence plus
  links to quickstart commands.
- **Reviewer QA**: local-principal walkthrough proving valid publish,
  blocked publish categories, conflict handling, tenant/platform isolation,
  safe audit evidence, timed authoring under 25 minutes, blocked-reason
  identification under 2 minutes, scoped endpoint p95 checks, publish outcome
  within 2 minutes, and coverage >=90 percent.
