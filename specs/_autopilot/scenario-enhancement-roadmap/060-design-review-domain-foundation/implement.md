# Spec 060 - Design Review Domain Foundation: Implement

Roadmap source: `scenario_enhancement.md`

## Deterministic Targets

- Feature directory: `specs/060-design-review-domain-foundation`
- Git branch: `codex/060-design-review-domain-foundation`
- QA id: `qa060`
- QA database: `multi_agent_platform_qa060`
- Post-spec curl-test database: `multi_agent_curl_test`
- Curl regression source: `curl_testing.md`

## Scenario Autonomy Rules

- Continue directly to the next spec after validation passes.
- Do not commit, stage, push, or create pull requests.
- Keep all local QA deterministic with local-principal auth and mocked provider/model paths unless a spec explicitly allows otherwise.
- Preserve tenant isolation, redaction, auditability, safe summaries, artifact references, and truthful live-data UI states.

## Implement Prompt

/speckit.implement Implement only the Design Review domain foundation tasks. Keep changes additive. Do not implement live model role execution, round auto-launching, or the Admin design review workspace in this spec. Run focused backend validation, Alembic migration validation, contract tests, integration route tests, ruff, mypy for touched modules, and spec QA docs validation.

## Required Post-Spec Validation Contract

After implementation, the active spec must pass QA document validation, `run_spec_qa.py`, Playwright UI validation, curl_testing.md coverage review/update, and the `multi-agent-curl-test` runner before the next spec starts. If the spec adds or changes an API, update `curl_testing.md` in the same spec and fix the implementation or curl commands until the multi-agent curl regression passes. Do not pause between completed specs and do not create git commits.
## Scenario Architecture Context

# Design Reviewer Scenario Enhancement

Review date: 2026-05-08

This document describes the architecture needed to turn the current deterministic
Design Reviewer Council setup into a first-class production feature. It is
written for Spec Kit implementation planning. The current platform can already
model and run one deterministic acyclic review round through workflow registry,
graph execution, and test-bench evidence. The missing production features are:

- durable design-review sessions, revisions, rounds, reviewer assignments,
  verdicts, quorum decisions, and development handoffs
- model-backed role-node execution through `ModelGateway`
- a review coordinator that launches successive acyclic workflow runs until
  quorum passes or manual resolution is required
- a live-data Admin workspace for session history, reviewer feedback, revision
  diffs, quorum decisions, and handoff state
- reusable templates and QA evidence that prove the scenario without mock UI
  records or hidden fixture behavior

The design below preserves the platform's existing constraints: tenant isolation,
local-principal/Auth0 authorization, redaction-safe records, immutable evidence,
no raw secrets, no raw provider payloads in UI or QA artifacts, deterministic
local QA, and acyclic graph execution.

## Architecture Overview

### Current Supported Surface

The current implementation supports these pieces today:

- Workflow drafts and published bundles can represent a lead role, reviewer
  sub-agent roles, quorum joins, synthesis, and terminal handoff nodes.
- `GraphExecutionService` schedules acyclic role nodes in parallel waves and can
  evaluate `quorum` joins with `failure_behavior=manual_resolution`.
- The worker can claim DB-backed runtime workflow runs and execute the graph.
- Test Bench can create required deterministic evidence for workflow publish
  gates.
- Prompt/profile/provider governance can publish prompts and activate runtime
  profiles, but graph role nodes currently execute through the deterministic
  role executor.

### Required Additions

The production Design Reviewer Council should be built as an additive domain on
top of workflow registry, runtime orchestration, governance, storage, audit, and
test bench:

1. `DesignReviewService` owns first-class session records and immutable design
   revisions.
2. `DesignReviewCoordinator` launches one runtime workflow run per review round.
   It never creates cycles in one graph. If quorum fails, it records the
   decision and creates the next revision before launching another run.
3. `ModelBackedRoleNodeExecutor` plugs into `GraphExecutionService` and calls
   `ModelGateway` only when the workflow/session execution mode permits it.
4. Contract validation converts lead, reviewer, synthesis, and handoff outputs
   into safe structured records, artifact references, digests, and usage
   provenance.
