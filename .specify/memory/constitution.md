<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Placeholder Principle 1 -> I. Durable By Default
- Placeholder Principle 2 -> II. Immutable State And Memory
- Placeholder Principle 3 -> III. Contract-First Agent Coordination
- Placeholder Principle 4 -> IV. Security With Practical Development Ergonomics
- Placeholder Principle 5 -> V. Operability Is A Product Requirement
- Added -> VI. Spec-Driven Delivery
- Added -> VII. Test And Documentation Discipline
- Added -> VIII. Clear Ownership And Small Safe Changes
- Added -> IX. Tenant Isolation And Fair Scheduling
- Added -> X. Version-Pinned Execution
- Added -> XI. Secret Hygiene And Controlled Tool Access
- Added -> XII. Tiered Storage For Large Payloads
- Added -> XIII. Human Approval Is Durable State
Added sections:
- Platform Constraints
- Delivery Workflow And Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ updated: .specify/templates/spec-template.md
- ✅ updated: .specify/templates/plan-template.md
- ✅ updated: .specify/templates/tasks-template.md
- ✅ updated: .specify/templates/commands/constitution.md
- ✅ updated: .specify/templates/commands/specify.md
- ✅ updated: .specify/templates/commands/plan.md
- ✅ updated: .specify/templates/commands/tasks.md
- ✅ updated: .specify/templates/commands/clarify.md
- ✅ updated: .specify/templates/commands/analyze.md
- ✅ updated: .specify/templates/commands/checklist.md
- ✅ updated: .specify/templates/commands/implement.md
- ✅ updated: .specify/templates/commands/taskstoissues.md
- ✅ updated: README.md
- ✅ updated: docs/quickstart.md
Follow-up TODOs:
- None
-->
# Multi-Agent AI Platform Constitution

## Core Principles

### I. Durable By Default
Every workflow, approval path, and operator intervention MUST survive process,
worker, and node failure without losing authoritative state. Before
implementation, the governing spec and plan MUST define checkpoint boundaries,
lease and retry behavior, compensation behavior, and idempotency rules for each
external side effect. Features that cannot explain how they resume after
interruption MUST NOT be approved. Rationale: long-running multi-agent
execution is the platform's core value and durability failures are product
failures.

### II. Immutable State And Memory
Workflow coordination MUST use immutable snapshots, append-only events, or
versioned records. Shared mutable in-memory state MUST NOT be the source of
truth for workflow handoffs, parent-child coordination, or memory updates.
Agent memory MUST be append-only, versioned, lineage-aware, tenant-scoped, and
auditable. Rationale: immutable state is required for replay, debugging,
auditing, safe retry, and incident analysis.

### III. Contract-First Agent Coordination
Agent-to-agent and channel-to-runtime communication MUST be governed by explicit
schemas plus semantic validation rules. Contracts MUST be versioned, reviewed,
compatibility-assessed, and tested before runtime use. Contract changes MUST
document migration or compatibility behavior for in-flight runs and parent-child
handoffs. Rationale: explicit contracts are the only safe coordination boundary
in a reusable multi-agent platform.

### IV. Security With Practical Development Ergonomics
Production authentication and authorization MUST use Auth0 plus role-based
authorization. Development and test modes MAY bypass external identity
providers only through explicit configuration that still exercises authorization
checks, tenant scoping, and audit behavior with deterministic local principals.
Security-sensitive shortcuts MUST be impossible to enable accidentally in
production. Rationale: developer ergonomics matter, but they MUST NOT erase the
security model that production depends on.

### V. Operability Is A Product Requirement
Every feature that affects runtime behavior MUST define logs, metrics, traces,
workflow timelines, lineage visibility, replay support, and operator debugging
surfaces before implementation. New runtime paths MUST emit enough structured
telemetry to diagnose failures, explain side effects, and support incident
response. Rationale: production multi-agent systems are only usable when they
can be observed and debugged under real load.

