# Spec-Kit Breakdown And Phase Prompts

## 1. Purpose

This document breaks the project into implementation specs that fit the
spec-kit lifecycle:

- `/speckit.specify`
- `/speckit.plan`
- `/speckit.tasks`

The prompts below are designed to keep every spec aligned with the same
standards:

- Python, FastAPI, LangChain, LangGraph, and PostgreSQL
- immutable versioned memory
- durable workflow execution
- reusable subagent workflows compiled as nested orchestrated subgraphs
- tenant isolation, fair scheduling, and quota-aware scaling
- version-pinned in-flight execution bundles
- Auth0 with development bypass
- secret-manager backed tool credentials and explicit tool policies
- object storage for large artifacts and payloads
- Web UI, Telegram, and Web API interaction
- explicit human approval and resume flows where workflows require it
- production-grade auditing and debugging
- at least 90 percent unit-test coverage for the implemented scope
- PR review notes and testing instructions in every spec artifact
- global `README.md` updates after each implemented spec

## 2. Recommended Spec Sequence

| Spec ID | Name | Why It Comes Here |
| --- | --- | --- |
| 001 | Platform foundation | Establish repo shape, config, DB, CI, quality gates |
| 002 | Identity and access | Secure entry points before exposing workflows |
| 003 | Workflow studio and registry | Define how admins model agents, skills, and contracts |
| 004 | Durable orchestration runtime | Create the execution engine and checkpoint model |
| 005 | Immutable memory and versioning | Add append-only memory and replay-safe retrieval |
| 006 | Interaction channels | Add Web UI, Telegram, and API entry flows |
| 007 | LLM routing and skill configuration | Support global and per-agent model control |
| 008 | Auditability and debugging | Provide production introspection and replay tools |
| 009 | Reliability and scale hardening | Add operational resilience and scale tests |

## 3. How To Use These Prompts

For each spec:

1. Run the `specify` prompt first and confirm the requirement boundaries.
2. Run the `plan` prompt with concrete technology and design expectations.
3. Run the `tasks` prompt to force TDD, docs, coverage, and README work into
   the task list.

If a generated artifact misses tests, docs, PR instructions, or README work,
consider it incomplete and regenerate or edit before implementation.

## 4. Spec Prompts

### Spec 001: Platform Foundation

#### Goal

Create the base Python service, repository layout, configuration model,
database scaffolding, testing harness, and developer workflow.

#### `/speckit.specify` Prompt

```text
/speckit.specify Create the platform foundation for a production multi-agent AI
system. The system must use Python, FastAPI, LangChain, LangGraph, and
PostgreSQL. This spec should cover repository structure, application bootstraps,
configuration loading, database migrations, local development workflow, worker
process bootstraps, health endpoints, CI quality gates, tenant-context
propagation, secret-provider abstractions, artifact-storage abstractions, and
test harness setup. Do not implement user-facing channels yet beyond placeholder
endpoints. Require at least 90 percent unit-test coverage for the spec
implementation, PR review documentation, testing instructions, and a README
update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Use Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, pytest, and
PostgreSQL. Plan a modular service layout that cleanly separates API, runtime,
memory, auth, admin, and audit concerns. Include environment-based config,
dependency injection, local Docker Compose support, migration strategy, test
fixtures, linting, type checking, coverage enforcement, tenant scoping,
artifact-storage strategy, secret-manager integration points, and queueing
abstractions. The plan must produce research.md, data-model.md, contracts where
applicable, quickstart.md, and explicit constitution checks. Keep all choices
aligned with a durable, auditable multi-agent platform.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the platform foundation plan into test-first tasks with
exact file paths. Include tasks for app bootstrap, config, DB session
management, migrations, pytest scaffolding, CI scripts, coverage thresholds,
tenant context plumbing, secret-provider abstractions, artifact-storage
abstractions, README updates, PR review notes, and testing instructions. Mark
safe parallel tasks with [P] and ensure tests are written before implementation
where practical.
```

### Spec 002: Identity And Access

#### Goal

