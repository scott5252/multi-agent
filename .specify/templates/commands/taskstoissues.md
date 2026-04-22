# /speckit.taskstoissues

Convert an approved `tasks.md` into executable issues without losing
constitution-required context.

## Mandatory Requirements

- Preserve task ordering, dependencies, and exact file ownership.
- Keep test-first, documentation, README, quickstart, security, and operational
  validation work visible rather than collapsing it into vague meta-issues.
- Carry over in-scope tenant, version pinning, secret/tool-policy, artifact
  storage, and approval/resume work as first-class issues.

## Output Rule

Each generated issue must remain traceable to the originating task and user
story.