### VI. Spec-Driven Delivery
All significant work MUST begin with spec-kit artifacts and MUST remain
traceable from specification through implementation. "Significant work"
includes user-visible behavior changes, schema or contract changes, workflow
changes, security changes, storage changes, tenant-affecting behavior, and
operational behavior changes. Implementation MUST NOT begin until constitution,
specify, plan, and tasks outputs exist and are mutually consistent. Rationale:
durable systems require deliberate design, not code-first improvisation.

### VII. Test And Documentation Discipline
Every implemented spec MUST target at least 90 percent unit-test coverage for
the relevant code unless an explicit waiver is approved and documented. Specs
and plans MUST include testing instructions, PR review guidance, and
documentation impact, and tasks MUST include documentation and README updates.
New behavior is incomplete until automated tests pass, relevant docs are
updated, and quickstart validation is recorded where applicable. Rationale:
quality, onboarding, and operability all degrade when tests and docs trail the
code.

### VIII. Clear Ownership And Small Safe Changes
Plans and tasks MUST identify exact files, dependency order, blocking
prerequisites, and safe parallelization boundaries. Large speculative refactors,
cross-cutting rewrites, or hidden scope growth that are not traceable to an
approved spec MUST NOT be merged. Every change set SHOULD be small enough to
review, test, and roll back safely, because safe change velocity is a platform
capability. Rationale: predictable delivery depends on explicit ownership and
controlled blast radius.

### IX. Tenant Isolation And Fair Scheduling
Tenant context MUST be explicit in APIs, data models, queues, workers,
artifacts, memory, approvals, and audits. Cross-tenant access MUST fail closed,
and shared infrastructure MUST enforce data isolation, fair scheduling, quota
controls, and noisy-neighbor protections. Plans for shared services MUST define
how tenant limits, concurrency budgets, and fairness policies are enforced and
observed. Rationale: a shared AI platform is unsafe unless isolation and fair
use are built into the platform primitives.

### X. Version-Pinned Execution
Every workflow run MUST persist a pinned execution bundle before any agent work
starts. That bundle MUST include the exact workflow version, subworkflow
versions, contract versions, prompt versions, model configuration versions, and
tool-policy versions used by the run. Resume behavior MUST reuse the same
bundle unless an explicit, audited migration path is invoked. Rationale: replay
and incident analysis are impossible if execution inputs drift mid-run.

### XI. Secret Hygiene And Controlled Tool Access
Secrets MUST be stored outside workflow definitions, source control,
application logs, and audit payloads. Runtime secret resolution MUST use a
secret manager plus least-privilege credentials, and persisted records MUST
store only auditable secret references or delegated credential metadata. Tool
use MUST be controlled by explicit allowlists, outbound egress policy, and
auditable authorization decisions. Rationale: tool and secret sprawl turns an
agent platform into an unbounded security perimeter.

### XII. Tiered Storage For Large Payloads
PostgreSQL MUST remain the transactional source of truth for workflow state,
lineage, approvals, memory metadata, audit records, and artifact metadata. The
platform MUST NOT use PostgreSQL as a blob store for large artifacts,
transcripts, attachments, or exports. Large payloads MUST use object storage
with retention, access control, and auditability anchored in PostgreSQL
metadata. Rationale: operational durability requires separating transactional
integrity from bulk storage concerns.

### XIII. Human Approval Is Durable State
Any workflow that requires approval, rejection, clarification, or supplemental
input MUST enter an explicit persisted wait state. Resume behavior MUST occur
only through auditable approval or input records and MUST preserve the original
pinned execution bundle and lineage chain. Ad hoc side channels, transient chat
state, or undocumented operator overrides MUST NOT be the authority for resume
behavior. Rationale: human input is part of workflow state and must be treated
with the same rigor as automated execution.

## Platform Constraints

- The production platform MUST be built in Python and MUST use FastAPI,
  LangChain, LangGraph, and PostgreSQL unless a future constitution amendment
  explicitly authorizes a stack change.