Add Auth0-based authentication, role-based authorization, and a development/test
mode that disables external auth while preserving authorization logic.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add authentication and authorization to the multi-agent
platform. Production must use Auth0 for end-user and admin authentication.
Development and test environments must be able to disable external auth while
still exercising authorization logic with deterministic local principals. The
spec must cover user roles, admin roles, API protection, Web UI protection, and
auditability of access decisions. Include tenant-scoped identity context and how
user-delegated credentials differ from platform-managed secrets. Require at
least 90 percent unit-test coverage, PR review notes, testing instructions, and
a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan Auth0 integration for FastAPI using JWT validation,
config-driven enable or disable behavior, and dependency-based authorization
checks. Include role mapping strategy, local principal injection for dev and
tests, security-sensitive configuration handling, failure modes, and audit
events for access decisions. Define tenant-context extraction, role scoping, and
how user-delegated OAuth credentials are linked to approved tools without
exposing secret material. Ensure the plan identifies data needs, interface
contracts, test strategy, and quickstart updates.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Convert the identity and access plan into file-specific tasks.
Include tests for JWT validation, role enforcement, dev bypass behavior,
configuration errors, protected endpoint behavior, tenant-context extraction,
and delegated-credential boundary handling. Also include tasks for docs, PR
review guidance, test instructions, and README updates. Use [P] only where
implementation areas do not overlap.
```

### Spec 003: Workflow Studio And Registry

#### Goal

Allow admins to define workflows, agents, subagents, skills, roles, and
contracts, then publish immutable versions for runtime execution.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add an admin workflow studio and registry for a multi-agent AI
platform. Admin users must be able to create multi-agent workflows, define agent
and subagent roles, assign skills, define communication contracts, maintain
drafts, validate designs, and publish immutable workflow versions for runtime
use. Include reusable subworkflows, join policies, approval gates, and immutable
published version bundles. Focus this spec on workflow-definition authoring and
storage, not execution. Require at least 90 percent unit-test coverage, PR
review notes, testing instructions, and a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Design the admin workflow registry using FastAPI, PostgreSQL, and
Pydantic-first schemas. Include draft and publish lifecycle, versioning rules,
agent-definition schema, skill bindings, contract schema management, validation
rules, subworkflow references, join-policy validation, approval-gate schema, and
an API plus Web UI plan for admin workflows. The plan must define data models,
contracts, compatibility rules, quickstart usage, and how published definitions
compile into runtime metadata and pinned run-version bundles.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the workflow studio plan into test-first tasks covering
schema models, persistence, validation, publish immutability, admin APIs, and
UI surfaces. Include tasks for contract validation tests, subworkflow validation,
approval-gate validation, version-compatibility validation, docs, PR review
notes, testing instructions, and README updates. Use task ordering that respects
model, service, API, and UI dependencies.
```

### Spec 004: Durable Orchestration Runtime

#### Goal

Build the LangGraph execution runtime, checkpoint persistence, handoff routing,
and worker leasing model.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add the durable orchestration runtime for the multi-agent AI
platform. The runtime must execute published workflows with LangGraph, persist
workflow state in PostgreSQL, route agent-to-agent handoffs through explicit
contracts, support background workers, and survive worker or node failure by
resuming from durable checkpoints. It must also support nested subworkflows,
parent-child run lineage, pinned execution bundles, and pause-resume behavior
for approval gates. Require at least 90 percent unit-test coverage, PR review
notes, testing instructions, and a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan a LangGraph-based orchestration runtime with a PostgreSQL
checkpointer, worker leasing, checkpoint frequency rules, handoff envelope
storage, contract validation, and side-effect intent capture. Include research
on durable execution patterns, failure recovery behavior, retry policy,
compensation hooks, subworkflow execution semantics, version-bundle pinning,
approval wait states, and test strategy for crash and resume scenarios.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Convert the orchestration runtime plan into ordered tasks with
clear file paths. Include tests for checkpoint persistence, resume after crash,
worker lease expiry, contract-gated routing, version-bundle pinning, subworkflow
lineage, approval pause-resume behavior, and idempotent retry handling. Add
tasks for docs, PR review notes, testing instructions, and README updates.
```

### Spec 005: Immutable Memory And Versioning

#### Goal

Create the append-only memory subsystem and retrieval interfaces.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add immutable, versioned memory to the multi-agent platform.
Agent memory must never be updated in place. Every change must create a new
version with lineage to the prior version, and the system must support replay,
diffing, audit, and current-head retrieval for workflow execution. Require at
least 90 percent unit-test coverage, PR review notes, testing instructions, and
a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Design an append-only memory subsystem backed by PostgreSQL.
Include memory scopes, version lineage, head projections, retrieval APIs,
concurrency handling, indexing strategy, archival considerations, and how the
runtime reads and writes memory safely. Include tenant scoping and how memory is
linked to pinned run bundles and parent-child run lineage. Define the data
model, access patterns, and test strategy for immutability and version
correctness.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the immutable memory plan into TDD-friendly tasks. Include
tests for append-only writes, head resolution, lineage integrity, concurrent
writes, retrieval filters, audit views, and tenant-scoped access behavior. Also
include docs, PR review notes, testing instructions, and README update tasks.
```

