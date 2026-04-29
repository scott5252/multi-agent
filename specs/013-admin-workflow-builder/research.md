# Research: Guided Admin Workflow Builder

## Decision 1: Extend the existing workflow registry store

- **Decision**: Represent builder output as an extended
  `WorkflowDraftDocument` persisted in the existing immutable
  `WorkflowDraftRevision.authoring_document_json` snapshots. Keep
  `WorkflowLineage`, `WorkflowDraft`, `ValidationResult`, and
  `WorkflowVersionBundle` as the authoritative store.
- **Rationale**: The feature explicitly requires extending existing registry
  lineage and bundle behavior. Whole-document revision snapshots already give
  durable history, optimistic concurrency, validation boundaries, and publish
  provenance without a second data model.
- **Alternatives considered**:
  - A new workflow builder table family: rejected because it would duplicate
    registry state and complicate publication lineage.
  - Browser-only builder state that compiles to the current document on save:
    rejected because conflict handling, validation, audit, and restore require
    server-owned durable snapshots.

## Decision 2: Use server-rendered admin pages with small graph enhancements

- **Decision**: Build the UX in the existing admin shell with Jinja2 templates,
  typed view models, and progressive `workflow_studio.js` behavior for graph
  manipulation, inline validation refresh, and unsaved-change/conflict states.
- **Rationale**: Current admin workflows, prompt/profile pages, and model
  provider pages are server-rendered. Staying in that pattern preserves
  authorization, saved filters, breadcrumbs, local-principal QA, and deployment
  simplicity while still enabling a richer graph editor.
- **Alternatives considered**:
  - A standalone SPA: rejected because it adds a frontend build/deploy surface
    before the backend authoring contracts settle.
  - Read-only server pages plus raw JSON editing: rejected because the feature
    requires non-developers to author without editing JSON.

## Decision 3: Make editor metadata server-owned

- **Decision**: Expand `WorkflowEditorMetadataResponse` to include sections,
  field definitions, lookup sources, graph element types, validation code
  mapping, help definitions, authorization capabilities, and action URLs.
- **Rationale**: The same metadata can drive templates, JavaScript behavior,
  server-rendered field labels, tests, and future clients. It also prevents
  drift between validation paths and UI anchors.
- **Alternatives considered**:
  - Hardcode labels and field paths in templates and JavaScript: rejected
    because validation mapping would drift.
  - Generate metadata only from Pydantic introspection: rejected because builder
    fields need UX labels, lookup sources, help text, and authorization notes
    that are not expressible through type annotations alone.

## Decision 4: Derive graph preview from the saved draft document

- **Decision**: Store the authoring graph as typed nodes, edges, joins,
  approvals, and subworkflow references inside the draft document, then derive
  a `GraphPreview` projection for rendering and validation highlighting.
- **Rationale**: The graph view should never become the only source of truth.
  A server-derived projection makes graph rendering, static validation, review,
  and publish compiler behavior consistent.
- **Alternatives considered**:
  - Persist canvas coordinates and graph library output as authoritative state:
    rejected because visual layout is not runtime semantics.
  - Generate the graph entirely client-side after loading raw JSON: rejected
    because server-rendered UI tests and no-JS review states need the same
    projection.

## Decision 5: Use canonical field paths for validation mapping

- **Decision**: Validation findings include canonical builder field paths,
  affected section ids, optional graph element ids, reference type/id, severity,
  blocking flag, code, message, remediation, and authorized links.
- **Rationale**: The builder must tie errors to form sections and graph nodes.
  Canonical paths let API, UI, audit, contract tests, and documentation agree
  on where a finding belongs.
- **Alternatives considered**:
  - Free-form validation messages only: rejected because admins could not find
    the affected field quickly and tests could not assert stable locations.
  - UI-only mapping tables: rejected because API clients and audits also need
    stable locations.

## Decision 6: Centralize readiness in a publish gate service

- **Decision**: Add a publish gate service that reuses validation output but
  independently checks current revision freshness, authorization, prompt/profile
  readiness, provider routing readiness, skill readiness, subworkflow pins,
  contract compatibility, approval gate completeness, graph policy, and
  required test evidence immediately before publish.
