# /speckit.implement

Execute approved tasks without drifting from the constitution, spec, or plan.

## Mandatory Execution Rules

- Implement only work that is traceable to approved `tasks.md` entries.
- Keep changes small and safe; return to specification or planning before adding
  unplanned scope.
- Preserve tenant isolation, version pinning, secret handling, artifact
  boundaries, approval durability, and observability guarantees for any in-scope
  feature.
- Run and record the tests required by the plan, including recovery or
  operational validation where applicable.
- Update docs, `README.md`, quickstarts, and task checkboxes as the approved
  work is completed.

## Completion Gate

Implementation is incomplete if tests, documentation, or constitution-required
runtime validation are missing.
