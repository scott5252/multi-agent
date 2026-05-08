# UI Contract: Test Bench Live Data

## Route Family

The existing React admin route family remains the browser entry point:

- `/admin/app/test-bench`
- `/admin/app/test-bench/bootstrap.json`
- `/admin/app/test-bench/suites`
- `/admin/app/test-bench/suites/{suite_id}`
- `/admin/app/test-bench/suites/{suite_id}/cases`
- `/admin/app/test-bench/suites/{suite_id}/runs`
- `/admin/app/test-bench/runs.json`
- `/admin/app/test-bench/runs/{run_id}.json`
- `/admin/app/test-bench/gates.json`
- `/admin/app/test-bench/gates/{gate_id}/refresh`
- `/admin/app/test-bench/artifacts/{artifact_reference_id}.json`
- `/admin/app/test-bench/audit.json`

All JSON endpoints must be backend-owned, tenant-scoped, redaction-safe, and generated from Pydantic schemas into `frontend/admin/src/api/generated/reactAdminApi.ts`.

## Dashboard Envelope

`TestBenchDashboard` must include:

- `page_id`, `title`, `description`, `scope`
- `provenance`: live repository source, generated timestamp, scope, and bounded source counts
- `empty_state`: null when live rows exist, otherwise a truthful empty/unavailable state
- `sections`: suite, runs, artifacts, gates, audit, and diagnostics section summaries
- `summary_cards`: live counts for suites, cases, runs, failing runs, missing gates, artifacts, or empty zero counts
- `gate_alerts`: live publish-gate evidence or empty list
- `suites`: live suite summaries or empty list
- `selected_suite`: live selected suite detail or null when empty
- `recent_runs`: live run summaries or empty list
- `audit_timeline`: live safe audit records or empty list
- `refresh` and backend-provided actions

The frontend must render an empty-state panel when `selected_suite` is null, rather than assuming a fixed suite exists.

## Suite And Case Detail

Suite detail must include persisted suite summary, target binding, run launcher metadata, case summaries, assertion definitions, and authorized actions. Case data must use safe fixture and expected contract summaries only.

Required denied/unavailable behavior:

- Unknown suite id in the active tenant returns 404 or an unavailable envelope.
- Cross-tenant suite id fails closed.
- Suite without active cases renders unavailable launch state.
- Stale suite/case revision returns stale conflict metadata.

## Run Detail

Run detail must include persisted run summary, progress snapshot, safe diagnostics, trace step summaries, artifact metadata, publish-gate relation, and audit reference. Raw transcripts, prompts, completions, run payloads, memory contents, stack traces, and local paths must never render.

Required denied/unavailable behavior:

- Unknown run id in the active tenant returns 404 or unavailable state.
- Cross-tenant run id fails closed.
- Runs without steps render pending or unavailable progress.
- Artifact references without safe metadata render artifact-unavailable state.

## Mutation Result

`TestBenchMutationResult` must support:

- accepted persisted suite save, case save, run launch, or gate refresh evidence
- stale conflict with submitted and current revision
- validation error for real probes, missing cases, malformed target references, or unsafe text
- denied or unavailable state when authorization or live records are absent
- optional refreshed suite, case, run, or gate evidence
- audit reference id and toast hints where safe

Playwright must perform at least one mutation through this contract and post-UI validation must prove the persisted state.

## Redaction Contract

The following strings and data categories are forbidden in React responses, screenshots, logs, exports, and QA docs:

- raw prompt
- raw completion
- raw transcript
- resolved credential
- authorization header
- provider token
- private message
- memory contents
- connector request or response
- raw tool output
- stack trace
- storage path
- local filesystem paths
- unauthorized tenant labels
- unsafe artifact contents

Schema validators and tests must reject these markers in production response models.
