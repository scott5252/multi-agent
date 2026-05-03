# Feature Specification: Workflow Graph Execution And Parallel Sub-Agent Runtime

**Feature Branch**: `codex/020-workflow-graph-execution-parallel-sub-agent-runtime`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add workflow graph execution for published workflow bundles. The runtime worker must load the published bundle document, execute role nodes in dependency order, fan out independent branches in parallel, apply join policies such as all_success, quorum, first_success, and manual_resolution, invoke agent and sub-agent runtime profiles through the existing ModelGateway and policy services, persist per-node run steps, checkpoints, handoffs, side-effect intents, approvals, timeline events, partial failure summaries, and final structured outputs. The first flagship scenario is the Daily Intelligence Briefing workflow: Telegram starts one orchestrator run, four scout sub-agents run in parallel, their outputs join, a focus recommender runs after the join, and a synthesis node produces a final briefing. Cross-tenant access must fail closed, execution must be idempotent on resume, and no raw secrets or raw tool payloads may be rendered."

## Clarifications

- Q: Should local QA execute real provider or external tool calls? -> A: No. QA uses deterministic mock role execution and safe summaries; live provider credentials and real tool connectors remain outside this feature's validation path. (autopilot)
- Q: How should raw role outputs and tool payloads be stored? -> A: Persist only structured safe summaries inline, with artifact references for oversized or sensitive payloads; never render raw secrets, credentials, prompts, model responses, or raw tool payloads. (autopilot)
- Q: What is the v1 completion path for manual_resolution joins? -> A: Persist an explicit waiting state, approval/timeline evidence, and a partial failure summary; resume requires an existing durable approval decision path rather than transient chat state. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute Published Workflow Graphs (Priority: P1)

Platform operators need claimed workflow runs to execute the graph stored in the
published workflow bundle instead of stopping after a worker claim.

**Why this priority**: This closes the central runtime gap: published workflow
metadata must turn into durable node execution.

**Independent Test**: Seed a published workflow bundle with an entry role node,
downstream role node, and terminal node, create a runnable run, execute one
worker poll, and verify run steps, timeline events, checkpoints, handoffs, and
final structured output are persisted.

**Acceptance Scenarios**:

1. **Given** a runnable run references a published bundle, **When** a worker
   claims it, **Then** the worker loads the pinned graph and executes nodes in
   dependency order.
2. **Given** a role node completes successfully, **When** downstream nodes
   become eligible, **Then** handoff summaries and runnable step records are
   persisted before downstream execution starts.
3. **Given** execution reaches a terminal node, **When** final output is
   available, **Then** the workflow run is marked succeeded with a safe output
   reference.

---

### User Story 2 - Fan Out Parallel Sub-Agent Branches (Priority: P2)

Workflow authors need independent role branches to run concurrently when graph
dependencies allow it, including sub-agent scout branches in the Daily
Intelligence Briefing workflow.

**Why this priority**: Parallel sub-agent execution is the flagship scenario
and the reason the graph executor exists.

**Independent Test**: Execute a Daily Intelligence Briefing graph where four
scout role nodes share the same predecessor and verify they are scheduled in one
parallel wave, record distinct run steps, and complete before the join unlocks.

**Acceptance Scenarios**:

1. **Given** four scout nodes depend only on the orchestrator node, **When** the
   orchestrator succeeds, **Then** all four scout nodes are scheduled in the
   same execution wave.
2. **Given** a worker resumes after a crash during the scout wave, **When** the
   graph executor restarts, **Then** completed scout steps are not duplicated
   and remaining scouts continue idempotently.
3. **Given** scout steps finish with safe structured outputs, **When** the join
   evaluates, **Then** the merged input summary contains one safe branch summary
   per scout.

---

### User Story 3 - Apply Join Policies And Partial Failure Semantics (Priority: P3)

Runtime operators need joins to behave predictably for all_success, quorum,
first_success, and manual_resolution policies, with durable failure summaries.

**Why this priority**: Joins decide whether parallel branches produce reliable
runtime outcomes or ambiguous partial results.

**Independent Test**: Run unit tests for each join policy over synthetic branch
results and integration tests for success, quorum success, first-success, and
manual-resolution wait behavior.

**Acceptance Scenarios**:

1. **Given** an `all_success` join has any failed branch, **When** the join
   evaluates, **Then** downstream execution does not proceed and a safe partial
   failure summary is persisted.
2. **Given** a `quorum` join reaches its configured threshold, **When** it
   evaluates, **Then** downstream execution proceeds with successful branch
   summaries and failed branch safe reasons.
3. **Given** a `manual_resolution` failure behavior is configured, **When** a
   join cannot proceed automatically, **Then** the run enters a durable paused
   state with approval/timeline evidence.

---

### User Story 4 - Preserve Tenant Isolation, Resume Safety, And Redaction (Priority: P4)

Security reviewers need graph execution to fail closed across tenant boundaries,
resume idempotently, and avoid leaking raw secrets or tool payloads.

**Why this priority**: Runtime execution crosses workflow, model, prompt,
skill, memory, approval, and channel boundaries; unsafe execution would violate
the platform constitution.

**Independent Test**: Attempt to execute a tenant run with a cross-tenant bundle
reference, resume the same run twice, and scan timeline/output/step records for
raw secret-looking fields.

**Acceptance Scenarios**:

1. **Given** a tenant run references a bundle owned by another tenant, **When**
   the worker tries to load it, **Then** execution fails closed with a safe
   denial event.
2. **Given** a worker crashes after some node steps succeed, **When** another
   worker resumes the run, **Then** succeeded node steps and handoffs are reused
   rather than duplicated.
