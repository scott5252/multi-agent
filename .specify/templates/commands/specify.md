# /speckit.specify

Create or update a feature specification that is fully aligned with
`.specify/memory/constitution.md`.

## Mandatory Output Requirements

- Produce prioritized, independently testable user stories with measurable
  success criteria and explicit edge cases.
- Keep the specification focused on user value and constraints rather than
  implementation details.
- Include a `Constitution Alignment` section that explicitly states whether each
  of the following is in scope and why:
  - durability and recovery
  - tenant isolation and fair use
  - contracts, versioning, and lineage
  - security, secrets, and tool access
  - artifact and data storage
  - approval and resume behavior
  - observability and auditability
- Include `Testing Instructions`, `PR Review Guidance`, and
  `Documentation Impact`, including required `README.md` and quickstart changes.

## Clarification Rules

- Ask clarifying questions only when unresolved choices materially change scope,
  security, tenant boundaries, approval behavior, or durability guarantees.
- Prefer bounded questions and make reasonable assumptions when risk is low.

## Completion Gate

The spec is incomplete if it is missing constitution alignment, testing
instructions, PR review guidance, or documentation impact.
