# Research: Design Review Coordinator And Iteration Loop

## Decision: Launch One Runtime Run Per Round

**Decision**: The coordinator creates one `runtime_execution_bundles` record and
one `runtime_workflow_runs` record for each review round. The workflow graph is
the published bundle selected for the session or request.

**Rationale**: The existing graph executor is acyclic and worker-driven.
Launching another run for the next revision preserves that model.

**Alternatives Considered**:

- Add graph cycles: rejected because the roadmap explicitly prohibits cyclic
  graph execution.
- Store coordinator-only synthetic runs: rejected because runtime evidence would
  not be worker-visible or compatible with existing operations/debug surfaces.

## Decision: Quorum Policies Are Explicit And Small

**Decision**: Implement `four_of_five_no_blockers` and
`three_of_four_no_blockers` as named policies. Both require approval count at or
above quorum and a total blocking issue count of zero.

**Rationale**: These are the roadmap policies. A small explicit policy map is
auditable and testable.

**Alternatives Considered**:

- Arbitrary policy expressions: rejected for this spec because it expands policy
  language and validation scope.

## Decision: Revision Loop Is Append-Only

**Decision**: When quorum does not pass and max rounds remain, create a new
`DesignRevision` with `previous_revision_id` set to the reviewed revision.

**Rationale**: This preserves immutable revision history and gives the next
round exactly one revision to review.

**Alternatives Considered**:

- Mutate active revision: rejected because it breaks immutable evidence.

## Decision: Manual Resolution Owns Ambiguous Outcomes

**Decision**: Incomplete evidence, contradictory verdicts, unsafe payloads,
policy conflicts, and max-round exhaustion move the session to
`manual_resolution`.

**Rationale**: The coordinator must not infer approvals or revisions when the
evidence is not trustworthy.

**Alternatives Considered**:

- Retry automatically on any incomplete evidence: rejected because it can mask
  policy and evidence defects.

## Decision: Existing Tables Are Sufficient

**Decision**: Use existing Spec 060 design review tables and runtime
orchestration tables. Add repository methods for status updates and next
revision creation.

**Rationale**: The schema already contains session status, round status,
workflow run references, revision predecessor links, verdicts, quorum decisions,
manual decisions, and handoffs.

**Alternatives Considered**:

- Add coordinator state table: rejected unless implementation discovers a
  durable field that cannot be represented by existing tables.

## Decision: Coordinator APIs Extend Existing Design Review Routes

**Decision**: Add JSON routes under `/admin/design-reviews` for coordinator
state, round launch, round completion, and manual coordinator decisions.

**Rationale**: Existing design review routes own tenant authorization,
redaction-safe response helpers, and API tags.

**Alternatives Considered**:

- Separate `/admin/design-review-coordinator` router: rejected because it would
  duplicate auth/service wiring and split one domain across route families.

## Decision: QA Uses Deterministic Runtime Documents

**Decision**: QA seeds a simple published workflow bundle and uses deterministic
or mocked model-backed execution paths. The verifier checks persisted
coordinator state.

**Rationale**: Local QA must not depend on real providers or external services.

**Alternatives Considered**:

- Live model-backed provider round: rejected by local QA and secret hygiene
  constraints.
