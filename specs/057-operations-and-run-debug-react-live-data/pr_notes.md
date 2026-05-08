# Reviewer Notes: Spec 057 Operations And Run Debug React Live Data

## Scope

Spec 057 replaces deterministic operations workbench and run-debug React
payloads with live service and repository-backed projections for health,
pressure, likely causes, run debug, reliability, logs, and durable export
evidence.

## Implementation Notes

- Operations workbench builders now require `OperationsConsoleService` and read
  live dashboard/log evidence before building React contracts.
- Run-debug builders resolve the requested run ID from live runtime and audit
  evidence, returning 404 for missing or unauthorized runs instead of rendering
  a fixed fallback run.
- Export actions call the existing operations export service and return safe
  `operations-export:<id>` references without storage URLs or local paths.
- Tenant workbench views hide platform-only provider, queue, database, worker,
  and storage pressure while still showing tenant-visible live evidence.
- Scanner guardrails now treat old operations QA029 markers as blocking
  regressions in production workbench surfaces.
- QA057 seed data persists Acme operations rows while leaving Globex empty for
  isolation checks.

## QA Notes

- QA environment: `specs/057-operations-and-run-debug-react-live-data/.env.qa057`
- Seed script: `scripts/qa/seed_operations_qa057.py`
- Post-UI verifier: `scripts/qa/verify_operations_qa057.py`
- Main browser route: `/admin/app/operations`
- Playwright action: sign in as `tenant-admin-acme`, load operations, click
  `Export evidence`, verify a completed `operations-export:` artifact
  reference, and confirm the verifier sees a new export audit row with checksum
  metadata.

## Documentation Notes

Reviewed `README.md` and `docs/quickstart.md`. No shared project-level command
or onboarding update is required because qa057 adds feature-specific QA
commands and docs only.

## Safety Notes

- No real provider calls are used.
- No external connectors or Telegram calls are used.
- QA secrets use the `qa057/` static reference prefix.
- Browser and API output must not include raw prompts, completions, memory
  content, authorization headers, credential values, storage file URIs, local
  filesystem paths, stack traces, private messages, connector details, or
  unauthorized tenant rows.

## Commit Notes

No intermediate commit is required for this spec. The autopilot is intentionally
continuing in the dirty worktree until the full remove-mock-data sequence is
complete and the user commits.
