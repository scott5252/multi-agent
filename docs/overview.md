# Multi-Agent AI Platform Overview

This document explains the planned product in business and user terms. It is
based on the architecture in
[architecture.md](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
and describes how the platform is expected to work once the full design is
implemented.

## What The System Is

The Multi-Agent AI Platform is a managed environment for running AI-powered
business workflows safely and at scale. Instead of relying on one general
assistant to do everything, the platform coordinates multiple specialized
agents, each with a defined role, approved tools, and a required output format.

In practical terms, the platform is designed to help organizations:

- turn repeatable knowledge work into structured AI workflows,
- let users start work from a Web UI, Telegram, or an API,
- show progress while work is running,
- pause for human approval when a decision should not be automated,
- keep results, timeline history, and audit evidence in one place,
- reuse proven agent patterns across teams and business processes.

This makes the product better suited to real operations than a simple chatbot.
It is intended for work that needs traceability, controlled handoffs, review,
and reliable recovery if a worker or service fails.

## What The System Can Do

Once developed, the platform is designed to support five core outcomes.

### 1. Run Multi-Step AI Workflows

Users will be able to submit a request such as reviewing a vendor packet,
preparing an incident summary, or assembling a customer brief. The platform
will route that request through a published workflow made up of multiple steps.
Each step can be handled by a different agent.

### 2. Support Specialized Agents And Reusable Sub-Agents

An organization can define a main workflow and then reuse smaller subworkflows
inside it. For example, a "Vendor Review" workflow could call a reusable
"Document Extraction" subworkflow and a reusable "Risk Assessment"
subworkflow. This makes large business processes easier to standardize and
scale.

### 3. Keep Humans In Control

The architecture explicitly supports approval gates. If a workflow reaches a
point where a human decision is required, the run can pause, request input, and
resume only after approval, rejection, or clarification.

### 4. Work Across Multiple Channels

The same workflow model is intended to be available through:

- a Web UI for rich interaction and run history,
- Telegram for lightweight approvals and status checks,
- Web APIs for system-to-system integration.

### 5. Provide Durable, Auditable Results

Every workflow run is intended to have a lifecycle, a visible status, a
timeline, and a final result. Users and managers will be able to see what
happened, when it happened, and where a run is blocked or completed.

## A Simple Mental Model

For non-technical readers, the product can be understood through a few terms.

| Term | Meaning in the product |
| --- | --- |
| Workflow | A repeatable business process the platform can run |
| Agent | A specialized AI worker responsible for one step |
| Sub-agent or subworkflow | A smaller reusable workflow inside a larger one |
| Run | One instance of a workflow started by a user or another system |
| Approval gate | A step where a human must approve, reject, or add input |

## How People Would Use The Product

### End Users

Most users will not build workflows themselves. They will choose from approved
published workflows, submit a request, provide any needed files or details, and
then monitor progress until the result is ready.

Typical user actions:

- choose a workflow in the Web UI,
- upload a document or enter a request,
- watch the run move from accepted to queued to running,
- respond if the workflow asks for clarification,
- review the final output and download related artifacts.

### Managers

Managers will use the system to review outputs, approve critical decisions, and
track work across teams. They may receive an approval request in the Web UI or
through Telegram, and they can inspect the timeline before making a decision.

Typical manager actions:

- approve or reject a proposed next step,
- monitor whether important requests are delayed or blocked,
- review the completed result package before it is acted on,
- confirm that the process followed the expected controls.

### Admins

Admins are the primary workflow authors in the planned architecture. They are
expected to define workflows, agent roles, approved skills, handoff contracts,
approval points, and reusable subworkflows. They can then publish immutable
workflow versions for users to run.

In some organizations, a department manager may also be given admin rights.
That person could then design workflows for their own function while standard
users continue to launch runs rather than author the workflows themselves.

## Realistic Usage Examples

The platform is intentionally general-purpose, so the most realistic examples
are cross-functional business processes that need structured AI help plus human
oversight.

### Example 1: Vendor Intake And Risk Review

A procurement analyst starts a "Vendor Review" workflow in the Web UI and
uploads a supplier questionnaire, draft contract, and security responses.

The workflow could run like this:

1. An intake agent extracts key details such as vendor name, services offered,
   contract term, and missing fields.
2. A document-summary subworkflow creates plain-language summaries of the
   uploaded materials.
3. A risk-review subworkflow runs several specialized checks in parallel, such
   as policy alignment, security response review, and contract red-flag
   detection.
4. The platform combines those results into one recommendation packet.
5. If the risk level crosses a defined threshold, the workflow pauses for a
   procurement manager or security lead to approve the next step.
6. After approval, the workflow completes and stores the final recommendation,
   supporting notes, and downloadable artifacts.

Why this is realistic:

- it uses structured documents,
- it benefits from multiple specialized reviews,
- it needs a human checkpoint before a business decision is finalized,
- it produces an auditable outcome that different stakeholders can inspect.

### Example 2: Incident Response Support

A service manager uses Telegram to submit a production incident summary after an
overnight outage. The manager wants a fast operational brief for the morning
leadership meeting.

The workflow could run like this:

1. A triage agent classifies the incident and identifies missing facts.
2. A research subworkflow gathers allowed evidence from approved internal
   systems, such as ticket summaries, logs, or prior incident notes, if those
   tools have been configured for the tenant.
3. A communications agent drafts a leadership summary with impact, timeline,
   likely cause, and recommended follow-up actions.
4. If confidence is too low or evidence conflicts, the workflow pauses and asks
   the manager for clarification rather than guessing.
5. The manager receives a Telegram completion message and can open a Web UI
   details page for the full report and timeline.

Why this is realistic:

- it matches the platform's support for Telegram, Web UI, and approval or
  clarification pauses,
- it uses specialized agents instead of a single monolithic prompt,
- it respects the architecture's tool-governance model by relying only on
  approved systems.

### Example 3: API-Driven Customer Onboarding Preparation

An organization connects its CRM or onboarding system to the platform through
the API. When a new enterprise customer is marked "ready for onboarding," the
external system starts a workflow automatically.

The workflow could run like this:

1. The onboarding system sends the request and receives a `run_id`.
2. A preparation agent reviews the customer profile and kickoff notes.
3. A subworkflow builds a first-pass onboarding plan, identifies dependencies,
   and drafts questions for the implementation team.
4. A manager reviews the package in the Web UI and approves it before it is
   shared with the customer team.
5. The external system fetches the final result through the API or receives it
   through the configured callback pattern.

Why this is realistic:

- it uses the architecture's asynchronous API model,
- it fits the design where runs are tracked independently of the calling
  system,
- it shows how AI workflows can be embedded in an existing business process
  instead of requiring users to switch tools for every task.

## Real-World User Interaction Examples

The platform is designed so that interaction feels operational, not
experimental.

### Web UI Example

A user opens the Web UI, selects "Vendor Review," uploads three files, and
starts the run. The screen first shows that the request has been accepted, then
queued, then running. A timeline view shows which step is active. If the
workflow needs a decision, the run changes to a waiting state and the user sees
an approval prompt. When the work is complete, the same page shows the final
summary, artifacts, and history.

### Telegram Example

A regional manager sends a request to the Telegram bot asking for a status
update on a previously submitted workflow. The bot responds with a concise
summary such as "running," "waiting for input," or "completed." If the run is
finished, the bot sends a short result summary and a deep link to the richer
Web UI details page.

### API Example

A business system submits a workflow request through the API and receives an
asynchronous response with a run identifier. That system can poll for status or
subscribe to updates. When the workflow finishes, it retrieves a structured
result payload and any related artifact links. This is how existing enterprise
systems can use the platform without changing the underlying workflow engine.

## How The System Can Scale

The architecture is designed to scale in ways that matter to business leaders,
admins, and end users.

### Scale In User Volume

The Web and API layer is designed to be stateless, which means more API or Web
servers can be added behind a load balancer as demand grows. This is important
for supporting thousands of active users without redesigning the application.

### Scale In AI Workload

The worker pool that runs workflows is separate from the user-facing API layer.
That means the organization can increase workflow-processing capacity without
changing the front end. Busy periods in one area do not have to overwhelm the
entire system.

### Scale Across Teams And Tenants

The platform is designed for multi-tenant use with tenant-aware scheduling,
tenant limits, and row-level data isolation. In business terms, that means one
department or customer should not be able to consume all shared capacity or see
another tenant's data.

### Scale In Workflow Complexity

Reusable subworkflows allow complex processes to be assembled from smaller,
tested building blocks. An admin does not have to redesign document extraction,
approval handling, or risk scoring every time a new workflow is introduced.

### Scale In Data And Output Size

Large files and generated artifacts are intended to be stored outside the
transactional database in object storage, while PostgreSQL retains the
ownership, audit, and retrieval metadata. This supports large outputs without
slowing the system's core transaction path.

### Scale In Governance

Published workflow versions are immutable, and in-flight runs are pinned to the
versions they started with. This is important operationally because a workflow
can be improved for new users without changing the behavior of requests already
in progress.

## How Admins Create Workflows With Agents And Sub-Agents

In the planned design, workflow creation is primarily an admin capability.
Standard users create workflow runs, not the underlying workflow definitions.

The expected admin workflow is:

1. Create a draft workflow in the Admin Studio.
2. Define the purpose of each agent step.
3. Assign approved skills, tool access, and model settings to each step.
4. Define the required input and output contracts between steps.
5. Insert approval gates where a human must review a decision.
6. Reuse existing subworkflows where appropriate.
7. Validate and simulate the draft.
8. Publish an immutable version and activate it for the intended tenant or
   environment.

### Realistic Workflow-Authoring Example

A department admin wants to build a "Contract Intake And Review" workflow.

The admin could design it as follows:

- Main workflow step 1: intake agent
  The agent checks that required files are present and extracts basic metadata.
- Main workflow step 2: clause-review subworkflow
  This subworkflow contains a red-flag agent, an obligations-summary agent, and
  a missing-terms agent.
- Main workflow step 3: policy-alignment subworkflow
  This subworkflow checks the draft contract against the organization's standard
  policy rules and approved positions.
- Main workflow step 4: approval gate
  If the contract contains red flags above a defined threshold, the legal
  manager must approve the next action.
- Main workflow step 5: recommendation agent
  This agent produces the final summary and recommended next step.

Why sub-agents matter in this example:

- the clause-review logic can be reused in other legal workflows,
- the policy-alignment logic can be maintained centrally,
- each subworkflow can have its own contract, validation rules, and join logic,
- the final workflow remains understandable to managers because each part has a
  clear business purpose.

## How Users Participate In Those Workflows

Once the workflow is published, a standard user does not need to understand the
internal agent design. They only need to know what business process to start
and what information to provide.

Using the contract-review example above, a user might:

1. open the published workflow,
2. upload the proposed agreement,
3. answer a few intake questions,
4. wait while the platform runs the specialized review steps,
5. respond if the workflow requests clarification,
6. receive the final recommendation and related artifacts.

That division of responsibility is important. Admins create the controlled AI
process. Users consume it in a guided way.

## Why This Matters For Executives And Managers

For executives, the value of the platform is not simply "more AI." The value is
that AI work can be standardized, governed, monitored, and improved over time.

For managers, the platform offers a practical operating model:

- specialized agents instead of one opaque assistant,
- visible progress instead of black-box waiting,
- approval checkpoints instead of uncontrolled automation,
- reusable workflow design instead of one-off prompt engineering,
- auditability and recovery instead of fragile session-based behavior.

In short, the planned product is a business workflow platform for AI-driven
work, designed to be usable by everyday teams and manageable by operations,
technology, and leadership stakeholders.
