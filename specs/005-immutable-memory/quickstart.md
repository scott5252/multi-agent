# Quickstart: Immutable Versioned Memory

**Feature**: Immutable Versioned Memory  
**Date**: 2026-04-24

This quickstart describes the validation flow expected after implementation.

## 1. Install Dependencies

```bash
uv sync
```

No new third-party dependency is expected for the initial implementation.

## 2. Prepare PostgreSQL

```bash
uv run alembic upgrade head
```

Confirm the immutable memory migration creates `memory_scopes`,
`memory_versions`, `memory_heads`, `memory_audit_events`, indexes, and the
trigger that rejects updates/deletes on `memory_versions`.

## 3. Start The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 4. Create Initial Memory

```bash
curl -sS -X POST http://127.0.0.1:8000/memory/versions \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme" \
  -d '{
    "scope": {
      "workflow_lineage_id": "workflow.customer-intake",
      "agent_key": "triage-agent",
      "memory_key": "patient-preferences"
    },
    "assert_no_current_head": true,
    "content": {
      "preferred_contact": "sms",
      "removed_fields": {"$memory_removed": ["legacy_phone"]}
    },
    "change_reason": "initial preference capture",
    "change_summary_redacted": "Captured preferred contact channel"
  }'
```

Expected result:

- HTTP 201
- `version_sequence` is `1`
- `previous_memory_version_id` is absent
- `head_advanced` is `true`
- response includes `memory_scope_id` and `memory_version_id`

## 5. Retrieve Current Head

```bash
curl -sS \
  "http://127.0.0.1:8000/memory/head?workflow_lineage_id=workflow.customer-intake&agent_key=triage-agent&memory_key=patient-preferences" \
  -H "X-Tenant-ID: acme"
```

Verify:

- `has_memory` is `true`
- returned head version id matches the initial write
- content hash matches the version response

For a missing scope, the same endpoint must return `has_memory: false` rather
than creating a version.

## 6. Create A Non-Initial Version

Use the current head id from step 5:

```bash
curl -sS -X POST http://127.0.0.1:8000/memory/versions \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme" \
  -d '{
    "scope": {
      "workflow_lineage_id": "workflow.customer-intake",
      "agent_key": "triage-agent",
      "memory_key": "patient-preferences"
    },
    "expected_current_version_id": "{current_memory_version_id}",
    "content": {
      "preferred_contact": "email",
      "removed_fields": {"$memory_removed": ["legacy_phone"]}
    },
    "change_reason": "user updated preference",
    "change_summary_redacted": "Updated preferred contact channel"
  }'
```

Expected result:

- HTTP 201
- `version_sequence` increments to `2`
- `previous_memory_version_id` equals the prior head
- current-head retrieval now returns version 2

## 7. Validate Stale-Head Handling

Repeat step 6 using the old version 1 id as `expected_current_version_id`.

Expected result:

- HTTP 409
- conflict type `stale_expected_head`
- prior versions remain retrievable and unchanged

## 8. Replay And Diff

Replay version 1:

```bash
curl -sS http://127.0.0.1:8000/memory/versions/{version_1_id}/replay \
  -H "X-Tenant-ID: acme"
```

Diff version 1 and version 2:

```bash
curl -sS -X POST http://127.0.0.1:8000/memory/diffs \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme" \
  -d '{
    "base_memory_version_id": "{version_1_id}",
    "compare_memory_version_id": "{version_2_id}"
  }'
```

Verify replay returns the exact version 1 snapshot and diff reports the changed
`/preferred_contact` value.

## 9. Validate Runtime Links

Run the focused runtime memory flow tests after implementation:

```bash
uv run pytest tests/integration/runtime/test_runtime_memory_flows.py -q
```

Required evidence:

- runtime current-head reads pass tenant, workflow lineage, run, step, bundle,
  and bundle digest
- runtime writes store `workflow_run_id`, `run_step_id`, `run_bundle_id`,
  `bundle_digest`, and child `run_lineage_id` when present
- resumed writes with the same idempotency key do not create duplicate versions
- stale resumed work cannot advance the head

## 10. Validate Immutability And Concurrency

```bash
uv run pytest \
  tests/unit/memory/test_service.py \
  tests/unit/memory/test_repository.py \
  tests/integration/db/test_memory_migration.py \
  tests/integration/runtime/test_runtime_memory_flows.py -q
```

Required evidence:

- ORM and raw SQL update/delete attempts on `memory_versions` fail
- racing initial writes produce exactly one accepted first version
- racing non-initial writes produce exactly one accepted successor
- rejected writes do not mutate prior versions or head state

## 11. Validate Audit Redaction

```bash
curl -sS "http://127.0.0.1:8000/memory/audit?memory_scope_id={memory_scope_id}" \
  -H "X-Tenant-ID: acme"
```

Verify audit events include action, actor/source, scope, version ids, hashes,
outcome, timestamps, run/bundle links when available, and redacted summaries.
Audit responses must not include raw memory content.

## 12. Run Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

PR evidence must include the coverage summary, stale-head conflict output,
racing-write test output, replay/diff examples, audit redaction evidence,
runtime bundle/lineage link evidence, README update, and reviewer notes for
immutability and version correctness.
