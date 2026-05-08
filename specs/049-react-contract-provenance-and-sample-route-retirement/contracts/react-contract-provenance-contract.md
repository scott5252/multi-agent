# Contract: React Contract Provenance And Sample Route Retirement

## Shared Metadata

React admin contracts may include backend-owned provenance and empty-state metadata using these concepts:

- `source_kind`: `live_repository`, `computed_metadata`, `empty_live_state`, `denied`, or `dependency_unavailable`
- `source_label`: safe source label
- `source_detail`: optional safe source summary
- `empty_state`: optional empty-state descriptor with reason, title, summary, setup hint, and provenance
- `action_metadata`: optional metadata describing revision, idempotency, and request ID sources

## Production Sample Route Retirement

Production-like configuration must satisfy:

- `GET /admin/app/patterns` does not return the React host for a sample data page.
- `GET /admin/app/patterns.json` does not return `AdminPageEnvelope` with `PatternsSampleData`.
- `POST /admin/app/patterns/actions/sample` does not return sample mutation results.
- `POST /admin/app/patterns/export` does not return sample export snapshots.
- `/admin/app/bootstrap.json` navigation omits `/admin/app/patterns`.
- `/admin/app/search.json` command results omit `/admin/app/patterns`.

If a development-only gate is retained, tests must prove it is unavailable by default and explicitly enabled only in local development.

## Redaction Requirements

Contracts, route responses, screenshots, logs, and docs must not include raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, private channel messages, raw run payloads, raw tool payloads, stack traces, local filesystem paths, or unauthorized tenant labels.
