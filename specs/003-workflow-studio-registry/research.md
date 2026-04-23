# Research: Admin Workflow Studio And Registry

## Decision 1: Use a Pydantic-first workflow document as the canonical authoring schema

- **Decision**: Represent each draft revision as a canonical
  `WorkflowDraftDocument` Pydantic model with nested role, contract,
  subworkflow, join-policy, and approval-gate models. Persist the immutable
  serialized document for each revision rather than maintaining a large set of
  mutable child tables for every authored element.
- **Rationale**: The feature needs flexible authoring for graph topology,
  contracts, and nested workflow parts without constant relational schema churn.
  Pydantic-first documents give the API, validation layer, UI view-models, and
  compiler one shared source of truth, while PostgreSQL still holds durable
  revision snapshots and queryable summary metadata.
- **Alternatives considered**:
  - Fully normalize every authored role, edge, contract, join, and approval row
    in PostgreSQL: rejected because the authoring model will evolve faster than
    the first storage schema and this would create brittle early migrations.
  - Store only opaque JSON with no typed schema model: rejected because it would
    weaken validation, UI metadata generation, and contract testing.
- **Sources**:
  - [Feature spec](./spec.md)
  - [Architecture guidance on workflow definitions](../../docs/architecture.md)

## Decision 2: Save drafts as whole-document immutable revisions with optimistic concurrency

- **Decision**: Every save replaces the active draft head by creating a new
  immutable draft revision from the full authoring document and advancing the
  head only when `base_revision_number` matches the current draft revision.
- **Rationale**: Whole-document saves are easy to diff, validate, and audit,
  align with the single-active-draft clarification, and keep optimistic
  concurrency straightforward for both API clients and the embedded Web UI.
- **Alternatives considered**:
  - Per-section patch endpoints: rejected because they complicate validation and
    make it easier to publish a draft assembled from partially incompatible
    section updates.
  - Exclusive edit locks: rejected because they add operational friction and are
    unnecessary for the low-concurrency admin authoring flow.
- **Sources**:
  - [Clarified spec](./spec.md)

## Decision 3: Publish-time compilation should create an immutable compiled bundle artifact

- **Decision**: On publish, compile the validated draft revision into a
  `CompiledWorkflowBundle` JSON artifact and store immutable PostgreSQL metadata
  that points to the artifact, bundle digest, dependency manifest, and source
  revision.
- **Rationale**: The architecture expects a compiler boundary between admin
  authoring and runtime execution. Compiling at publish time catches structural
  and dependency issues early, gives operators a deterministic artifact to
  inspect, and avoids mutable late binding when runtime work arrives later.
- **Alternatives considered**:
  - Compile only when a run starts: rejected because broken definitions would
    reach runtime too late and operator debugging would lose the publish-time
    checkpoint.
  - Store the full compiled bundle only in PostgreSQL: rejected because bundle
    payloads can grow and the constitution prefers artifact storage for larger
    immutable blobs.
- **Sources**:
  - [Architecture compiler guidance](../../docs/architecture.md)
  - [Constitution](../../.specify/memory/constitution.md)

## Decision 4: Resolve exact skill versions into runtime refs during publish

- **Decision**: Skill bindings remain authoring-time references to exact skill
  versions, and publish-time compilation resolves each skill version into the
  prompt-template, model-configuration, and tool-policy refs that the future
  runtime will need for pinned run bundles.
- **Rationale**: The spec already requires exact skill-version pinning. By
  resolving the runtime refs while publishing, the system honors the
  constitution’s version-pinned execution rule without making the future runtime
  perform mutable catalog lookups before every run.
- **Alternatives considered**:
  - Store only skill version ids and let runtime resolve the rest later:
    rejected because future skill catalog changes could otherwise alter run
    behavior after publish.
  - Allow floating skill references in the published bundle: rejected by the
    clarified spec and immutability requirements.
- **Sources**:
  - [Clarified spec](./spec.md)
  - [Architecture version-bundle guidance](../../docs/architecture.md)

## Decision 5: Manage communication contracts as typed schemas with compatibility evaluation

- **Decision**: Contracts are authored as named Pydantic models with exported
  JSON Schema, semantic version labels, examples, and role/subworkflow bindings.
  Validation compares current contract versions against the last published
  bundle’s matching contract keys to label changes as compatible or breaking.
