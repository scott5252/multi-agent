# Spec-Kit Constitution Prompt

Use the following prompt with `/speckit.constitution` at project start.

```text
/speckit.constitution Create the constitution for a production-grade
multi-agent AI platform called "Multi-Agent AI Platform". This constitution must
govern all future specification, planning, task generation, and implementation
work.

The platform mission:
- Build a multi-agent AI system in Python using FastAPI, LangChain, LangGraph,
  and PostgreSQL.
- Support Web UI, Telegram, and Web API interactions.
- Support reusable agent and subagent workflows with durable parent-child
  execution lineage.
- Use Auth0 for authentication and authorization in production.
- Allow auth to be disabled in development and testing without removing
  authorization behavior from the codebase.
- Enforce tenant isolation and fair use controls in a shared platform.
- Persist workflow state, transactions, and memory durably.
- Store agent memory as immutable, versioned records.
- Pin in-flight runs to immutable workflow, contract, prompt, model, and tool
  policy versions.
- Resolve secrets through a secret manager and control tool egress explicitly.
- Store large artifacts outside the transactional database while keeping metadata
  and auditability in PostgreSQL.
- Model human approvals and pause-resume behavior as durable workflow state.
- Provide auditing, lineage, replay, and debugging in production.
- Allow admin users to design multi-agent workflows, agent roles, skills, and
  communication contracts.

Create the constitution with principles that are explicit, testable, and
enforceable. The constitution should include at least the following principles
and may expand them if needed:

1. Durable By Default
   Every workflow must survive process crashes and resumable execution must be a
   first-class design requirement. Checkpoints, retry behavior, compensation
   behavior, and idempotency for side effects must be defined before
   implementation.

2. Immutable State And Memory
   Shared mutable state is prohibited for workflow coordination. Workflow
   handoffs must use immutable snapshots, and agent memory must be append-only,
   versioned, and auditable.

3. Contract-First Agent Coordination
   Agent-to-agent communication must be governed by explicit schemas and
   semantic validation rules. Contracts must be versioned, reviewed, and tested.

4. Security With Practical Development Ergonomics
   Production paths must use Auth0 and role-based authorization. Development and
   test modes may bypass external identity providers only through explicit
   configuration, while still exercising authorization checks and audit
   behavior.

5. Operability Is A Product Requirement
   Logging, metrics, traces, workflow timelines, lineage, replay support, and
   operator debugging surfaces must be designed into each feature rather than
   added after the fact.

6. Spec-Driven Delivery
   All significant work must begin with spec-kit artifacts. Constitution,
   specify, plan, and tasks outputs are mandatory inputs to implementation.
   Specs must stay aligned with the active constitution.

7. Test And Documentation Discipline
   Every implemented spec must target at least 90 percent unit-test coverage for
   the relevant code. Every spec must include testing instructions, PR review
   guidance, and README updates. New behaviors are incomplete until
   documentation is updated.

8. Clear Ownership And Small Safe Changes
   Plans and tasks must identify exact files, dependency order, and safe
   parallelization. Large speculative refactors that are not traceable to an
   approved spec are disallowed.

9. Tenant Isolation And Fair Scheduling
   Tenant context must be explicit in data models, APIs, worker execution, and
   audits. Shared infrastructure must enforce data isolation, fair scheduling,
   and quota-aware controls to prevent noisy-neighbor failures.

10. Version-Pinned Execution
   Every workflow run MUST pin the exact workflow, subworkflow, contract,
   prompt, model, and tool-policy versions used at start time. Resumes MUST use
   the same pinned bundle unless an explicit, audited migration path is invoked.

11. Secret Hygiene And Controlled Tool Access
   Secrets MUST be stored outside workflow definitions and application logs.
   Tool use MUST be governed by explicit allowlists, outbound access policy, and
   auditable secret references or delegated credentials.

12. Tiered Storage For Large Payloads
   PostgreSQL is the transactional source of truth, not the blob store. Large
   artifacts, transcripts, exports, and attachments MUST use object storage with
   PostgreSQL metadata, retention, and access control.

13. Human Approval Is Durable State
   Workflows that require approval or supplemental user input MUST enter an
   explicit persisted wait state and MUST resume through auditable approval or
   input records instead of ad hoc side channels.

Add a governance section that defines:
- amendment rules,
- semantic versioning for constitution changes,
- compliance review expectations in every plan,
- how templates and command files must stay synchronized with the constitution.

Also require the constitution update process to propagate changes to:
- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`
- command prompt files under `.specify/templates/commands/`
- `README.md` and any quickstart docs when principles change.

Write the constitution so that future `/speckit.plan` outputs must include:
- a constitution check,
- explicit durability and failure-recovery decisions,
- tenant-isolation and quota decisions,
- subworkflow and parent-child lineage decisions,
- version-bundle pinning decisions,
- secret-management and tool-policy decisions,
- artifact-storage decisions,
- approval and resume decisions where relevant,
- observability requirements,
- test strategy,
- documentation tasks,
- security review notes where relevant.

Write the constitution so that future `/speckit.tasks` outputs must include:
- test-first tasks where practical,
- documentation tasks,
- README update tasks,
- tasks for tenant isolation, version pinning, secrets, artifact storage, and
  approval flows when those concerns are in scope,
- operational validation tasks for features that affect runtime behavior.

Use direct language such as MUST, MUST NOT, and SHOULD with rationale. Leave no
placeholder tokens unresolved. Use ISO dates. If any ratification date is
unknown, insert an explicit TODO marker and mention it in the sync impact
report.
```

## Why This Prompt Works

- It matches the official spec-kit constitution phase, which updates
  `.specify/memory/constitution.md` and keeps templates synchronized.
- It hard-codes the non-negotiable project needs into the governing principles.
- It pushes coverage, docs, PR review, and README maintenance into the default
  delivery path instead of treating them as optional cleanup work.
