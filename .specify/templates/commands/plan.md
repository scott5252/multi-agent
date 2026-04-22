# /speckit.plan

Generate an implementation plan that turns an approved specification into a
constitution-compliant design package.

## Required Inputs

- approved `spec.md`
- active `.specify/memory/constitution.md`
- repository context needed to choose concrete files and modules

## Mandatory Output Requirements

- Fill the plan template completely.
- Produce a `Constitution Check` with pass or fail status for every core
  principle.
- Document explicit decisions for:
  - durability and failure recovery
  - tenant isolation, fairness, and quotas
  - subworkflow boundaries and parent-child lineage
  - version-bundle pinning and contract compatibility
  - secret management, delegated credentials, and tool policy
  - artifact storage and retention
  - approval, wait-state, and resume behavior where relevant
  - observability, audit, replay, and operator debugging
  - test strategy, including failure and recovery testing
  - documentation tasks and security review notes
- Generate or update `research.md`, `data-model.md`, `contracts/`, and
  `quickstart.md` when the feature requires them.

## Gate Rules

- Stop on unresolved constitution violations.
- Record any approved exception with rationale, approver, and expiration or
  removal condition.
- Do not produce vague structure decisions; use real repository paths whenever
  possible.