5. Admin routes under `/admin/app/design-reviews` expose live session state,
   round history, quorum decisions, revision diffs, manual-resolution actions,
   and final handoff references.
6. A reusable workflow template and deterministic QA suite make the scenario
   easy to install, test, and publish.

### Non-Goals

- Do not add a cyclic workflow graph executor.
- Do not store raw prompts, completions, secrets, authorization headers, private
  channel payloads, memory contents, or raw external tool payloads in design
  review tables, route responses, screenshots, or QA artifacts.
- Do not replace prompt/profile/provider governance. Design review assignments
  should reference existing published prompt versions, active profile versions,
  and provider routing provenance.
- Do not make the Admin UI invent sample sessions, reviewer rows, or successful
  handoffs. Empty states must be truthful.

## Architecture Diagrams

### Component Architecture

```mermaid
flowchart LR
    AdminUI["Admin Design Review Workspace"] --> DesignAPI["Design Review API"]
    DesignAPI --> DesignService["DesignReviewService"]
    DesignService --> DesignRepo["DesignReviewRepository"]
    DesignRepo --> PG[("PostgreSQL")]

    DesignAPI --> Coordinator["DesignReviewCoordinator"]
    Coordinator --> Registry["Workflow Registry Service"]
    Coordinator --> RuntimeRepo["RuntimeOrchestrationRepository"]
    RuntimeRepo --> PG

    Worker["Runtime Worker"] --> GraphExecutor["GraphExecutionService"]
    GraphExecutor --> RoleExecutor["ModelBackedRoleNodeExecutor"]
    GraphExecutor --> RuntimeRepo
    RoleExecutor --> Governance["Prompt/Profile/Provider Governance"]
    RoleExecutor --> Gateway["ModelGateway"]
    RoleExecutor --> ContractValidator["Output Contract Validator"]
    RoleExecutor --> ArtifactStore["Storage Provider"]

    Gateway --> Providers["Provider Adapters"]
    ContractValidator --> DesignService
    ArtifactStore --> Artifacts[("Artifact References")]
    DesignService --> Audit["Audit/Timeline/Usage Evidence"]
    TestBench["Agent Test Bench"] --> Registry
    TestBench --> DesignAPI
```

### Data Model

```mermaid
erDiagram
    DesignReviewSession ||--o{ DesignRevision : has
    DesignReviewSession ||--o{ DesignReviewRound : launches
    DesignReviewSession ||--o| DesignDevelopmentHandoff : produces
    DesignRevision ||--o{ DesignReviewRound : reviewed_by
    DesignReviewRound ||--o{ DesignReviewerAssignment : assigns
    DesignReviewRound ||--o{ DesignReviewerVerdict : records
    DesignReviewRound ||--o| DesignQuorumDecision : evaluates
    DesignReviewRound }o--|| RuntimeWorkflowRun : uses

    DesignReviewSession {
        uuid design_review_session_id
        uuid tenant_id
        string status
        string request_summary
        int active_revision_number
        string quorum_policy_key
        uuid workflow_version_bundle_id
        string owner_principal_id
    }

    DesignRevision {
        uuid design_revision_id
        uuid design_review_session_id
        int revision_number
        string author_role_key
        string safe_summary
        uuid artifact_id
        string payload_digest
        uuid previous_revision_id
    }

    DesignReviewRound {
        uuid design_review_round_id
        uuid design_review_session_id
        uuid design_revision_id
        int round_number
        string status
        uuid workflow_run_id
        int reviewer_count
        int quorum_count
    }

    DesignReviewerAssignment {
        uuid design_reviewer_assignment_id
        uuid design_review_round_id
        string reviewer_key
        string role_key
        uuid prompt_version_id
        uuid profile_version_id
        bool enabled
    }

    DesignReviewerVerdict {
        uuid design_reviewer_verdict_id
        uuid design_review_round_id
        string reviewer_key
        string verdict
        int score
        int blocking_issue_count
        string safe_feedback_summary
        uuid artifact_id
        string output_digest
    }

    DesignQuorumDecision {
        uuid design_quorum_decision_id
        uuid design_review_round_id
        string status
        int approval_count
        int blocking_issue_count
        string next_action
        string policy_version
    }

    DesignDevelopmentHandoff {
        uuid design_development_handoff_id
        uuid design_review_session_id
        uuid approved_revision_id
        uuid artifact_id
        string safe_summary
        string output_digest
    }
```

