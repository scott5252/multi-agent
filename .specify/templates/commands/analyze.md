# /speckit.analyze

Analyze `spec.md`, `plan.md`, and `tasks.md` for consistency, missing coverage,
and constitution compliance before implementation.

## Required Checks

- Treat any conflict with `.specify/memory/constitution.md` as critical.
- Verify coverage for durability, tenant isolation, lineage, version pinning,
  secrets and tool policy, artifact storage, approval flows, observability,
  testing, and documentation when those concerns are in scope.
- Flag requirements or success criteria that have no corresponding design or
  task coverage.
- Flag plans or tasks that omit README, quickstart, coverage, or operational
  validation work when required.

## Output Expectations

- Report findings by severity with concrete artifact references.
- Prefer actionable fixes over generic summaries.