- The platform MUST support Web UI, Telegram, and Web API interaction channels
  through a shared runtime model that preserves tenant, user, trace, and run
  context.
- Admin users MUST be able to design workflows, agent roles, subagent roles,
  skills, and communication contracts, and published runtime definitions MUST be
  immutable.
- Durable parent-child execution lineage MUST be preserved for reusable
  subworkflows, child runs, approval gates, and replay tooling.
- PostgreSQL MUST store workflow state, approvals, transactions, memory
  metadata, lineage, and audit records; object storage MUST hold large artifacts
  with PostgreSQL metadata.
- Secret resolution MUST flow through a secret manager, and outbound tool access
  MUST be explicitly policy-controlled and auditable.

## Delivery Workflow And Quality Gates

- `/speckit.specify` outputs MUST describe prioritized user stories, measurable
  outcomes, edge cases, and explicit constitution impact for durability,
  tenant isolation, versioning, secrets, artifact storage, approval/resume,
  observability, and security whenever those concerns are in scope.
- `/speckit.specify` outputs MUST include testing instructions, PR review
  guidance, and documentation impact, including whether `README.md`,
  `docs/quickstart.md`, or feature quickstarts require updates.
- `/speckit.plan` outputs MUST include a constitution check plus explicit
  durability and failure-recovery decisions, tenant-isolation and quota
  decisions, subworkflow and parent-child lineage decisions, version-bundle
  pinning decisions, secret-management and tool-policy decisions,
  artifact-storage decisions, approval and resume decisions where relevant,
  observability requirements, test strategy, documentation tasks, and security
  review notes where relevant.
- `/speckit.plan` MUST stop on unresolved constitution violations. Any approved
  exception MUST be documented in the plan with rationale, approver, and an
  expiration or removal condition.
- `/speckit.tasks` outputs MUST be dependency-ordered, file-specific, and safe
  to execute incrementally. They MUST include test-first tasks where practical,
  documentation tasks, `README.md` update tasks, and in-scope tasks for tenant
  isolation, version pinning, secrets, artifact storage, approval flows, and
  operational validation for runtime-affecting changes.
- Implementation MUST map directly to approved tasks. Unplanned refactors or
  scope expansion MUST return to specification or planning before code merges.
- Reviews MUST verify constitution compliance, test evidence, coverage impact,
  security impact, observability impact, and documentation updates before
  approval.

## Governance

This constitution is the highest-priority delivery policy for this repository.
When other local guidance conflicts with it, this document wins until the
conflict is resolved through amendment and synchronization.

- Amendments MUST be proposed by updating this file through
  `/speckit.constitution` or an equivalent reviewed change. The amendment MUST
  include a Sync Impact Report, the semantic-version rationale, and the
  dependent artifact updates listed below before merge.
- Constitution versioning MUST use semantic versioning:
  - MAJOR for removed principles, materially weakened rules, or governance
    changes that invalidate existing delivery expectations.
  - MINOR for new principles, new mandatory sections, or materially expanded
    obligations for specs, plans, tasks, or implementation.
  - PATCH for clarifications, wording improvements, examples, or sync-only
    changes that do not alter obligations.
- Every implementation plan review MUST contain an explicit Constitution Check
  with pass or fail status for each applicable principle. Missing or failed
  checks block implementation until resolved or explicitly approved as a dated
  exception.
- Every constitution amendment MUST synchronize the following artifacts in the
  same change when they are affected:
  - `.specify/templates/spec-template.md`
  - `.specify/templates/plan-template.md`
  - `.specify/templates/tasks-template.md`
  - command prompt files under `.specify/templates/commands/`
  - `README.md`
  - `docs/quickstart.md`
  - any feature-specific quickstart or operator guidance that changed meaning
    under the new rules
- Dependent artifacts MUST NOT contradict this constitution. If an artifact is
  intentionally deferred, the Sync Impact Report MUST mark it as pending with a
  reason and owner.

**Version**: 1.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22