### Spec 006: Interaction Channels

#### Goal

Expose the system through Web UI, Telegram, and Web APIs without splitting core
runtime semantics.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add user interaction channels to the multi-agent platform:
Web UI, Telegram, and Web APIs. All channels must route into the same workflow
invocation model, share authentication and authorization policies where
applicable, and support live progress, persisted status retrieval, terminal
completion notifications, and final result retrieval by run identifier. Define
a consistent run lifecycle across channels, including queued, running,
waiting-for-input, completed, failed, and cancelled states. Focus this spec on
channel adapters and user interaction flows, not new workflow logic. Include
approval and resume interactions plus artifact download behavior. Require at
least 90 percent unit-test coverage, PR review notes, testing instructions, and
a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan the channel layer using FastAPI for Web UI and REST APIs plus
Telegram webhook handling. Include request normalization, session identifiers,
trace correlation, streaming or polling status updates, error handling,
auth-aware routing, and test strategy. Define the run-status API, timeline-event
model, result retrieval endpoints, Telegram completion message behavior, Web UI
run details behavior, approval and resume endpoints, artifact access patterns,
and any callback patterns for API clients. Define any contracts, quickstart
instructions, and UX considerations needed for operators and end users.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Generate file-specific tasks for Web UI routes, API routes,
Telegram webhook handling, shared request envelopes, and channel-level tests.
Include tasks for status endpoints, timeline endpoints, result retrieval,
streaming updates, completion notifications, approval and resume flows, artifact
download behavior, and channel-level tests for terminal-state behavior. Include
tasks for auth integration checks, docs, PR review notes, testing instructions,
and README updates. Use [P] only for safely isolated adapters.
```

### Spec 007: LLM Routing And Skill Configuration

#### Goal

Let the platform choose models globally or per agent and bind allowed skills to
each agent definition.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add model routing and skill configuration to the platform.
Administrators must be able to set a global default LLM and override it per
workflow, per agent, or per step. Agents must also have explicit skill bindings
and allowed tool policies. The system must record which model and prompt version
were used for every run. Secret references, outbound domain policies, and
tool-specific credential requirements must also be versioned and auditable.
Require at least 90 percent unit-test coverage, PR review notes, testing
instructions, and a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Design a configuration subsystem for model routing and skill
bindings. Include precedence rules, validation, persistence, runtime resolution,
audit metadata, rollback behavior, secret references, outbound tool policies,
and tests for deterministic resolution. The plan should define data models,
APIs, and quickstart guidance for changing model assignments and tool access
safely.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the model routing and skill configuration plan into
test-first tasks. Include tests for precedence resolution, invalid
configurations, audit logging of chosen models, allowed-skill enforcement,
secret-reference validation, and outbound policy enforcement. Also include docs,
PR review notes, testing instructions, and README updates.
```

### Spec 008: Auditability And Debugging

#### Goal

