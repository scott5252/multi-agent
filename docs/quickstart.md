# Multi-Agent AI Platform Quickstart

## Purpose

Use this repository to define, plan, and implement a production-grade
multi-agent AI platform without drifting from the governing constitution.

## Before You Start

1. Read the
   [constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md).
2. Review the
   [architecture overview](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md).
3. Check the
   [spec-kit breakdown](/Users/scottcornell/src/my-projects/multi-agent/docs/spec-kit-breakdown.md)
   for recommended feature sequencing.

## Delivery Flow

1. Run `/speckit.specify` to create a spec with:
   - prioritized user stories
   - measurable success criteria
   - constitution impact for durability, tenancy, versioning, secrets,
     artifacts, approvals, observability, and security
   - testing instructions, PR review guidance, and documentation impact
2. Run `/speckit.plan` to create a plan with:
   - constitution check results
   - explicit recovery, tenant, lineage, version pinning, secret/tool-policy,
     artifact, approval, observability, testing, documentation, and security
     decisions
   - generated `research.md`, `data-model.md`, `contracts/`, and
     feature-specific `quickstart.md` when needed
3. Run `/speckit.tasks` to create:
   - dependency-ordered, file-specific tasks
   - test-first tasks where practical
   - documentation, `README.md`, and quickstart update tasks
   - operational validation tasks for runtime-affecting behavior
4. Run `/speckit.implement` only after the spec, plan, and tasks align.

## Definition Of Ready For Implementation

- Constitution check passes or approved exceptions are documented with dates.
- Durability, retry, compensation, and idempotency decisions are explicit.
- Tenant isolation, fairness, and quota handling are explicit.
- Parent-child lineage and version-bundle pinning are explicit.
- Secret handling, tool egress, and artifact storage are explicit.
- Approval/resume behavior and observability requirements are explicit where
  relevant.
- Test strategy supports at least 90 percent unit-test coverage for the
  implemented scope.
- `README.md`, quickstart, and other affected docs are identified for updates.

## Review Expectations

- Reviewers verify constitution compliance, not just code correctness.
- Runtime-affecting features need validation evidence for recovery,
  observability, and operational behavior.
- Documentation updates are part of the definition of done.
