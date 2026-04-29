# Guided Admin Workflow Builder PR Notes

## Implementation Summary

- Added guided builder document fields while preserving existing workflow
  registry draft payload compatibility.
- Added editor metadata, lookup response, graph preview, validation finding,
  reference readiness, required test, conflict, and publish gate schemas.
- Added graph projection, scoped reference readiness, publish gate, and builder
  observability helpers.
- Added JSON routes for editor lookups, graph preview, revision history,
  restore, copy, publish gate, and publish-gate-aware publication.
- Added server-rendered create, editor, revision history, publish gate, and
  published version detail views.
- Added published bundle summaries for source revision, publish gate digest,
  prompt/profile pins, routing provenance, skill pins, subworkflow pins,
  contract compatibility, approval summary, graph summary, and test evidence.

## Risk Notes

- Reference readiness adapters currently produce safe local summaries from the
  builder document and visible subworkflow checks; deeper prompt/profile,
  model-routing, provider catalog, and test-bench integrations remain behind
  the same typed contract.
- No database migration was added; compact evidence is stored in existing JSON
  fields.
- Server-rendered forms expose fallback controls, while JSON mutation routes
  remain authoritative for structured payloads.

## QA Evidence Checklist

- [x] Valid publish result covered by unit, contract, and service tests.
- [x] Blocked publish categories covered by publish gate tests.
- [x] Stale save conflict returns `409` with no revision in service and route tests.
- [x] Tenant/platform isolation covered by auth policy and route tests.
- [x] Graph cycle policy covered by graph preview tests.
- [x] Prompt/profile/provider/skill/subworkflow/test readiness covered by reference and validation tests.
- [x] Safe audit and observability payload redaction covered by builder tests.
- [x] Docs, README links, and QA013 guide validation checked.

## Timed Acceptance Results

- Authoring under 25 minutes: manual reviewer timing steps documented in `specs/013-admin-workflow-builder/qa013.md`.
- Blocked reason identification under 2 minutes: manual reviewer timing steps documented in `specs/013-admin-workflow-builder/qa013.md`.
- Scoped endpoint p95 checks: bounded request tests and QA013 endpoint checks documented; manual p95 capture remains reviewer evidence.
- Publish outcome within 2 minutes: ready publish flow documented in QA013; automated publish-gate behavior covered by tests.

## Automated Checks

- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed, 658 files already formatted
- `uv run mypy src`: passed, no issues in 244 source files
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: passed, 675 tests, 9 warnings, 90.14% coverage
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/013-admin-workflow-builder`: passed

## Rollback Considerations

The change is additive. Rollback can disable the new UI links and routes while
existing workflow registry draft, validation, publish, version detail, and
sharing behavior continue to use the original tables and bundle artifacts.