3. **Given** node execution produces sensitive-looking fields, **When** output
   references, timeline payloads, and failure summaries are persisted, **Then**
   raw secrets, credential values, prompts, model responses, and raw tool
   payloads are absent.

### Edge Cases

- Published bundle id is missing, retired, hidden, or tenant-inaccessible.
- Bundle summary lacks a graph document or has stale schema fields.
- Entry node is inactive or missing.
- Graph has a cycle, orphan node, duplicate key, or no terminal node.
- Role node references a missing role or missing prompt/profile reference.
- Sub-agent profile readiness is unknown or not ready.
- Skill requirements are not ready for a role node.
- A node succeeds before the worker process crashes.
- A retry encounters an already-succeeded step key.
- A branch fails before a join reaches its threshold.
- A join policy has an invalid quorum count.
- `first_success` receives a success after another branch has already won.
- `manual_resolution` creates a paused run and approval evidence.
- Final output exceeds inline-safe limits.
- Timeline payload contains sensitive-looking keys.
- Tenant id on run and bundle do not match.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load the pinned published workflow bundle for each
  claimed workflow run before executing any graph node.
- **FR-002**: System MUST fail closed when the run tenant and bundle tenant are
  incompatible.
- **FR-003**: System MUST derive executable graph nodes, edges, contracts,
  roles, prompt/profile references, skill references, join policies, approval
  gates, and terminal nodes from the published bundle document or summary.
- **FR-004**: System MUST create or reuse one run-step record per graph node and
  attempt, keyed idempotently by workflow run and node key.
- **FR-005**: System MUST execute role nodes in dependency order and schedule
  independent ready role nodes in the same parallel wave.
- **FR-006**: System MUST treat role nodes and sub-agent role nodes through the
  same role-execution boundary while preserving role kind in step metadata.
- **FR-007**: System MUST provide a deterministic mock role executor for local
  QA and tests without real provider calls.
- **FR-008**: System MUST expose a role-execution boundary that can later call
  the existing ModelGateway, model-skill config resolver, memory service, and
  tool-policy services with pinned provenance.
- **FR-009**: System MUST persist safe input references, output references,
  branch summaries, error references, checkpoints, handoff envelopes, timeline
  events, and final output references.
- **FR-010**: System MUST evaluate `all_success`, `quorum`, `first_success`,
  and `manual_resolution` join semantics deterministically.
- **FR-011**: System MUST persist partial failure summaries when a graph cannot
  proceed automatically.
- **FR-012**: System MUST pause the run and persist approval/timeline evidence
  when manual resolution is required.
- **FR-013**: System MUST mark the run succeeded when a terminal node is reached
  and final structured output has been safely persisted.
- **FR-014**: System MUST mark the run recoverable_failed or failed with safe
  diagnostics when graph execution cannot continue.
- **FR-015**: System MUST avoid rendering or persisting raw secrets, credential
  values, raw prompts, raw model responses, raw tool payloads, raw channel
  messages, or unauthorized tenant data in inline records.
- **FR-016**: Tests MUST cover graph contracts, bundle loading, dependency
  scheduling, parallel fan-out, role/sub-agent execution, join policies,
  partial failures, checkpoint/resume idempotency, worker integration, tenant
  isolation, redaction, Daily Intelligence Briefing, docs, and coverage.
- **FR-017**: Documentation MUST include quickstart validation, QA guide, UI
  walkthrough, non-developer QA user guide, PR review notes, testing
  instructions, README updates, and `docs/quickstart.md` updates.

### Key Entities *(include if feature involves data)*

- **Graph Execution Plan**: Normalized executable view of nodes, edges, roles,
  joins, contracts, prompt/profile refs, and terminal nodes for one pinned
  bundle.
- **Graph Node State**: Durable status for one node key in one workflow run,
  including attempt, safe inputs, safe outputs, errors, and checkpoints.
- **Execution Wave**: Set of ready nodes whose dependencies are satisfied and
  can run concurrently.
- **Branch Result**: Safe summary of a branch outcome used by join evaluation.
- **Join Decision**: Deterministic decision for all_success, quorum,
  first_success, or manual_resolution.
- **Final Output Reference**: Safe structured output summary or artifact
  reference exposed to channel/result readers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Worker integration tests show a claimed published workflow run
  completes from entry node to terminal node without manual database edits.
- **SC-002**: Daily Intelligence Briefing tests show four scout nodes scheduled
  in one parallel wave and joined before focus and synthesis nodes execute.
- **SC-003**: Crash-resume tests prove rerunning the executor after a partial
  success does not duplicate completed node steps.
- **SC-004**: Join policy tests cover all_success, quorum, first_success, and
  manual_resolution outcomes.
- **SC-005**: Tenant isolation tests prove cross-tenant bundle execution fails
  closed.
- **SC-006**: Redaction tests scan node inputs, outputs, timeline events,
  failure summaries, and final output references for forbidden raw fields.
- **SC-007**: Relevant automated coverage remains at or above 90 percent.
- **SC-008**: QA020 documents and validation evidence are generated for manual
  and automated reviewers.

## Assumptions

- Published bundle rows already contain the workflow graph summary, run version
  bundle pins, prompt/profile pins, and publish-gate summaries produced by
  existing workflow registry publication.
- This feature executes graph orchestration and deterministic mock role outputs
  in QA; real external skill tool connectors are handled by Spec 021, Telegram
  natural-language delivery by Spec 022, briefing preferences by Spec 023, test
  bench gate automation by Spec 024, and live provider credential resolution by
  Spec 025.
- The worker continues to use existing runtime run, step, lease, checkpoint,
  handoff, side-effect, approval, lineage, and timeline tables.
- Server-rendered admin UI does not change in this feature; existing run,
  operations, workflow, and audit screens should show the new runtime evidence.
