# Design Reviewer Workflow Example

Review date: 2026-05-09

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

The current product now supports the Design Reviewer Council as a first-class,
live-data-backed scenario. The safest local path remains deterministic or
mocked model-backed QA, but the durable domain, coordinator loop, Admin
workspace, template installer, publish-gate evidence, workflow graph viewer,
runtime graph, and interaction replay evidence are implemented.

Current support is strongest for:

- workflow drafting through the React workflow builder
- agent and sub-agent role modeling
- parallel role-node execution
- quorum joins such as three of four or four of five reviewers
- deterministic local and CI execution
- prompt/profile/provider governance
- safe audit, redaction, artifact references, and test-bench evidence
- manual approval pauses when a design needs human resolution
- live repository/service-backed Admin setup views, backend-owned provenance,
  truthful empty states, live-only route guardrails, and product-facing Admin
  terminology
- purpose-built design review domain records for sessions, immutable
  revisions, rounds, assignments, verdicts, quorum decisions, manual decisions,
  and handoff references
- governed model-backed role-node execution behind explicit execution mode,
  prompt/profile/provider pins, credential readiness, policy checks, contract
  validation, and redaction
- a review-round coordinator that launches successive acyclic workflow runs
  until quorum passes, revision is required, or manual resolution is needed
- a live Admin workspace for session creation, launch, verdict/quorum review,
  manual-resolution actions, reusable template readiness, and handoff
  inspection