Provide operators with production-safe introspection, traceability, and replay
tooling.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add auditing and debugging capabilities for the multi-agent
platform in production. The system must capture workflow timelines, agent
handoffs, contract-validation results, memory writes, tool usage, model
selection, and operator-visible trace data. Admin users must be able to inspect
run timelines and debug failed executions without direct database access.
Include version-bundle visibility, parent-child run lineage, notification
delivery state, and secret-access audit metadata. Require at least 90 percent
unit-test coverage, PR review notes, testing instructions, and a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Plan an observability and audit subsystem using structured logs,
trace IDs, metrics, PostgreSQL audit tables, and operator-facing APIs or UI.
Include how audit data will be queried, how sensitive data will be redacted or
classified, how replay views will work, how parent-child runs and version
bundles will be visualized, and how testing will validate trace and timeline
completeness.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Turn the auditability plan into implementation tasks with exact
paths. Include tests for event creation, trace correlation, timeline assembly,
redaction behavior, version-bundle visibility, notification traceability, and
admin-only debug access. Also include docs, PR review notes, testing
instructions, and README update tasks.
```

### Spec 009: Reliability And Scale Hardening

#### Goal

Prepare the system for thousands of active users, failure injection, and
production operating limits.

#### `/speckit.specify` Prompt

```text
/speckit.specify Add reliability and scale hardening to the multi-agent
platform. The system must support thousands of active users, use recovery-safe
worker behavior, implement circuit breakers and compensation hooks where needed,
and provide operational controls for backpressure, retry tuning, failure
inspection, tenant fairness, and quota enforcement. Require at least 90 percent
unit-test coverage, PR review notes, testing instructions, and a README update.
```

#### `/speckit.plan` Prompt

```text
/speckit.plan Create a reliability and scale plan covering worker autoscaling,
lease tuning, database pooling, partitioning strategy, retry policy, circuit
breaker rules, compensation orchestration, dead-letter handling, load test
approach, operational dashboards, tenant fairness controls, and artifact-storage
throughput considerations. Include failure-mode research and a validation
strategy for resume-after-failure behavior under load.
```

#### `/speckit.tasks` Prompt

```text
/speckit.tasks Break the reliability and scale plan into concrete tasks. Include
tests for lease expiry handling, retry backoff, circuit breaker transitions,
compensation invocation, tenant-quota enforcement, fair scheduling, and
load-test harness creation. Add tasks for docs, PR review notes, testing
instructions, and README updates.
```

## 5. Cross-Cutting Architecture Requirements

These requirements must be addressed in any spec where they are relevant:

- Tenant isolation and quota enforcement must be explicit in data models, APIs,
  and runtime scheduling.
- Runs must pin immutable workflow, contract, prompt, model, and tool-policy
  versions before execution begins.
- Reusable subworkflows must preserve parent-child lineage and join semantics.
- Secrets must be represented as references and resolved through a secret
  manager, never embedded in workflow definitions or logs.
- Large artifacts must use object storage with PostgreSQL metadata.
- Human approvals must be modeled as durable wait states with auditable resume
  behavior.

## 6. Cross-Spec Rules To Add To Every PR

Every implementation PR should include:

- linked spec directory,
- summary of functional behavior added,
- architecture impact notes,
- database or contract changes,
- test evidence and coverage summary,
- manual testing steps,
- README delta summary,
- operational or rollback notes.

## 7. Suggested Spec Review Checklist

Before implementation begins on a spec, confirm:

- the spec focuses on user and business outcomes,
- the plan resolves all open technology choices,
- the tasks are file-specific and dependency-aware,
- tests appear before implementation work where possible,
- README and docs work is present,
- coverage expectations are explicit,
- production observability and failure behavior are addressed where relevant,
- tenant isolation and quota behavior are addressed where relevant,
- version pinning, secrets, artifact storage, and approval flows are addressed
  where relevant.

## 8. Sources

This breakdown is aligned with:

- the attached multi-agent orchestration PDF,
- the official spec-kit workflow of constitution, specify, plan, and tasks as
  documented in [github/spec-kit](https://github.com/github/spec-kit).