### Review Round Runtime Shape

```mermaid
flowchart TD
    A["DesignReviewCoordinator launches round"] --> B["Lead Design Agent"]
    B --> C1["Product Fit Reviewer"]
    B --> C2["UX And Interaction Reviewer"]
    B --> C3["Visual And Design System Reviewer"]
    B --> C4["Accessibility Reviewer"]
    B --> C5["Engineering And API Reviewer"]
    C1 --> D["Quorum Join"]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    D --> E["Feedback Synthesizer"]
    E --> F["Terminal Handoff Or Revision Request"]
    F --> G["Coordinator records round result"]
```

### Cross-Round Coordinator Loop

```mermaid
flowchart TD
    A["Create design review session"] --> B["Create design revision 1"]
    B --> C["Launch review round"]
    C --> D{"Quorum reached and no blockers?"}
    D -->|"Yes"| E["Persist development handoff"]
    D -->|"No, feedback clear"| F["Persist revision request"]
    F --> G["Create next design revision"]
    G --> C
    D -->|"Policy conflict or runtime issue"| H["Pause for manual resolution"]
    H --> I{"Manual decision"}
    I -->|"Revise"| G
    I -->|"Approve exception"| E
    I -->|"Cancel"| J["Mark session cancelled"]
```

### Runtime Integration

```mermaid
flowchart LR
    Coordinator["Coordinator"] --> Bundle["Runtime execution bundle with design revision input"]
    Bundle --> DBRun["runtime_workflow_runs status=runnable"]
    DBRun --> Worker["Existing worker lease"]
    Worker --> Graph["GraphExecutionService"]
    Graph --> ExecutorChoice{"Execution mode"}
    ExecutorChoice -->|"mock_model"| Deterministic["DeterministicRoleNodeExecutor"]
    ExecutorChoice -->|"model_gateway"| ModelExec["ModelBackedRoleNodeExecutor"]
    ModelExec --> Gateway["ModelGateway"]
    ModelExec --> Validate["Validate output contract"]
    Validate --> Persist["Persist safe design review evidence"]
    Persist --> CoordinatorResult["Round result evaluation"]
```

## Sequence Diagrams

### Start Session And Launch First Round

```mermaid
sequenceDiagram
    actor Admin
    participant UI as Admin UI
    participant API as Design Review API
    participant Service as DesignReviewService
    participant Coord as DesignReviewCoordinator
    participant Registry as Workflow Registry
    participant Runtime as Runtime Repository
    participant Worker as Runtime Worker

    Admin->>UI: Submit design request
    UI->>API: POST /admin/design-reviews/sessions
    API->>Service: create_session(request, quorum_policy)
    Service->>Service: persist session and revision 1
    API->>Coord: launch_round(session_id, revision_id)
    Coord->>Registry: load published Design Reviewer workflow
    Coord->>Runtime: create execution bundle and runnable workflow run
    Runtime-->>Coord: workflow_run_id
    Coord-->>API: round accepted
    API-->>UI: session and round envelope
    Worker->>Runtime: claim runnable run
```

### Model-Backed Reviewer Execution

```mermaid
sequenceDiagram
    participant Worker as Runtime Worker
    participant Graph as GraphExecutionService
    participant Exec as ModelBackedRoleNodeExecutor
    participant Gov as Governance Repositories
    participant Gateway as ModelGateway
    participant Store as Storage Provider
    participant Design as DesignReviewService

    Worker->>Graph: execute claimed workflow run
    Graph->>Exec: execute role node
    Exec->>Gov: resolve profile, prompt, provider, policy pins
    Exec->>Exec: build redaction-safe model input
    Exec->>Gateway: invoke model with gateway context
    Gateway-->>Exec: normalized result and usage evidence
    Exec->>Exec: validate JSON output contract
    Exec->>Store: store allowed large structured output
    Exec->>Design: record role evidence or reviewer verdict
    Exec-->>Graph: RoleExecutionResult with safe summary and digest
    Graph->>Graph: persist run step, handoff, checkpoint, timeline
```