- **Rationale**: This keeps contracts explicit, testable, and versionable while
  avoiding a separate contract product in the first slice. Contract compatibility
  directly affects subworkflow reuse and publish safety, so it must be part of
  validation rather than a documentation-only concern.
- **Alternatives considered**:
  - Accept free-form JSON payload examples as contracts: rejected because they
    would not reliably support publish-time compatibility or API/UI guidance.
  - Build a fully separate contract registry before workflow authoring:
    rejected because it expands scope beyond the first authoring/storage slice.
- **Sources**:
  - [Feature spec](./spec.md)
  - [Architecture contract-validation guidance](../../docs/architecture.md)

## Decision 6: Use a staged validation pipeline instead of a single pass/fail check

- **Decision**: Validation runs in three stages: structural validation
  (topology, required fields, single active draft assumptions), compatibility
  validation (contracts, subworkflow I/O, skill version/runtime refs, sharing
  grants), and publish-readiness validation (exact pins, compiler success,
  immutable bundle eligibility).
- **Rationale**: Admins need actionable feedback rather than one opaque failure.
  A staged pipeline lets the UI show blocking versus advisory findings and keeps
  later publish behavior deterministic.
- **Alternatives considered**:
  - Validate only on publish: rejected because it makes authoring frustrating
    and delays critical feedback until the last step.
  - Validate only with schema-level checks: rejected because compatibility and
    bundle resolution need deeper semantic rules.
- **Sources**:
  - [Feature spec](./spec.md)

## Decision 7: Serve the first admin Web UI from FastAPI with template-backed pages and metadata-driven help modals

- **Decision**: Implement the initial admin studio as FastAPI-served HTML pages
  backed by JSON admin APIs, a small static JavaScript layer, and an
  `editor-metadata` response that contains field-level help definitions for the
  icon-triggered pop-up modals next to each input.
- **Rationale**: The repo is currently Python-first and does not yet contain a
  standalone frontend toolchain. Server-rendered admin pages plus targeted
  enhancement keep the initial blast radius low while still delivering the
  guided authoring experience the feature requires.
- **Alternatives considered**:
  - Introduce a separate SPA immediately: rejected for this first slice because
    it would add a second build system and deployment surface before the backend
    contracts and authoring rules settle.
  - Hardcode field instructions directly into template text: rejected because
    every editable field needs consistent modal help and the same metadata should
    be reusable in tests and future UI iterations.
- **Sources**:
  - [Feature spec](./spec.md)
  - [Architecture Web UI guidance](../../docs/architecture.md)

## Decision 8: Use explicit sharing grants for cross-tenant access to platform-scoped assets

- **Decision**: Platform-scoped published workflow versions become reusable to
  tenant admins only when a `RegistrySharingGrant` explicitly authorizes that
  tenant to discover and reference the asset.
- **Rationale**: The clarified spec requires dual scope without turning the
  platform registry into a default cross-tenant catalog. Explicit sharing grants
  make the policy auditable and reversible.
- **Alternatives considered**:
  - Make all platform-scoped assets globally visible: rejected because it
    expands blast radius and weakens tenant isolation.
  - Copy platform assets into tenant scope on every reuse: rejected because it
    undermines immutable lineage and exact version references.
- **Sources**:
  - [Clarified spec](./spec.md)

## Decision 9: Keep draft snapshots transactional in PostgreSQL and move compiled bundles to artifact storage

- **Decision**: Store active draft heads, immutable revision snapshots, and
  validation summaries in PostgreSQL JSONB, while storing the canonical compiled
  bundle JSON and oversized reports through the existing artifact provider.
- **Rationale**: Drafts are transaction-heavy and need efficient read-modify-
  validate behavior. Compiled bundles are immutable release artifacts and fit
  the existing artifact-storage pattern better than growing PostgreSQL blob
  payloads.
- **Alternatives considered**:
  - Put all authoring and bundle payloads in artifact storage: rejected because
    draft editing and validation need transactional locality.
  - Put all compiled bundles in PostgreSQL: rejected because the constitution
    discourages large immutable blobs in the transactional store.
- **Sources**:
  - [Constitution](../../.specify/memory/constitution.md)
  - [Platform foundation data model](../001-platform-foundation/data-model.md)