- design-time, published-version, runtime, and replay graph evidence for
  inspecting agent communication without raw payloads

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
- `specs/048-live-data-inventory-and-mock-guardrails/plan.md`
- `specs/049-react-contract-provenance-and-sample-route-retirement/plan.md`
- `specs/050-workflow-react-live-data/plan.md`
- `specs/051-governance-react-live-data/plan.md`
- `specs/052-skill-lifecycle-react-live-data/plan.md`
- `specs/053-test-bench-react-live-data/plan.md`
- `specs/054-membership-and-access-react-live-data/plan.md`
- `specs/055-channels-telegram-briefing-react-live-data/plan.md`
- `specs/056-usage-react-live-data/plan.md`
- `specs/057-operations-and-run-debug-react-live-data/plan.md`
- `specs/058-live-only-ui-decommission-gate/plan.md`
- `specs/059-admin-ui-transitional-react-label-removal/plan.md`
- `specs/060-design-review-domain-foundation/plan.md`
- `specs/061-model-backed-graph-role-executor/plan.md`
- `specs/062-design-review-coordinator-and-iteration-loop/plan.md`
- `specs/063-admin-design-review-workspace/plan.md`
- `specs/064-design-reviewer-template-test-bench-and-publish-gates/plan.md`
- `specs/065-agent-communication-graph-contracts-and-projections/plan.md`
- `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/plan.md`
- `specs/067-runtime-agent-communication-graph-for-runs/plan.md`
- `specs/068-durable-agent-interaction-evidence-and-replay-graph/plan.md`
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
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `src/multi_agent_platform/api/schemas/design_review.py`
- `src/multi_agent_platform/api/schemas/admin_design_review_workspace.py`
- `src/multi_agent_platform/api/schemas/admin_agent_graph.py`
- `src/multi_agent_platform/admin/design_review/*`
- `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- `src/multi_agent_platform/operations/runtime_agent_graph.py`
- `src/multi_agent_platform/runtime/orchestration/interaction_evidence.py`
- `src/multi_agent_platform/db/models/design_review.py`
- `src/multi_agent_platform/db/repositories/design_review.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `frontend/admin/src/components/workflows/*`
- `frontend/admin/src/components/governance/*`
- `frontend/admin/src/components/testBench/*`
- `frontend/admin/src/components/designReviews/*`
- `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- `frontend/admin/src/components/workbench/*`

Specs `048` through `059` make the browser workspaces live-data guarded and
product-facing. Specs `060` through `068` add the Design Review domain,
coordinator, workspace, template, design-time graph contracts, graph viewer,
runtime graph, and durable interaction replay evidence. Production Admin routes
should not invent workflows, reviewers, sessions, verdicts, test runs, usage
rows, audit references, artifact references, graph nodes, replay rows, or
mutation success. They should return live durable data, allowed computed
metadata, or truthful empty/denied/unavailable states with backend-owned
provenance. Visible browser copy should say "Admin" or domain-specific terms;
implementation framework labels should stay out of product-facing setup copy.

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
| Admin setup for workflow authoring | The primary browser path is `/admin/app/workflows`; admins can author guided workflow drafts with roles, sub-agent roles, contracts, graph nodes, joins, validation, publish readiness, and revision history from live workflow records | `admin/workflow_builder.py`, `admin/workflow_registry/*`, `api/schemas/workflow_registry.py`, `frontend/admin/src/components/workflows/*` | Yes |
| Lead and reviewer role modeling | Workflow roles support `agent` and `subagent` role kinds, prompt/profile references, output contracts, skill bindings, handoff notes, and graph node references | `api/schemas/workflow_registry.py` | Yes |
| Parallel reviewer fan-out | Graph execution schedules ready role nodes in parallel waves with durable run steps and timeline events | `runtime/orchestration/graph_execution.py`, `workers/orchestration.py` | Yes for deterministic role-node QA |
| Three-of-four or four-of-five quorum | Join policies support strategy `quorum` with `quorum_count`; validation checks positive quorum values | `admin/workflow_registry/validation.py`, `runtime/orchestration/graph_execution.py` | Yes |
| Manual resolution when reviewers disagree | Join policies can use `manual_resolution`, and approval nodes can pause workflow execution | `api/schemas/workflow_registry.py`, `runtime/orchestration/graph_execution.py` | Yes |
| Structured design and review contracts | Workflow draft documents support JSON-schema-backed contracts for workflow input, handoff, artifact, approval, failure, and data contracts | `api/schemas/workflow_registry.py` | Yes |
| Prompt and runtime profile governance | Prompt, profile, provider, routing, policy, gateway diagnostic, and provenance surfaces exist as live governance projections | `admin/governance.py`, `prompts/*`, `agents/*`, `model_providers/*`, `frontend/admin/src/components/governance/*` | Yes |
| Live model-backed reviewer agents | Role nodes can opt into governed model-backed execution through ModelGateway when execution mode, tenant scope, prompt/profile/provider pins, credential readiness, policy, redaction, and output-contract validation pass; deterministic mode remains the local QA default | `model_providers/gateway.py`, `model_providers/secrets.py`, `runtime/orchestration/graph_roles.py`, `runtime/orchestration/graph_execution.py` | Yes, with governed or mocked-safe execution mode |
| Durable design review artifacts | Purpose-built design review tables and services persist safe sessions, revisions, rounds, assignments, verdicts, quorum decisions, manual decisions, and handoff references | `admin/design_review/*`, `db/models/design_review.py`, `db/repositories/design_review.py`, `api/routers/admin_design_review.py` | Yes |
| Iteration loop until quorum | The coordinator launches one acyclic runtime run per review round, evaluates zero-blocker quorum, creates the next immutable revision or handoff, and pauses for durable manual resolution when needed | `admin/design_review/coordinator.py`, `runtime/orchestration/graph_execution.py`, `db/repositories/runtime_orchestration.py` | Yes |
| Review evidence and QA gates | Test bench suites, cases, runs, artifacts, and publish gate evidence are live repository-backed and can validate the review workflow itself | `testing/agent_bench/*`, `testing/agent_bench/react_test_bench.py`, `admin/workflow_registry/publish_gate.py`, `api/routers/admin_agent_tests.py` | Yes |
| Browser review surface | `/admin/app/design-reviews` administers sessions, template readiness, launch, revisions, rounds, verdicts, quorum, manual decisions, and handoffs with live-data provenance | `admin/design_review/react_workspace.py`, `frontend/admin/src/components/designReviews/*`, `api/routers/admin_react.py` | Yes |
| Workflow communication graph | Draft and published workflow pages render backend-owned Agent Communication Graph contracts with safe node/edge categories, references, validation badges, and keyboard-readable lists | `admin/workflow_registry/agent_graph.py`, `api/schemas/admin_agent_graph.py`, `frontend/admin/src/components/workflows/AgentGraphPanel.tsx` | Yes |
| Runtime graph and replay | Operations run inspection overlays published topology with run steps, timeline, status, handoff/tool/gateway evidence, and durable interaction replay references | `operations/runtime_agent_graph.py`, `runtime/orchestration/interaction_evidence.py`, `frontend/admin/src/components/workbench/*` | Yes |
| Redaction and tenant isolation | Existing platform conventions require safe summaries, artifact references, tenant guards, and no raw prompts, completions, secrets, connector payloads, or unauthorized tenant data in UI or QA artifacts | `auth/*`, `audit/*`, `model_providers/redaction.py`, `runtime/orchestration/graph_redaction.py` | Yes |
| Live-data and terminology guardrails | Production Admin routes must not expose deterministic reviewer/demo records, sample route data, or implementation-framework labels as product copy; guardrail checks cover source, built assets, route responses, visible copy, empty states, and seeded states | `api/routers/admin_react.py`, `tests/unit/admin/test_transitional_label_scanner.py`, `tests/integration/api/test_admin_live_data_inventory_routes.py` | Yes |
| Browser routing | Admin workspaces are the canonical browser interface; old admin and run links must redirect or alias into Admin without rendering server templates | `api/routers/admin_react.py`, `api/routers/auth.py`, `api/routers/web_run_ui.py`, `frontend/admin/src/App.tsx` | Yes |

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

## Implemented Data Model

The scenario now has a dedicated design-review domain instead of storing review
state only in runtime step output references.

Implemented models:

| Model | Purpose |
| --- | --- |
| `DesignReviewSession` | Tenant-scoped session created from the user's build prompt. Tracks status, active revision, quorum rule, owner, and final handoff reference. |
| `DesignRevision` | Immutable design packet revision with safe summary, artifact reference, previous revision link, and author role. |
| `DesignReviewRound` | One acyclic workflow run against one design revision. Tracks reviewer count, quorum target, status, started/completed timestamps, and runtime run id. |
| `DesignReviewerAssignment` | Reviewer role assignment for a round, including lens, prompt/profile references, expected output contract, and enabled status. |
| `DesignReviewerVerdict` | Structured reviewer result with verdict, score, blocking issue count, safe feedback summary, artifact reference, and output digest. |
| `DesignQuorumDecision` | Durable aggregate decision with approval count, blocker count, pass/fail state, policy version, and next action. |
| `DesignManualDecision` | Append-only tenant admin decision for revise, approve-exception, retry, or cancel while preserving safe rationale and idempotency. |
| `DesignDevelopmentHandoff` | Approved design output with implementation outline, QA checklist, acceptance criteria, safe references, and audit metadata. |

All records are tenant-scoped and audit-safe. Revisions, reviewer verdicts,
quorum decisions, and handoffs are immutable or append-only evidence, while
session status is updated only through domain services and coordinator actions.

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

Open the Admin console:

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

### Browser Setup Page Walkthrough

The screenshots in this section were captured from the running local server on
May 8-9, 2026 at desktop viewports. Open the image directly if your Markdown
viewer scales it down. The design reviewer setup flow uses `tenant-admin-acme`
for tenant-scoped pages unless a step explicitly says otherwise.

#### Local Login

![Local login for the Design Reviewer Council setup](docs/assets/design-reviewer-example/admin-ui/local-login-wide.png)

Use this page in Step 3 to enter the Admin console.

1. Open `/auth/local-login?redirect_to=/admin/app`.
2. Choose `Platform Admin` only when you need platform-wide governance or
   diagnostic checks.
3. Choose `Acme Tenant Admin` for the Design Reviewer Council workflow setup.
4. Confirm the browser redirects to `/admin/app`.
5. If you need to change principals, use Log off in the top-right corner and
   return to this page.

Visible elements:

- Principal cards show the local display name, catalog key, and role badges.
- `Sign In` stores the chosen local principal in the browser cookie and sends
  the browser to the requested Admin route.

#### Console Home

![Console home for the Design Reviewer Council setup](docs/assets/design-reviewer-example/admin-ui/admin-home-wide.png)

Use this page after login to confirm scope and choose the next setup area.

1. Confirm the top bar shows `tenant-admin-acme`, system health `Ready`, and
   active scope `Acme`.
2. Use Refresh to reload backend-owned notices, metrics, and destination links.
3. Review Current notices. A clean local setup should not need a blocking
   notice before the design reviewer setup starts.
4. Use Start here for common destinations such as Review workflows, Check
   routing, Open test bench, Manage access, and Review usage.
5. Use Authorized destinations to confirm which workspaces the current
   principal can open.
6. Use the left navigation for the rest of the setup: Workflow Registry,
   Configuration, Agent Tests, Usage Analytics, Membership Administration, Run
   Search, and Reliability pages.

Visible elements:

- The left navigation groups all Admin workspaces by area.
- The top bar exposes the command/search control, active principal, scope, and
  logoff action.
- Summary metrics, Current notices, Start here, and Authorized destinations
  are live projections from the Admin home endpoint.

#### Governance Setup

![Governance setup page for Design Reviewer providers, prompts, profiles, and routing](docs/assets/design-reviewer-example/admin-ui/governance-wide.png)

Use this page for Step 4.

1. Open `/admin/app/governance?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the Governance panel appears and the active scope is Acme.
3. Use Setup to review readiness counts for provider connections, prompt
   lineages, and runtime profiles.
4. Use Providers to create or inspect the model provider connection for
   reviewer roles. Store credential references only; never paste raw API keys
   into visible fields.
5. Use Prompts to create and publish the lead, reviewer, and feedback
   synthesizer prompt versions from Step 4.
6. Use Profiles to create and activate runtime profiles for the lead designer,
   each reviewer, and the synthesizer.
7. Use Routing to preview read-only routing behavior for the profiles.
8. Use Provenance to inspect run provenance after tests or workflow runs exist.
9. Treat empty panels as truthful setup state: the page is saying no durable
   records exist yet for this scope.

Visible elements:

- The section tabs switch between Setup, Providers, Prompts, Profiles, Routing,
  and Provenance content.
- Readiness summary lists what backend records are present or missing.
- Provider, prompt, and profile panels expose safe mutation buttons only when
  the current principal is authorized.
- Provenance cards show redaction-safe provider, prompt, profile, credential,
  and audit evidence after runtime activity exists.

#### Workflow Setup

![Workflow setup page for the Design Reviewer Council graph](docs/assets/design-reviewer-example/admin-ui/workflows-wide.png)

Use this page for Steps 5 and 7.

1. Open `/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the Workflow Registry and Workflow builder panels are visible.
3. Use Create draft to start the `Design Reviewer Council` workflow draft.
4. Set the draft display name, description, tenant scope, workflow kind, and
   entry node described in Step 5.
5. Add the lead role, four or five reviewer sub-agent roles, quorum join,
   feedback synthesis role, terminal handoff node, edges, and JSON contracts.
6. Pin the prompt and runtime profile references created from Governance.
7. Save the draft and review the graph preview, validation panel, JSON
   inspector, sharing state, and revision history.
8. Run validation and resolve blocking findings.
9. After Step 6 creates current passing test evidence, return here, review the
   publish gate, and publish.

Visible elements:

- Workflow Registry lists existing live workflow records for the active scope.
- Create workflow starts a backend-owned draft; the empty state appears when no
  active draft exists yet.
- Draft forms own the safe editable metadata, selected prompt/profile
  references, and join policy controls once a draft is available.
- Graph, validation, publish, sharing, revisions, and JSON inspector panels
  explain whether the draft is ready to become an immutable published bundle.

#### Workflow Agent Graph

![Workflow Agent Graph for the Design Reviewer Council graph](docs/assets/design-reviewer-example/admin-ui/workflow-agent-graph-wide.png)

Use this graph panel during Steps 5 and 7 to verify the council topology before
publication.

1. Open a workflow draft or published version from `/admin/app/workflows`.
2. Confirm the Agent Graph panel is present when backend graph data is
   available.
3. Verify the visual graph includes coordinator, reviewer/sub-agent, tool,
   join, approval, handoff, and terminal nodes as expected for the draft.
4. Select a node such as Specialist and verify the detail panel shows category,
   status, references, badges, and safe summary text.
5. Select an edge and verify labels such as delegates, joins, transitions, uses
   tool, or hands off.
6. Use Node list and Edge list to confirm keyboard-readable graph coverage.

Visible elements:

- Projected graph canvas with stable backend-owned nodes and edges.
- Selected node or edge detail panel.
- Node list and Edge list alternatives.
- Safe reference summaries for roles, contracts, prompts, profiles, providers,
  skills, and validation badges when available.

#### Design Reviews Workspace

![Design Reviews workspace for the Design Reviewer Council](docs/assets/design-reviewer-example/admin-ui/design-reviews-wide.png)

Use this page for session creation, launch, review status, manual resolution,
and final handoff inspection.

1. Open `/admin/app/design-reviews?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the left navigation highlights Design Reviews under Workflows.
3. Review summary cards for Sessions, In review, Needs decision, and Approved.
4. Use Create request to start a session with a safe request summary, quorum
   policy, and optional authorized published workflow.
5. Select a session from History to inspect revisions, rounds, verdict
   summaries, quorum decisions, manual decisions, and handoff state.
6. Use Launch review only when the selected session has an authorized published
   workflow bundle.
7. Use manual-resolution controls only when the backend reports the session is
   paused for a human decision.

Visible elements:

- Live tenant-scoped session counters.
- Create request form.
- Session history with backend-owned status and revision state.
- Selected-session detail with safe evidence only.

#### Council Template Readiness

![Design Reviewer template readiness](docs/assets/design-reviewer-example/admin-ui/design-review-template-wide.png)

Use this state before publishing a reusable council workflow.

1. From `/admin/app/design-reviews`, run Install council template if the
   template is not installed.
2. Confirm the Template card reports not installed, pending, stale, ready, or
   published from live backend state.
3. When ready, confirm the safe summary says the council template has current
   required evidence.
4. Open the related workflow draft in `/admin/app/workflows` and inspect the
   publish gate before publishing.
5. Treat empty session rows as truthful: template readiness does not invent
   design review sessions, reviewer rows, quorum decisions, or handoffs.

Visible elements:

- Template readiness card.
- Council template summary.
- Required evidence and publish-gate state.
- No sample session records when the tenant has no sessions.

#### Agent Tests Setup

![Agent Tests setup page for Design Reviewer publish-gate evidence](docs/assets/design-reviewer-example/admin-ui/test-bench-wide.png)

Use this page for Step 6.

1. Open `/admin/app/test-bench?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the Agent Tests page and Test Bench panel are visible.
3. Create a `Design Reviewer Council` suite for the current workflow draft
   revision.
4. Add the deterministic approval, revision-required, blocking-issue,
   manual-resolution, and cross-tenant-denial cases from Step 6.
5. Target the current `workflow_draft_id` and current
   `workflow_draft_revision_id`.
6. Launch the suite in a safe deterministic mode.
7. Review backend-owned status, recent runs, pass/fail diagnostics, traces,
   artifacts, publish-gate evidence, and audit timeline after a run exists.
8. Return to `/admin/app/workflows` and confirm the publish gate sees current
   passing evidence for the draft revision.

Visible elements:

- The section tabs separate Suites, Runs, Diagnostics, Gates, and Audit.
- Release confidence summary cards report suite, run, and gate readiness.
- Suite authoring controls create or update suites and cases when records are
  present and the principal is authorized.
- Run launch, progress, run detail, trace/artifact, and publish-gate panels are
  live evidence surfaces; empty state means no durable test records exist yet.

#### Membership Administration

![Membership Administration page for Design Reviewer access setup](docs/assets/design-reviewer-example/admin-ui/memberships-wide.png)

Use this page when setup is blocked by principal, role, or tenant-access
problems.

1. Open `/admin/app/memberships?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the active scope is Acme.
3. Use Users to inspect visible principals and tenant memberships.
4. Use Invite users if a new tenant user needs access to design review setup.
5. Use Link identity when an external identity must be associated with a
   principal.
6. Use Assign roles to grant `tenant_user` or `tenant_admin` when policy allows
   it.
7. Use status controls to suspend, activate, or update memberships only when
   authorized.
8. Use Recent decisions, support overrides, and Membership timeline to diagnose
   route or permission denials.

Visible elements:

- Overview cards summarize the active tenant scope and membership posture.
- User directory and raw identifier detail expose only policy-safe user data.
- Invite, Link, Grant, Revoke, and status action controls write audited access
  changes through backend actions.

#### Run Workspace

![Run workspace for the Design Reviewer Council example](docs/assets/design-reviewer-example/admin-ui/run-workspace-wide.png)

Use this page for optional user-facing run review after a workflow version is
published.

1. Open `/admin/app/channels/runs?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Confirm the Run workspace panel is visible.
3. Enter the safe workflow reference, such as the published workflow version id.
4. Enter a safe Request summary such as `Design an admin workspace where tenant
   admins can create, test, and publish multi-agent workflows without editing
   raw JSON.`
5. Select Start Run.
6. Review action state after submission.
7. After a run id exists, review status and progress, permitted actions,
   approval prompts, safe result keys, artifacts, subscriptions, and callback
   state.

Visible elements:

- The Start run form contains Workflow and Request summary fields plus Start
  Run.
- Status and progress appears only after a run exists.
- Actions are backend-permitted controls such as Cancel, Subscribe, Register
  Callback, and approval decisions when the run is waiting on a prompt.

#### Operations Review

![Operations review page for the Design Reviewer Council example](docs/assets/design-reviewer-example/admin-ui/operations-wide.png)

Use this page after setup, validation, test runs, or optional user-facing runs.

1. Open `/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Review Workbench summaries for tenant activity, system health, channels,
   reliability state, runs, providers, skills, and usage.
3. Review Likely causes for bounded failure summaries.
4. Review Tenant activity and any run timeline, branch, gateway, tool, or
   delivery summaries when run debug evidence exists.
5. Review Recovery posture for retry, dead-letter, quota, lease, and breaker
   evidence.
6. Use Export evidence only when you need a redacted support package.
7. Review Redacted signals for safe operational log summaries.

Visible elements:

- Summary and health panels give the operator-level picture of the active
  tenant.
- Run debug panels appear when there is safe run evidence to inspect.
- Export evidence produces a redaction-safe snapshot rather than raw runtime
  payloads.

#### Runtime Replay Graph

![Runtime replay graph for the Design Reviewer Council example](docs/assets/design-reviewer-example/admin-ui/interaction-replay-graph-wide.png)

Use this page after a review round has launched or completed.

1. Open `/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Select or link to the review round's workflow run.
3. Confirm Runtime run communication appears when the run has authorized graph
   evidence.
4. Review node statuses such as succeeded, retry scheduled, paused, queued, or
   unavailable.
5. Select an edge to inspect replay references such as handoff to reviewer,
   replay sequence, run steps, timeline events, or interaction evidence.
6. Confirm partial replay evidence is called out when some interaction records
   cannot be mapped to topology edges.

Visible elements:

- Runtime graph canvas.
- Node and edge lists.
- Selected edge detail with safe run-step and interaction references.
- Partial runtime evidence and partial replay evidence status messages.

#### Usage Review

![Usage review page for the Design Reviewer Council example](docs/assets/design-reviewer-example/admin-ui/usage-wide.png)

Use this page after provider probes, gateway calls, test runs, or optional
runtime activity.

1. Open `/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Keep the tenant filter scoped to Acme as a tenant administrator.
3. Choose a Group By dimension such as Day, Provider, Model, Workflow, Agent,
   Prompt, Gateway Operation, or Governed Tool.
4. Review total tokens, estimated cost, usage-event count, latency,
   unavailable usage, and confidence cards.
5. Review the Daily usage trend and Rollups table.
6. Review Safe events for redacted drilldown rows when events exist.
7. Use Export CSV or Create export only for reviewer-safe usage evidence.

Visible elements:

- Header actions refresh the dashboard and request exports.
- Filter controls adjust tenant, date range, and grouping.
- Summary cards, trend, rollups, safe events, and exports are all
  backend-owned projections of usage records.

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

Current-code review: prompt/profile/provider governance is supported.
Model-backed graph role execution is available behind explicit governed
execution mode and safe pin/policy/credential/contract checks; deterministic
execution remains the default for local QA.

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

Current-code review: the workflow draft can be modeled, validated, published,
and inspected through both the stored graph preview and Agent Communication
Graph viewer.

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

### Step 8 - Use The Production Review Loop

The implemented coordinator owns repeated rounds:

```text
DesignReviewService.create_session(...)
DesignReviewCoordinator.launch_round(...)
DesignReviewCoordinator.complete_round(...)
DesignReviewCoordinator.apply_manual_decision(...)
```

Use `/admin/app/design-reviews` for the browser flow or the
`/admin/design-reviews` API route family for automation. The coordinator
launches exactly one acyclic DB-backed runtime workflow run for each review
round. Completion records safe reviewer verdicts, evaluates
`four_of_five_no_blockers` or `three_of_four_no_blockers`, creates a handoff
when approved, creates the next immutable revision when revision is required,
or pauses for manual resolution when evidence is incomplete, unsafe,
contradictory, or exhausted.

Source locations:

- `src/multi_agent_platform/admin/design_review/`
- `src/multi_agent_platform/api/schemas/design_review.py`
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `src/multi_agent_platform/db/models/design_review.py`
- `src/multi_agent_platform/db/repositories/design_review.py`
- `frontend/admin/src/components/designReviews/`
- `tests/unit/admin/design_review/test_design_review_service.py`
- `tests/integration/api/test_admin_design_review_api.py`
- `tests/integration/api/test_admin_design_review_coordinator_api.py`
- `tests/contract/test_design_review_contracts.py`

Current-code review: the domain, coordinator, workspace, and template
readiness paths are implemented. Remaining production hardening should focus on
tenant-specific prompt/profile/provider content and deployment policy rather
than inventing new domain foundations.

### Step 9 - Use Governed Model-Backed Role Execution

The production path can opt role nodes into governed model-backed execution.
The executor:

1. Loads the role's prompt/profile/provider references.
2. Builds a safe model input from the design packet and upstream summaries.
3. Calls `ModelGateway`.
4. Validates the structured output against the role's output contract.
5. Stores large allowed outputs only as governed artifacts when allowed.
6. Returns safe summaries, digests, redacted evidence, and usage metadata.

Source locations:

- `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- `src/multi_agent_platform/model_providers/gateway.py`
- `src/multi_agent_platform/model_providers/secrets.py`
- `src/multi_agent_platform/usage/`
- `src/multi_agent_platform/storage/`
- `tests/unit/runtime/test_model_role_executor.py`
- `tests/integration/test_graph_model_role_execution.py`

Current-code review: model-backed role execution is available only when
explicit execution mode, prompt/profile/provider pins, credential readiness,
provider policy, output-contract validation, tenant scope, and redaction checks
permit it. Denied paths fail closed before graph success. Existing deterministic
QA and test-bench paths remain the default.

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
uv run pytest tests/unit/admin/design_review/test_design_review_service.py
uv run pytest tests/unit/admin/design_review/test_design_review_coordinator.py
uv run pytest tests/unit/admin/design_review/test_design_review_template.py
uv run pytest tests/unit/admin/test_agent_graph.py
uv run pytest tests/unit/operations/test_runtime_agent_graph.py
uv run pytest tests/unit/runtime/orchestration/test_interaction_evidence.py
uv run pytest tests/integration/api/test_admin_design_review_api.py
uv run pytest tests/integration/api/test_admin_design_review_workspace_api.py
uv run pytest tests/integration/api/test_admin_design_review_template_api.py
uv run pytest tests/integration/api/test_admin_agent_graph_api.py
uv run pytest tests/integration/api/test_admin_runtime_agent_graph_api.py
uv run pytest tests/integration/runtime/test_runtime_interaction_evidence_repository.py
uv run pytest tests/contract/test_design_review_contracts.py
uv run pytest tests/contract/test_design_review_coordinator_contracts.py
```

Full validation:

```bash
uv run pytest
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Frontend validation:

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
- live-data empty states before seeded design review records exist
- seeded-state projections after repository-backed design review records exist
- prompt/profile/provider readiness
- five-reviewer round
- four-reviewer round
- quorum success
- quorum failure
- blocking issue override
- manual resolution pause
- revision round launch
- approved development handoff
- reusable council template readiness and current required evidence
- workflow draft and published-version Agent Communication Graph
- runtime Agent Communication Graph with safe node and edge statuses
- durable interaction replay references and partial replay state
- cross-tenant denial
- redaction sweep for raw prompts, completions, secrets, credential values,
  private payloads, memory contents, unauthorized run data, and raw tool payloads
- visible-copy sweep for product-facing Admin terminology, with implementation
  framework labels limited to developer documentation and source context

## Development Recommendation

Continue treating this as an additive scenario on top of the workflow registry,
graph execution, governance, test bench, and operations workbench.

The durable foundation is now present:

1. Reusable `Design Reviewer Council` template installation exists.
2. Required deterministic and model-safe evidence can back publish gates.
3. `DesignReviewCoordinator` persists sessions and launches repeated acyclic
   review-round runs.
4. Model-backed role execution is gated behind explicit safe execution mode.
5. `/admin/app/design-reviews` is live-data backed from the production route.
6. Agent graph and runtime replay surfaces expose safe inspection evidence.

Next production work should be tenant-specific: author high-quality prompts and
profiles, configure real provider policy and credential references, decide
which reviewer roles are enabled for each tenant, tune evidence retention, and
run the QA064/QA068 validation matrix before enabling governed live model calls.

This matches the project's current architecture: contract-first, tenant-scoped,
redaction-safe, live-data guarded, auditable, deterministic in local QA, and
capable of later switching to governed live model calls when provider policy
allows it.
