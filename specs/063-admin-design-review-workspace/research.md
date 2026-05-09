# Research: Admin Design Review Workspace

## Decision: Use a backend-owned React workspace envelope

**Rationale**: Existing React admin workspaces use backend-owned envelopes for
scope, state, links, live summaries, provenance, and safe action descriptors.
This keeps authorization and redaction centralized and avoids client-side
composition from multiple unaudited endpoints.

**Alternatives considered**:
- Direct client calls to every design-review endpoint: rejected because the
workspace would duplicate backend state composition and action eligibility logic.
- Static test data in production bundle: rejected because the roadmap forbids
mock UI records.

## Decision: Reuse existing design-review and coordinator APIs for mutations

**Rationale**: Spec 060 and Spec 062 already own durable session creation,
round launch, completion, handoff, and manual-resolution semantics. The React
workspace should not create a parallel write model.

**Alternatives considered**:
- New React-only mutation endpoints: deferred unless existing APIs prove too
coarse. Existing APIs already expose safe request/response contracts.

## Decision: Workflow options come from published workflow bundles

**Rationale**: The coordinator requires a published workflow bundle. Listing
authorized tenant/global published bundles in the envelope lets the UI present
real options and hide launch controls when none exist.

**Alternatives considered**:
- Hard-coded template IDs: rejected because production UI would imply records
that may not exist.

## Decision: QA seeds live rows through scripts

**Rationale**: Local QA needs deterministic evidence. Seeding the QA database is
acceptable because the production route still reads live durable rows and empty
tenants remain empty.

**Alternatives considered**:
- Embedding QA rows in the route: rejected as hidden fixture behavior.

## Decision: Manual controls are state-driven

**Rationale**: The backend coordinator state is authoritative for whether manual
resolution is required. The UI should render actions only when that state says
they are valid.

**Alternatives considered**:
- Always render disabled controls: rejected because it creates noisy repeated
actions and can confuse manual QA.
