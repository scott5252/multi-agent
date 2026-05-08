# Data Model: React Contract Provenance And Sample Route Retirement

## Response Provenance

Backend-owned metadata describing why a React contract can be trusted.

Fields:

- `source_kind`: one of `live_repository`, `computed_metadata`, `empty_live_state`, `denied`, or `dependency_unavailable`.
- `source_label`: safe human-readable label naming the repository, computed source, denial, empty setup, or dependency.
- `source_detail`: optional safe summary with additional reviewer context.
- `last_verified_at`: optional timestamp when the backend can safely expose it.
- `evidence`: optional tuple of safe evidence summaries.

Validation:

- Text fields use safe summary validators and cannot include secrets, raw payloads, stack traces, local paths, or unauthorized tenant labels.
- `live_repository` is used only when data is read from durable services or repositories.
- `computed_metadata` requires a named derivation source.

## Empty State Descriptor

Machine-readable and user-facing metadata for truthful empty states.

Fields:

- `reason`: one of `no_live_rows`, `setup_required`, `filtered_empty`, `tenant_scope_empty`, or `dependency_unavailable`.
- `title`: safe title.
- `summary`: safe explanation of the missing setup or unavailable dependency.
- `setup_hint`: optional safe next-step hint.
- `provenance`: required response provenance.

Validation:

- Must not contain fake IDs, sample records, raw exception text, local paths, or unauthorized tenant labels.
- Must distinguish filtered empty state from an empty durable live setup.

## Action Metadata

Backend or generated-client metadata that tells production components how to prepare mutations without fixed QA defaults.

Fields:

- `revision`: optional backend-provided revision value.
- `revision_source`: one of `backend`, `not_required`, or `generated_client_state`.
- `idempotency_key`: optional backend-provided idempotency key.
- `idempotency_source`: one of `backend`, `generated_client_state`, or `not_required`.
- `request_id_source`: one of `backend`, `generated_client_state`, or `not_required`.

Validation:

- Production source must not hardcode `qa0xx` action defaults.
- Client-generated values must be non-domain request metadata and redaction-safe.

## Sample Route Gate

Route availability decision for former sample patterns endpoints.

Fields:

- `route`: route path or operation identifier.
- `production_available`: false for sample patterns.
- `development_gate`: optional setting name if retained for local development.
- `retirement_status`: one of `removed`, `redirected`, `denied`, or `development_only`.
- `validation_evidence`: safe route test and scanner evidence.

Validation:

- Production navigation and command search must not list sample patterns.
- Production-like requests must not return `PatternsSampleData`.

## Contract Generation Evidence

Reviewer-safe evidence that generated TypeScript contracts match backend schemas.

Fields:

- `schema_hash`: generated contract hash.
- `source_models`: tuple of Pydantic model names.
- `generated_file`: repo-relative generated TypeScript path.
- `result`: `passed` or `failed`.

Validation:

- Generated output must not include retired sample route client helpers or fixed QA action defaults.
