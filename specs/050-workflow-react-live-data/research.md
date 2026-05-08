# Research: Workflow React Live Data

## Decision: Use Existing Workflow Registry Services As Source Of Truth

**Decision**: Workflow React projections will read and mutate workflow state through the existing workflow registry repository/service layer, validation helpers, publish-gate evaluator, sharing helpers, artifact repository, and test-bench evidence service.

**Rationale**: The roadmap explicitly requires durable live data and existing services already own workflow lineages, drafts, revisions, validation, publishing, sharing, artifacts, and required evidence. Reusing them preserves revision semantics, audit behavior, tenant guards, bundle pinning, and publish readiness.

**Alternatives considered**:

- Keep deterministic builders and rename the labels: rejected because fixed workflow rows, `qa030` IDs, and fake evidence remain production mock data.
- Add a new React-specific workflow table: rejected because it duplicates source-of-truth state and creates reconciliation risk.
- Query database models directly from routers: rejected because workflow registry services already encapsulate validation, publish, sharing, artifacts, and tenant rules.

## Decision: Introduce A Workflow React Projection Layer

**Decision**: Convert `admin/workflow_builder.py` from deterministic payload builders into projection functions that adapt durable workflow records into `admin_workflow_builder.py` response models.

**Rationale**: Existing React components and tests already consume workflow builder envelope contracts. A projection layer keeps route code thin, lets tests target transformation rules, and avoids moving business decisions into frontend code.

**Alternatives considered**:

- Put projection logic directly in `admin_react.py`: rejected because route functions would become hard to test and would mix authorization, querying, and presentation.
- Rebuild the frontend around raw workflow registry API schemas: rejected because this spec is bounded to live data replacement, not a new workflow UI architecture.

## Decision: Preserve Existing React Workflow Route Family

**Decision**: Keep the current registry, create, builder, draft detail, version detail, publish-gate, lookup, save, validate, and publish route family. Add or adapt parameters only where needed for live IDs, filters, pagination, and stale conflict recovery.

**Rationale**: Preserving route shape minimizes compatibility risk for the React UI and validation scripts while still removing mock data. Clarification establishes that lineage-oriented or ID-less entry points open the latest authorized active draft, while explicit detail routes require durable identifiers.

**Alternatives considered**:

- Replace the whole route family with new URLs: rejected because it expands scope and creates avoidable navigation churn.
- Keep one builder route that always returns the first workflow: rejected because it hides empty and multi-workflow states and can leak data across scopes.

## Decision: Backend-Owned List Controls And Empty States

**Decision**: Workflow registry list projections will expose backend-owned search, status, scope, sort, pagination, provenance, and empty-state metadata. The browser may render controls and submit filter requests but does not decide which hidden records exist.

**Rationale**: Filtering and pagination are part of tenant-scoped data access. Backend-owned controls let tests verify empty and seeded behavior without relying on frontend-only filtering over a preloaded fixture list.

**Alternatives considered**:

- Client-side filtering over all visible records: rejected because it can become inefficient, makes pagination fake, and risks exposing records that should not be sent to the browser.
- No filtering in this spec: rejected because the existing registry UI already presents list state and seeded QA should prove live list behavior.

## Decision: Build Graph Preview From Stored Documents

**Decision**: Graph previews will be generated from persisted workflow draft documents using existing graph preview and reference validation helpers. Invalid documents return safe findings and unavailable/blocked states instead of synthetic fallback graphs.

**Rationale**: The graph is a core builder affordance and must reflect the stored draft. Existing helpers already validate references and can produce safe summaries without raw payload leakage.

**Alternatives considered**:

- Continue showing a default graph when parsing fails: rejected because it masks invalid live data with mock graph nodes.
- Render raw document JSON in place of graph preview: rejected because it weakens UX and increases redaction risk.

## Decision: Query Publish-Gate And Test-Bench Evidence For Readiness

**Decision**: Publish readiness will use existing publish-gate evaluation and test-bench evidence records for the current draft or published bundle, distinguishing missing, stale, failing, passing, denied, and unavailable states.

**Rationale**: Spec 024/030 publish-gate behavior already defines required evidence semantics. React must display those durable results, not fake readiness or fake pass evidence.

**Alternatives considered**:

- Treat validation pass as publish readiness: rejected because required test-bench evidence is a separate gate.
- Return a canned missing-evidence message: rejected because seeded QA must prove live missing/stale/passing evidence projections.

## Decision: Seed QA050 Through Durable Paths

**Decision**: QA050 seeded validation will create at least one Acme tenant workflow draft with revisions, validation evidence, publish-gate evidence, and a published bundle through durable repositories, domain services, migrations intended for QA, or admin APIs. Empty-state validation uses a genuinely empty workflow database path.

**Rationale**: The live-data roadmap requires both empty and seeded validation. Durable seed setup keeps production builders clean while making browser and API tests deterministic.

**Alternatives considered**:

- Keep production builders as QA seed source: rejected because that is the mock-data pattern this roadmap removes.
- Seed only via frontend actions: rejected because Playwright should exercise a safe mutation, but route tests and Spec QA need repeatable preconditions.

## Decision: Scanner Blocks Old Workflow Mock Markers

**Decision**: The live-data scanner mappings will classify old workflow deterministic markers, including `DEFAULT_DRAFT_ID`, `DEFAULT_LINEAGE_ID`, `draft-rev-qa030`, fake publish evidence, fake audit references, and fake graph nodes, as blocking production findings once Spec 050 lands.

**Rationale**: Spec 048 introduced the inventory/guardrail mechanism. Updating it for workflow-specific markers prevents regression after deterministic builders are removed.

**Alternatives considered**:

- Rely only on unit tests: rejected because generated contracts and built assets need production-surface scanning too.
- Ban all `qa030` markers globally: rejected because historical specs and test fixtures may legitimately retain deterministic QA values under test-only paths.