### Quorum Fails And Next Revision Starts

```mermaid
sequenceDiagram
    participant Graph as GraphExecutionService
    participant Coord as DesignReviewCoordinator
    participant Service as DesignReviewService
    participant Runtime as Runtime Repository

    Graph->>Runtime: persist terminal revision_required output
    Coord->>Runtime: observe completed round
    Coord->>Service: record reviewer verdicts and quorum decision
    Service-->>Coord: decision = revision_required
    Coord->>Service: create immutable next revision from synthesis feedback
    Service-->>Coord: design_revision_id
    Coord->>Runtime: launch next acyclic review-round run
```

### Quorum Passes And Handoff Is Published

```mermaid
sequenceDiagram
    participant Graph as GraphExecutionService
    participant Coord as DesignReviewCoordinator
    participant Service as DesignReviewService
    participant Store as Storage Provider
    participant UI as Admin UI

    Graph->>Coord: round completed with quorum reached
    Coord->>Service: evaluate and persist quorum decision
    Service->>Store: persist final handoff artifact
    Service->>Service: mark session approved
    Service-->>Coord: handoff reference
    UI->>Service: GET session detail
    Service-->>UI: approved session, handoff summary, artifact refs
```

### Manual Resolution

```mermaid
sequenceDiagram
    actor Admin
    participant UI as Admin UI
    participant API as Design Review API
    participant Service as DesignReviewService
    participant Coord as DesignReviewCoordinator

    Service-->>UI: round paused for manual resolution
    Admin->>UI: choose revise, approve exception, retry, or cancel
    UI->>API: POST /sessions/{id}/manual-decisions
    API->>Service: record manual decision and audit event
    alt Revise
        Service->>Coord: create next revision and launch round
    else Approve exception
        Service->>Service: create handoff with accepted risk marker
    else Retry
        Service->>Coord: relaunch same revision with new idempotency key
    else Cancel
        Service->>Service: mark session cancelled
    end
```

## Implementation Notes

### Durable Domain

Add a new `admin/design_review` domain with Pydantic schemas, SQLAlchemy models,
repositories, and services. These records should be tenant-scoped and immutable
where they represent evidence:

- sessions: mutable status and active revision pointer
- revisions: immutable design packet artifacts and safe summaries
- rounds: one runtime workflow run against one revision
- assignments: reviewer role/profile/prompt pins used in one round
- verdicts: immutable structured reviewer outputs
- quorum decisions: immutable aggregate policy results
- handoffs: immutable final development handoff references

Recommended source locations:

- `src/multi_agent_platform/admin/design_review/`
- `src/multi_agent_platform/api/schemas/design_review.py`
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `src/multi_agent_platform/db/models/design_review.py`
- `src/multi_agent_platform/db/repositories/design_review.py`
- `frontend/admin/src/components/designReview/`

### Coordinator

The coordinator should be the only component that implements the repeated
review loop. It should:

- create sessions and initial revisions
- load a published Design Reviewer Council workflow bundle
- create DB-backed runtime execution bundles and runnable workflow runs
- record round completion from runtime output, timeline, and role evidence
- evaluate quorum using design-review policy, not only raw graph branch success
- launch the next round when revision is required
- pause for manual resolution when policy cannot decide
- enforce a max-round limit and explicit cancellation

The coordinator should not call the existing in-memory runtime facade for
production design reviews. It should write through
`RuntimeOrchestrationRepository` so the existing worker can claim and execute
the run.

### Model-Backed Role Executor

`GraphExecutionService` already accepts a `RoleNodeExecutor`; the worker
currently uses the deterministic default. Add a model-backed executor and a
factory/selection layer so each run chooses the correct executor from persisted
execution mode and policy pins.

