# Quickstart: Production Audit And Debugging

## Prerequisites

- Python 3.12 and `uv`
- PostgreSQL available through the repository's normal development setup
- Auth0 or deterministic local principals configured for admin/operator tests

## Setup

```bash
uv sync
uv run alembic upgrade head
```

## Run The API And Worker

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
uv run python -m multi_agent_platform.workers.main
```

## Validate Audit Capture

1. Start a representative workflow run that completes successfully.
2. Start a representative workflow run that fails after at least one runtime
   decision.
3. Start a workflow that includes a child run, a retry or resume event, an
   agent handoff, a contract validation, a memory write, a tool decision, a
   model selection, a notification attempt, and a secret-reference request.
4. Confirm each run has a trace id and chronological timeline events for
   acceptance, queueing, start, wait/resume when applicable, completion,
   cancellation, failure, retry, or timeout.

## Inspect As An Administrator

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/{workflow_run_id}/timeline?tenant_id={tenant_id}"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/debug-search?tenant_id={tenant_id}&status=failed"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/{workflow_run_id}/replay?tenant_id={tenant_id}"
```

## Review Expected Evidence

- Timeline includes lifecycle events in sequence with status after each event.
- Failed runs include failed stage, safe failure reason, related event, and
  recommended investigation category.
- Handoffs, validations, memory writes, tool usage, model selections,
  notifications, and secret-access decisions are linked to timeline events.
- Parent-child lineage and retries are visible only within the authorized
  tenant scope.
- Version-bundle view shows the pinned execution bundle and configuration refs
  that governed the run at acceptance.
- Notification delivery state shows destination category, status, attempts,
  latest attempt time, and safe failure reason.
- Secret-access audit metadata shows requester, reference metadata, policy
  outcome, time, run context, and reason without raw secret values.
- Capture gaps appear as unavailable markers instead of silent omissions.

## Validate Redaction And Authorization

1. Request the same run as an unauthorized user and confirm the response fails
   closed.
2. Confirm the denied inspection attempt is audit logged.
3. Search for a cross-tenant run id and confirm protected details are not
   disclosed.
4. Confirm timelines, logs, metrics, traces, exports, README guidance, and PR
   notes contain no raw secrets, credential values, unauthorized prompt text,
   or unauthorized memory content.

## Create A Debug-Evidence Export

```bash
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  "http://127.0.0.1:8000/admin/runs/{workflow_run_id}/exports" \
  -d '{
    "tenant_id": "{tenant_id}",
    "recipient_scope": "tenant_auditor",
    "lineage_scope": "authorized_children",
    "included_sections": ["timeline", "trace", "lineage", "bundle", "notifications", "secret_access"],
    "reason": "incident review"
  }'
```

Confirm the export record is audited before the artifact becomes available and
that the artifact uses the same redaction rules as API responses.

## Test Commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/audit tests/unit/observability tests/contract/test_production_audit_debugging_contract.py
uv run pytest tests/integration/runtime/test_audit_capture_runtime.py tests/integration/runtime/test_timeline_completeness.py
uv run pytest tests/performance/audit/test_run_inspection_latency.py
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Review Notes Checklist

- Timeline completeness across successful, failed, cancelled, waiting,
  resumed, retried, and timed-out runs.
- Runtime decision capture for handoffs, validations, memory writes, tools,
  models, notifications, and secret access.
- Tenant and role authorization for timelines, traces, lineage, version
  bundles, exports, and denied attempts.
- Sensitive-data classification and redaction behavior.
- Append-only correction, redaction, and supersession behavior.
- Lookup/search latency evidence for p95 <= 2 seconds and p95 <= 5 seconds.
- README and operator guidance for production debugging.

## Implementation Verification Notes

The implemented admin endpoints match the paths in this quickstart:
`/admin/runs/debug-search`, `/admin/runs/{workflow_run_id}/timeline`,
`/admin/runs/{workflow_run_id}/replay`, `/admin/runs/{workflow_run_id}/lineage`,
`/admin/runs/{workflow_run_id}/bundle`, and
`/admin/runs/{workflow_run_id}/exports`. Export creation returns safe metadata
with status, included/excluded sections, artifact references when available,
and safe failure reasons.
