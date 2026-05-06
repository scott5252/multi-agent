# Design Reviewer Workflow Example

Review date: 2026-05-05

This file documents how to set up and develop a "Design Reviewer Council"
scenario against the current `multi-agent-platform` codebase. It follows the
same style as `test_example.md`: first stating what is implementable now, then
mapping the scenario to current code, current gaps, and a safe implementation
path.

The scenario uses the platform as a governed design workflow:

1. A user describes what they want to build.
2. A Lead Design Agent creates a structured design packet.
3. The Lead Design Agent fans out to four or five independent reviewer
   sub-agents.
4. Reviewers return structured feedback and an approval verdict.
5. A quorum gate checks whether three of four, or four of five, approve with no
   blocking issues.
6. If quorum is not reached, the Lead Design Agent revises the design and starts
   another review round.
7. When quorum is reached, the workflow produces a development-ready handoff.

## Implementation Verdict

The current product can support a governed, deterministic QA version of this
scenario today, and the project can develop the full production version with
well-scoped additions.

Current support is strongest for:

- workflow drafting through the React workflow builder
- agent and sub-agent role modeling
- parallel role-node execution
- quorum joins such as three of four or four of five reviewers
- deterministic local and CI execution
- prompt/profile/provider governance
- safe audit, redaction, artifact references, and test-bench evidence
- manual approval pauses when a design needs human resolution

The main production gaps are:

- a purpose-built design review domain model for design packets, review rounds,
  reviewer votes, quorum decisions, and final handoff artifacts
- a model-backed role-node executor that calls `ModelGateway` for lead and
  reviewer agents instead of the default deterministic executor
- a review-round coordinator that launches successive acyclic workflow runs
  until quorum is reached
- optional React admin UI for design review history, reviewer feedback,
  iteration diffs, and development handoff status

The repeated "iterate until quorum" behavior should not be implemented as a
cycle inside one workflow graph. The current graph executor validates workflow
plans as acyclic. Instead, one graph run should represent one design review
round. If quorum fails, a coordinator records the next design revision and
launches a new review-round run. That keeps the runtime resumable, auditable,
and compatible with the existing graph execution model.

## Current Code Structure Reviewed

The scenario setup below is grounded in these current code areas:

- `test_example.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/plan.md`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/plan.md`
- `specs/030-react-workflow-builder/plan.md`
- `specs/031-model-prompt-profile-and-provider-governance/plan.md`
- `specs/033-react-agent-and-workflow-test-bench/plan.md`
- `specs/037-react-admin-migration-hardening-and-jinja-retirement/plan.md`
- `src/multi_agent_platform/api/schemas/workflow_registry.py`
- `src/multi_agent_platform/admin/workflow_registry/validation.py`
- `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- `src/multi_agent_platform/admin/workflow_builder.py`
- `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- `src/multi_agent_platform/workers/orchestration.py`
- `src/multi_agent_platform/prompts/*`
- `src/multi_agent_platform/agents/*`
- `src/multi_agent_platform/model_providers/*`
- `src/multi_agent_platform/testing/agent_bench/*`
- `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `frontend/admin/src/components/workflows/*`
- `frontend/admin/src/components/governance/*`
- `frontend/admin/src/components/testBench/*`

## Scenario To Build

A product owner or builder sends a design request:

```text
Design an admin workspace where tenant admins can create, test, and publish
multi-agent workflows without editing raw JSON.
```

The Lead Design Agent turns that request into a structured design packet:

- product goal
- target users
- primary tasks
- page and route structure
- workflow steps
- data contracts
- expected backend APIs
- component inventory
- empty, loading, denied, stale, and error states
- accessibility requirements
- implementation risks
- acceptance criteria

The Lead Design Agent then sends the design packet to five independent
reviewers:

1. Product Fit Reviewer
2. UX And Interaction Reviewer
3. Visual And Design System Reviewer
4. Accessibility Reviewer
5. Engineering And API Reviewer

Each reviewer returns a structured verdict:

```json
{
  "reviewer_key": "accessibility-reviewer",
  "verdict": "request_changes",
  "score": 3,
  "blocking_issues": [
    {
      "code": "keyboard-path-missing",
      "summary": "The graph-only node editor needs a keyboard-accessible list alternative.",
      "severity": "blocking"
    }
  ],
  "important_feedback": [
    "Add explicit focus order for graph, node list, validation panel, and publish gate.",
    "Describe accessible names for icon-only actions."
  ],
  "nice_to_have": [
    "Include a compact screen-reader summary for the current graph structure."
  ],
  "approval_conditions": [
    "Add keyboard-accessible node and edge lists.",
    "Add focus restoration after save and validation actions."
  ]
}
```

The quorum gate evaluates the reviewer outputs:

- four of five reviewers must return `approve`, or
- three of four reviewers must return `approve` when only four reviewers are
  active, and
- no reviewer may report a blocking issue.

If the design does not pass, the Lead Design Agent synthesizes the feedback,
records accepted and rejected changes, creates the next design revision, and
starts another review round. When quorum passes, the Lead Design Agent creates a
development handoff:

```text
Design Review Result: Approved
Review round: 3
Approval count: 4 of 5
Blocking issues: 0

Development handoff:
- final design packet reference
- reviewer feedback summary
- accepted change log
- unresolved non-blocking risks
- implementation task outline
- QA checklist
- acceptance criteria
```

## Current Capability Map

| Scenario requirement | Current support | Codebase used | Implementable now |
| --- | --- | --- | --- |
| React admin setup for workflow authoring | The primary browser path is `/admin/app/workflows`; admins can author guided workflow drafts with roles, sub-agent roles, contracts, graph nodes, joins, validation, publish readiness, and revision history | `admin/workflow_builder.py`, `api/schemas/workflow_registry.py`, `frontend/admin/src/components/workflows/*` | Yes |
| Lead and reviewer role modeling | Workflow roles support `agent` and `subagent` role kinds, prompt/profile references, output contracts, skill bindings, handoff notes, and graph node references | `api/schemas/workflow_registry.py` | Yes |
| Parallel reviewer fan-out | Graph execution schedules ready role nodes in parallel waves with durable run steps and timeline events | `runtime/orchestration/graph_execution.py`, `workers/orchestration.py` | Yes for deterministic role-node QA |
| Three-of-four or four-of-five quorum | Join policies support strategy `quorum` with `quorum_count`; validation checks positive quorum values | `admin/workflow_registry/validation.py`, `runtime/orchestration/graph_execution.py` | Yes |
| Manual resolution when reviewers disagree | Join policies can use `manual_resolution`, and approval nodes can pause workflow execution | `api/schemas/workflow_registry.py`, `runtime/orchestration/graph_execution.py` | Yes |
| Structured design and review contracts | Workflow draft documents support JSON-schema-backed contracts for workflow input, handoff, artifact, approval, failure, and data contracts | `api/schemas/workflow_registry.py` | Yes |
| Prompt and runtime profile governance | Prompt, profile, provider, routing, policy, and provenance surfaces exist in the governance workspace | `prompts/*`, `agents/*`, `model_providers/*`, `frontend/admin/src/components/governance/*` | Yes |
| Live model-backed reviewer agents | Model provider gateway and live credential resolution exist, but graph role nodes default to deterministic execution | `model_providers/gateway.py`, `model_providers/secrets.py`, `runtime/orchestration/graph_roles.py` | Needs development |
| Durable design review artifacts | Runtime step outputs and artifact references exist, but there is no purpose-built design review table or service yet | `runtime/orchestration/*`, `testing/agent_bench/*`, `storage/*` | Partially |
| Iteration loop until quorum | One review round can run as an acyclic graph. Repeated rounds should be coordinated as separate workflow runs because graph execution asserts acyclic plans | `runtime/orchestration/graph_execution.py` | Needs coordinator development |
| Review evidence and QA gates | Test bench suites, runs, artifacts, and publish gate evidence are available and can validate the review workflow itself | `testing/agent_bench/*`, `admin/workflow_registry/publish_gate.py`, `api/routers/admin_agent_tests.py` | Yes |
| Browser review surface | Existing workflow builder, governance, test bench, operations, and migration workspaces can administer the pieces; a dedicated design-review workspace would be additive | `frontend/admin/src/*`, `api/routers/admin_react.py` | Partially |
| Redaction and tenant isolation | Existing platform conventions require safe summaries, artifact references, tenant guards, and no raw prompts, completions, secrets, connector payloads, or unauthorized tenant data in UI or QA artifacts | `auth/*`, `audit/*`, `model_providers/redaction.py`, `runtime/orchestration/graph_redaction.py` | Yes |

## Recommended Workflow Shape

One workflow run should represent one review round:

```mermaid
flowchart TD
    A["User design request"] --> B["Lead Design Agent creates design packet"]
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
    D --> E["Lead Feedback Synthesizer"]
    E --> F{"Quorum reached?"}
    F -->|"Yes"| G["Development Handoff"]
    F -->|"No"| H["Record revision request"]
```

The review-round coordinator owns the cross-round loop:

```mermaid
flowchart TD
    A["Create design review session"] --> B["Launch review round 1"]
    B --> C{"Quorum reached?"}
    C -->|"Yes"| D["Mark session approved"]
    C -->|"No"| E["Persist feedback and next revision prompt"]
    E --> F["Launch next review round"]
    F --> C
```

This avoids cyclic graph execution while still delivering the user-visible
behavior: keep iterating until the reviewer quorum approves the design.

## Suggested Workflow Draft Document

The workflow draft should use explicit contracts and role keys. This is an
illustrative skeleton, not a complete import payload:

```json
{
  "workflow_key": "design-reviewer-council",
  "display_name": "Design Reviewer Council",
  "workflow_kind": "main_workflow",
  "entry_node_key": "lead-design",
  "roles": [
    {
      "role_key": "lead-designer",
      "display_name": "Lead Design Agent",
      "role_kind": "agent",
      "purpose": "Create and revise design packets from user requests and reviewer feedback.",
      "input_contract_key": "design-request",
      "output_contract_key": "design-packet",
      "graph_node_keys": ["lead-design", "lead-synthesis"]
    },
    {
      "role_key": "product-reviewer",
      "display_name": "Product Fit Reviewer",
      "role_kind": "subagent",
      "purpose": "Review whether the design solves the right user problem.",
      "input_contract_key": "design-packet",
      "output_contract_key": "reviewer-verdict",
      "graph_node_keys": ["product-review"]
    },
    {
      "role_key": "ux-reviewer",
      "display_name": "UX And Interaction Reviewer",
      "role_kind": "subagent",
      "purpose": "Review flows, interaction states, and task efficiency.",
      "input_contract_key": "design-packet",
      "output_contract_key": "reviewer-verdict",
      "graph_node_keys": ["ux-review"]
    },
    {
      "role_key": "visual-reviewer",
      "display_name": "Visual And Design System Reviewer",
      "role_kind": "subagent",
      "purpose": "Review hierarchy, density, components, and design-system fit.",
      "input_contract_key": "design-packet",
      "output_contract_key": "reviewer-verdict",
      "graph_node_keys": ["visual-review"]
    },
    {
      "role_key": "accessibility-reviewer",
      "display_name": "Accessibility Reviewer",
      "role_kind": "subagent",
      "purpose": "Review keyboard, focus, labels, contrast, motion, and screen-reader support.",
      "input_contract_key": "design-packet",
      "output_contract_key": "reviewer-verdict",
      "graph_node_keys": ["accessibility-review"]
    },
    {
      "role_key": "engineering-reviewer",
      "display_name": "Engineering And API Reviewer",
      "role_kind": "subagent",
      "purpose": "Review backend contracts, permissions, persistence, reliability, and testability.",
      "input_contract_key": "design-packet",
      "output_contract_key": "reviewer-verdict",
      "graph_node_keys": ["engineering-review"]
    }
  ],
  "join_policies": [
    {
      "join_policy_key": "reviewer-quorum-4-of-5",
      "strategy": "quorum",
      "quorum_count": 4,
      "failure_behavior": "manual_resolution",
      "output_merge_contract_key": "review-panel-summary"
    }
  ],
  "nodes": [
    {
      "node_key": "lead-design",
      "node_type": "role",
      "display_name": "Create Design Packet",
      "role_key": "lead-designer"
    },
    {
      "node_key": "product-review",
      "node_type": "role",
      "display_name": "Product Review",
      "role_key": "product-reviewer"
    },
    {
      "node_key": "ux-review",
      "node_type": "role",
      "display_name": "UX Review",
      "role_key": "ux-reviewer"
    },
    {
      "node_key": "visual-review",
      "node_type": "role",
      "display_name": "Visual Review",
      "role_key": "visual-reviewer"
    },
    {
      "node_key": "accessibility-review",
      "node_type": "role",
      "display_name": "Accessibility Review",
      "role_key": "accessibility-reviewer"
    },
    {
      "node_key": "engineering-review",
      "node_type": "role",
      "display_name": "Engineering Review",
      "role_key": "engineering-reviewer"
    },
    {
      "node_key": "review-quorum",
      "node_type": "join",
      "display_name": "Evaluate Reviewer Quorum",
      "join_policy_key": "reviewer-quorum-4-of-5"
    },
    {
      "node_key": "lead-synthesis",
      "node_type": "role",
      "display_name": "Synthesize Review Feedback",
      "role_key": "lead-designer"
    },
    {
      "node_key": "development-handoff",
      "node_type": "terminal",
      "display_name": "Development Handoff"
    }
  ]
}
```

For a four-reviewer panel, use the same graph shape with one reviewer omitted
and set the quorum policy to:

```json
{
  "join_policy_key": "reviewer-quorum-3-of-4",
  "strategy": "quorum",
  "quorum_count": 3,
  "failure_behavior": "manual_resolution",
  "output_merge_contract_key": "review-panel-summary"
}
```

## Proposed Data Model Additions

If this becomes a first-class product feature, add a small design-review domain
instead of storing everything only in runtime step output refs.

Suggested models:

| Model | Purpose |
| --- | --- |
| `DesignReviewSession` | Tenant-scoped session created from the user's build prompt. Tracks status, active revision, quorum rule, owner, and final handoff reference. |
| `DesignRevision` | Immutable design packet revision with safe summary, artifact reference, previous revision link, and author role. |
| `DesignReviewRound` | One acyclic workflow run against one design revision. Tracks reviewer count, quorum target, status, started/completed timestamps, and runtime run id. |
| `DesignReviewerAssignment` | Reviewer role assignment for a round, including lens, prompt/profile references, expected output contract, and enabled status. |
| `DesignReviewerVerdict` | Structured reviewer result with verdict, score, blocking issue count, safe feedback summary, artifact reference, and output digest. |
| `DesignQuorumDecision` | Durable aggregate decision with approval count, blocker count, pass/fail state, policy version, and next action. |
| `DesignDevelopmentHandoff` | Approved design output with implementation outline, QA checklist, acceptance criteria, safe references, and audit metadata. |

All models should be tenant-scoped, audit-safe, and immutable where they
represent reviewer evidence or design revisions.

## Step-By-Step Setup With Current Code

### Step 1 - Prepare The Local Environment

From the repository root:

```bash
uv sync
cp .env.example .env
cd frontend/admin
npm install
npm run build
cd ../..
```

Use local-principal auth for deterministic review:

```bash
APP_ENV=local
AUTH_MODE=local_principal
DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/multi_agent_platform
LOCAL_PRINCIPAL_CATALOG_JSON=<copy-current-.env.example-value>
```

Codebase used by this step:

- `config/settings.py`
- `.env.example`
- `compose.yaml`
- `auth/local_principals.py`

Current-code review: this step is fully supported.

### Step 2 - Start PostgreSQL And Apply Migrations

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

Create or confirm the Acme tenant used by the example:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform <<'SQL'
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  'acme',
  'Acme',
  'active',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING;
SQL
```

Codebase used by this step:

- `alembic/versions/*.py`
- `db/models/*`
- `db/session.py`

Current-code review: this step is fully supported.

### Step 3 - Start The API And Optional Worker

Terminal 1:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, optional for DB-backed orchestration work:

```bash
uv run python -m multi_agent_platform.workers.main
```

Open the React admin console:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Use `platform-admin` for platform setup and `tenant-admin-acme` for tenant
workflow setup.

Codebase used by this step:

- `api/main.py`
- `api/routers/admin_react.py`
- `workers/main.py`
- `workers/orchestration.py`
- `runtime/orchestration/graph_execution.py`

Current-code review: API startup and deterministic graph execution are
supported.

### Step 4 - Configure Provider, Prompt, And Profile Governance

Open:

```text
http://127.0.0.1:8000/admin/app/governance
```

Create prompt and profile entries for:

1. `design-lead`
2. `product-fit-reviewer`
3. `ux-interaction-reviewer`
4. `visual-design-system-reviewer`
5. `accessibility-reviewer`
6. `engineering-api-reviewer`
7. `feedback-synthesizer`

Recommended prompt responsibilities:

- Lead Design Agent: create and revise design packets from the user build
  prompt and prior round feedback.
- Product Fit Reviewer: check user value, scope, prioritization, and missing
  workflows.
- UX And Interaction Reviewer: check task flow, navigation, state coverage, and
  recovery paths.
- Visual And Design System Reviewer: check hierarchy, density, component
  choices, responsiveness, and local design-system fit.
- Accessibility Reviewer: check keyboard paths, focus management, labels,
  contrast, motion, screen reader support, and accessible alternatives.
- Engineering And API Reviewer: check contracts, persistence, permissions,
  tenant isolation, async states, performance, and testability.
- Feedback Synthesizer: merge reviewer feedback, resolve conflicts, record
  accepted/rejected changes, and produce either a revision instruction or final
  handoff.

Codebase used by this step:

- `prompts/service.py`
- `prompts/validation.py`
- `prompts/preview.py`
- `agents/*`
- `model_providers/*`
- `api/routers/admin_prompts.py`
- `api/routers/admin_agent_profiles.py`

Current-code review: prompt/profile/provider governance is supported. Live
model execution for graph role nodes requires the additional model-backed role
executor described below.

### Step 5 - Create The Workflow Draft

Open:

```text
http://127.0.0.1:8000/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111
```

Create a tenant workflow draft named `Design Reviewer Council`.

Recommended draft structure:

- one lead role node
- four or five reviewer sub-agent role nodes
- one quorum join node
- one feedback synthesis role node
- one terminal development handoff node
- a `quorum` join policy with `quorum_count` set to `3` or `4`
- explicit JSON contracts for user prompt, design packet, reviewer verdict,
  review summary, revision request, and final handoff
- a required test suite requirement before publication

Codebase used by this step:

- `api/schemas/workflow_registry.py`
- `admin/workflow_registry/validation.py`
- `admin/workflow_builder.py`
- `frontend/admin/src/components/workflows/*`

Current-code review: the workflow draft can be modeled and validated now.

### Step 6 - Add Test Bench Evidence

Open:

```text
http://127.0.0.1:8000/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111
```

Create a test suite for the current workflow draft revision.

Recommended deterministic test cases:

1. Five reviewers, four approvals, zero blocking issues, expected result
   `approved`.
2. Five reviewers, three approvals, zero blocking issues, expected result
   `revision_required`.
3. Four reviewers, three approvals, zero blocking issues, expected result
   `approved`.
4. Five reviewers, four approvals, one blocking issue, expected result
   `revision_required`.
5. One reviewer fails with a deterministic role error and the join uses
   `failure_behavior=manual_resolution`, expected result `paused`.
6. Cross-tenant access attempt, expected result `denied`.

Codebase used by this step:

- `testing/agent_bench/*`
- `api/routers/admin_agent_tests.py`
- `frontend/admin/src/components/testBench/*`
- `admin/workflow_registry/publish_gate.py`

Current-code review: deterministic test-bench authoring and publish-gate
evidence are supported.

### Step 7 - Publish The Workflow For Deterministic QA

From the workflow builder:

1. Run validation.
2. Confirm the quorum join policy and contracts are valid.
3. Confirm the required test suite evidence targets the current draft revision.
4. Open publish review.
5. Publish only after required evidence is passing.

Codebase used by this step:

- `admin/workflow_registry/service.py`
- `admin/workflow_registry/publish_gate.py`
- `admin/workflow_registry/compiler.py`
- `frontend/admin/src/components/workflows/*`

Current-code review: publish readiness and immutable bundle summaries are
supported.

### Step 8 - Develop The Production Review Loop

Add a domain coordinator that owns repeated rounds:

```text
DesignReviewCoordinator.start_session(user_prompt)
DesignReviewCoordinator.launch_round(session_id, design_revision_id)
DesignReviewCoordinator.record_round_result(round_id, runtime_run_id)
DesignReviewCoordinator.evaluate_quorum(round_id)
DesignReviewCoordinator.request_revision(session_id, feedback_summary)
DesignReviewCoordinator.approve_for_development(session_id)
```

Recommended source locations:

- `src/multi_agent_platform/admin/design_review/`
- `src/multi_agent_platform/api/schemas/design_review.py`
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `src/multi_agent_platform/db/models/design_review.py`
- `src/multi_agent_platform/db/repositories/design_review.py`
- `frontend/admin/src/components/designReview/`
- `tests/unit/admin/test_design_review_service.py`
- `tests/integration/test_admin_design_review_routes.py`
- `tests/contract/test_admin_design_review_contract.py`

Current-code review: this is the primary new feature work.

### Step 9 - Develop A Model-Backed Role Node Executor

The production path needs a role executor that:

1. Loads the role's prompt/profile/provider references.
2. Builds a safe model input from the design packet and upstream summaries.
3. Calls `ModelGateway`.
4. Validates the structured output against the role's output contract.
5. Stores raw or large payloads only as governed artifacts when allowed.
6. Returns safe summaries, digests, redacted evidence, and usage metadata.

Recommended source locations:

- `src/multi_agent_platform/runtime/orchestration/model_role_executor.py`
- `src/multi_agent_platform/runtime/orchestration/contract_validation.py`
- `tests/unit/runtime/test_model_role_executor.py`
- `tests/integration/test_graph_model_role_execution.py`

Current-code review: `ModelGateway` and credential resolution exist. The graph
role executor defaults to deterministic output, so this production executor is
new work.

## Quorum Policy

Recommended policy:

```text
approval_count >= quorum_count
blocking_issue_count == 0
redaction_status == "safe"
contract_validation_status == "passed"
```

Recommended verdict values:

- `approve`
- `approve_with_notes`
- `request_changes`
- `block`

For quorum counting, treat `approve` as approval. Treat
`approve_with_notes` as approval only if it has no blocking issues and all
approval conditions are non-blocking.

Recommended next-action mapping:

| Condition | Next action |
| --- | --- |
| Quorum reached and no blockers | Create development handoff |
| Quorum reached with any blocker | Request revision |
| Quorum not reached and feedback is clear | Request revision |
| Reviewer outputs conflict or policy cannot decide | Pause for manual resolution |
| Reviewer failed due to runtime or redaction error | Pause or request retry based on reliability policy |

## QA And Validation Plan

Use the same quality posture as the existing Spec Kit features.

Backend validation:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/admin/test_design_review_service.py
uv run pytest tests/unit/runtime/test_model_role_executor.py
uv run pytest tests/integration/test_admin_design_review_routes.py
uv run pytest tests/contract/test_admin_design_review_contract.py
```

Full validation:

```bash
uv run pytest
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Frontend validation if a dedicated React workspace is added:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Browser validation should cover:

- local-principal login
- tenant-scoped design review session creation
- prompt/profile/provider readiness
- five-reviewer round
- four-reviewer round
- quorum success
- quorum failure
- blocking issue override
- manual resolution pause
- revision round launch
- approved development handoff
- cross-tenant denial
- redaction sweep for raw prompts, completions, secrets, credential values,
  private payloads, memory contents, unauthorized run data, and raw tool payloads

## Development Recommendation

Build this as an additive feature on top of the existing workflow registry,
graph execution, governance, and test bench capabilities.

The safest first milestone is:

1. Provide a reusable `Design Reviewer Council` workflow template.
2. Add deterministic tests that prove reviewer fan-out, quorum joins, blocking
   issue handling, manual resolution, and development handoff.
3. Add the `DesignReviewCoordinator` to persist sessions and launch repeated
   acyclic review-round runs.
4. Add the model-backed role executor behind an explicit safe execution mode.
5. Add a React design-review workspace only after the backend contracts and
   deterministic QA path are stable.

This matches the project's current architecture: contract-first, tenant-scoped,
redaction-safe, auditable, deterministic in local QA, and capable of later
switching to governed live model calls when provider policy allows it.