- **Rationale**: Publication is the irreversible boundary where drafts become
  runtime-ready immutable bundles. A single service gives API routes, UI pages,
  and tests one readiness contract and prevents stale validation from being
  treated as publish authority.
- **Alternatives considered**:
  - Let `publish_draft` check only latest validation status: rejected because
    references can become retired, unauthorized, unhealthy, or stale after
    validation.
  - Put readiness checks entirely in the UI: rejected because API clients and
    retries must enforce the same gate.

## Decision 7: Treat external references as authoritative in their home systems

- **Decision**: The builder stores references and readiness snapshots, while
  prompt library, agent profiles, model-skill routing, provider catalog,
  installed skills/policies, subworkflow bundles, contracts, approval roles,
  and future test bench results remain the owners of availability and policy.
- **Rationale**: This avoids duplicating lifecycle state and keeps tenant
  authorization decisions in existing services. Builder validation becomes an
  orchestration layer over safe, scoped reference checks.
- **Alternatives considered**:
  - Copy full prompt/profile/provider/skill records into the workflow draft:
    rejected because it risks stale or secret-bearing data.
  - Validate only ids exist: rejected because publish readiness depends on
    lifecycle status, scope grants, health, credentials, policy, and tests.

## Decision 8: Preserve whole-document optimistic concurrency

- **Decision**: Save, restore, and copy-from-revision operations require the
  current `base_revision_number`; stale requests return 409 and create no new
  revision.
- **Rationale**: Whole-document builder forms and graph edits are easiest to
  reason about when each save creates one immutable snapshot. Rejecting stale
  saves prevents hidden overwrites across concurrent admin sessions.
- **Alternatives considered**:
  - Last-writer-wins saves: rejected because graph and reference edits could
    silently remove another admin's work.
  - Long edit locks: rejected because they add operational friction and are not
    necessary for low-concurrency admin authoring.

## Decision 9: Allow only bounded semantic graph cycles

- **Decision**: Graph validation blocks arbitrary cycles and permits only
  explicit retry loops or approval-resume loops when loop type, maximum
  attempts or timeout, failure exit, and audit/resume semantics are configured.
- **Rationale**: The runtime may eventually support bounded loops, but
  unbounded cycles are unsafe for durable execution and reviewer reasoning.
- **Alternatives considered**:
  - Full acyclic graph policy: rejected because the clarified spec allows
    retry and approval-resume loops.
  - Arbitrary cycles with runtime safeguards only: rejected because publish
    should catch unsafe graph semantics before execution.

## Decision 10: Make required test bench status a reference readiness check

- **Decision**: Model future workflow/profile test bench status as a
  readiness source with required suite id, target revision/profile, latest
  result id, status, executed_at, staleness policy, and safe summary. Until the
  full workflow test bench exists, the contract supports missing-result
  blocking findings and profile test bench evidence from existing profile
  services.
- **Rationale**: The spec requires publication to block on missing, failing, or
  stale required tests, while the repository currently has profile test bench
  plumbing rather than a full workflow test bench product. A contract-first
  readiness adapter keeps the builder future-proof without inventing execution
  semantics in the UI.
- **Alternatives considered**:
  - Omit test evidence until the future test bench is implemented: rejected by
    the feature requirements.
  - Create a full workflow test bench in this feature: rejected as scope creep;
    the builder should consume test status, not own test execution.

## Decision 11: Persist safe audit evidence for every critical action

- **Decision**: Record safe audit events for create, save, conflict, validate,
  publish gate, publish attempt, blocked publish, successful publish,
  authorization denial, restore, copy, and hidden reference denial.
- **Rationale**: Workflow governance depends on knowing who changed what,
  which revision was evaluated, which references blocked publication, and
  which immutable bundle became active, without exposing sensitive content.
- **Alternatives considered**:
  - Audit only successful publication: rejected because blocked attempts and
    denied actions are important governance signals.
  - Store raw documents in audit payloads: rejected because documents may carry
    unsafe references or cross-tenant identifiers; revisions already preserve
    source content under normal access controls.