The model-backed executor must:

- load prompt/profile/provider pins for the role
- build a safe model input from upstream summaries and artifact references
- call `ModelGateway` with a complete gateway invocation context
- validate the model output against the role output contract
- persist large outputs as governed artifacts when allowed
- return only safe summaries, digests, structured safe output, and usage
  provenance to graph execution
- fail closed when prompt/profile/provider pins, credentials, policy, or output
  validation are not ready

### Admin Workspace

Add a live-data Admin workspace after backend contracts stabilize. It should
support:

- session creation and safe request summary capture
- prompt/profile/provider readiness and workflow template readiness
- round timeline with reviewer assignments, verdict summaries, quorum decision,
  revision request, and handoff status
- revision diffs based on safe summaries and artifact metadata
- manual resolution actions with audit-safe decisions
- handoff export/download only through artifact references and allowed policies

The UI must not render mock sessions. Empty, denied, loading, stale, and error
states must be backend-owned.

## Accuracy Review

This design is implementable against the current repository because it builds
on existing extension points and deliberately avoids unsupported runtime cycles:

- `GraphExecutionService` already supports role executor injection, parallel
  waves, quorum joins, terminal nodes, and manual-resolution pauses.
- The DB-backed worker already claims `runtime_workflow_runs` through
  `RuntimeOrchestrationRepository`; the coordinator should create DB-backed runs
  for production instead of using the in-memory runtime facade.
- Workflow registry already stores document contracts, roles, nodes, joins,
  prompt/profile references, test requirements, validation results, publish
  gates, and compiled bundle summaries.
- Prompt/profile/provider governance and `ModelGateway` already exist, so the
  missing executor can resolve pins and call the gateway without inventing a new
  provider layer.
- Test Bench already supports deterministic required evidence and publish-gate
  summaries; the template spec can extend this with scenario-specific fixtures.
- React Admin live-data patterns already exist for workflows, governance,
  operations, test bench, usage, memberships, and channels; the design-review
  workspace should follow those patterns.

Known implementation risks:

- The executor must be strict about redaction and artifact boundaries because
  design packets and reviewer feedback may contain product-sensitive content.
- Coordinator idempotency must prevent duplicate rounds when the same session
  action is retried.
- Manual-resolution behavior must be auditable and must not silently override
  blocking reviewer issues.
- Contract validation must distinguish model formatting failures from reviewer
  verdicts that legitimately request changes.
- Admin route envelopes must not synthesize sessions or handoffs when no durable
  records exist.

Definition of done for the full scenario:

- A tenant admin can create a design review session from Admin.
- The coordinator launches round 1 as a DB-backed runtime run.
- Lead and reviewer role nodes can run in deterministic mode for QA and
  model-backed mode when configured policy permits it.
- Four-of-five and three-of-four quorum rules produce correct decisions with no
  blocking issues.
- Failed quorum creates a new design revision and launches a new acyclic round,
  subject to max-round and manual-resolution policy.
- Approved quorum creates a development handoff with safe artifact references.
- Admin shows live session, round, revision, verdict, decision, and handoff
  data with truthful empty/denied/error states.
- Required test-bench evidence and Playwright QA cover success, revision,
  manual-resolution, redaction, and cross-tenant denial paths.

## Cross-Spec Rollout Notes

```mermaid
flowchart TD
    S060["060 Design Review Domain Foundation"] --> S061["061 Model-Backed Graph Role Executor"]
    S060 --> S062["062 Design Review Coordinator"]
    S061 --> S062
    S062 --> S063["063 Admin Design Review Workspace"]
    S060 --> S063
    S063 --> S064["064 Template, Test Bench, Publish Gates"]
    S062 --> S064
```

Recommended implementation order:

1. Spec 060 creates the durable domain and route contracts.
2. Spec 061 adds model-backed role execution while preserving deterministic QA.
3. Spec 062 connects sessions to repeated acyclic runtime rounds.
4. Spec 063 adds the live-data Admin workspace.
5. Spec 064 packages the scenario as a reusable template with end-to-end QA and
   publish-gate evidence.
