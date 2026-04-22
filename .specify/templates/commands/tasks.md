# /speckit.tasks

Generate a dependency-ordered `tasks.md` that is directly executable and
traceable to the approved spec and plan.

## Mandatory Output Requirements

- Organize tasks by user story in priority order after setup and foundational
  phases.
- Use exact file paths in every implementation or documentation task.
- Include test-first tasks where behavior can be automated. If a test is
  omitted, cite the plan-approved justification.
- Include documentation tasks, `README.md` update tasks, and quickstart
  validation tasks.
- Include explicit tasks for tenant isolation, version pinning, secrets,
  artifact storage, approval/resume behavior, and operational validation when
  those concerns are in scope.
- Include observability, audit, replay, quota, or failure-recovery validation
  tasks for runtime-affecting features.

## Task Quality Rules

- Keep tasks small, reviewable, and dependency-aware.
- Mark `[P]` only for work that touches different files or isolated modules.
- Make story phases independently testable and shippable.
- Keep final polish tasks focused on docs, coverage evidence, security closure,
  and operational validation rather than vague cleanup.
