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
- After implementation, create the spec-specific post-implementation QA guide
  and QA environment file in the active spec directory:
  - `qaNNN.md`
  - `.env.qaNNN`
- The QA guide MUST follow the detail level of
  `specs/008-production-audit-debugging/qa008.md`, with copy/paste setup,
  seed data, manual verification steps, expected outputs, negative-path checks,
  security/redaction checks, automated evidence, troubleshooting, and related
  files.
- The QA environment file MUST follow the shape of
  `specs/008-production-audit-debugging/.env.qa008`, using a dedicated
  `multi_agent_platform_qaNNN` database, local-principal auth, fake
  spec-specific secret references, and `.data/qaNNN-artifacts` storage.

## Completion Gate

Implementation is incomplete if tests, documentation, constitution-required
runtime validation, `qaNNN.md`, `.env.qaNNN`, or the QA document validator are
missing.

Before reporting completion, run:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```
