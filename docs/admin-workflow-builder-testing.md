# Guided Admin Workflow Builder Reviewer Testing

## Local Principal Setup

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
export AUTH_MODE=local_principal
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui
```

## Deterministic Smoke Draft

Create a platform draft:

```bash
curl -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST http://127.0.0.1:8000/admin/workflows \
  -d '{"scope_type":"platform","workflow_kind":"main_workflow","slug":"guided-builder-smoke","display_name":"Guided Builder Smoke","document":{"workflow_key":"guided-builder-smoke","display_name":"Guided Builder Smoke","workflow_kind":"main_workflow","entry_node_key":"intake","nodes":[{"node_key":"intake","node_type":"terminal","display_name":"Intake Complete"}],"edges":[],"roles":[],"contracts":[],"join_policies":[],"approval_gates":[],"subworkflow_refs":[]}}'
```

Expected: `201`, `workflow_draft_id`, `workflow_lineage_id`, and
`current_revision_number`.

## Manual Verification

- Registry list shows create action, scope/status filters, validation status,
  publish readiness, draft editor, revision history, publish gate, and version
  detail links when authorized.
- Draft editor shows guided sections, reference readiness, graph preview,
  validation panel, revision link, publish gate link, and read-only JSON
  inspector.
- Graph preview renders stable ids and field paths for nodes and edges.
- Validation findings group by section and include remediation.
- Revision history shows revision number, actor-safe summary, changed sections,
  restore controls, and conflict-safe base revision fields.
- Publish gate shows ready, blocked, stale, or unauthorized status, digest,
  pin summary, required test evidence, and disabled confirmation when blocked.

## Negative Path Checks

- Save with a stale `base_revision_number`; expect `409` and no new revision.
- Submit a draft with a disconnected active node; expect blocking graph finding.
- Add a skill version of `latest`; expect blocking skill readiness.
- Add a required test with `missing`; expect publish gate blocked.
- Tenant principal attempts platform-only publish without grant; expect `403`.
- Oversized builder payload over one megabyte; expect `413`.

## Security And Redaction Checks

- Audit payloads must not include raw prompts, rendered prompt previews,
  provider responses, secret values, tokens, credential values, or unauthorized
  tenant data.
- Hidden lookup references must produce safe denial counts or blocking findings
  without leaking protected names.
- Published bundle summaries store reference ids, digests, and safe summaries
  only.

## Timed Acceptance

- Admin can author a 100-node draft in under 25 minutes with form-backed
  sections and graph preview.
- Reviewer can identify every blocked publish reason in under 2 minutes from
  the publish gate.
- Scoped editor metadata and lookup endpoints should stay under p95 250 ms.
- Publish gate and publish confirmation should return a ready, blocked, or
  retryable outcome within 2 minutes.

## Automated Evidence

```bash
uv run pytest tests/unit/api/test_workflow_builder_schemas.py
uv run pytest tests/unit/admin/test_graph_preview.py
uv run pytest tests/unit/admin/test_workflow_builder_references.py
uv run pytest tests/unit/admin/test_publish_gate.py
uv run pytest tests/unit/api/test_admin_workflow_builder_ui_models.py
uv run pytest tests/contract/test_workflow_builder_contract.py
uv run pytest tests/docs/test_workflow_builder_docs.py
```

Full gate:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
