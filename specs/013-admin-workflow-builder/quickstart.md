# Quickstart: Guided Admin Workflow Builder

## Purpose

Validate the guided workflow builder in local-principal mode:

- create a workflow draft through existing registry APIs or the new UI
- edit builder sections without raw JSON
- render graph preview and field-level validation
- validate prompt/profile/provider/skill/subworkflow/test readiness
- reject stale saves
- block unsafe publication
- publish a valid draft as an immutable workflow bundle
- review revision history, published pins, and safe audit evidence

## 1. Prepare The Environment

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
```

Use local-principal auth for reviewer QA:

```bash
export AUTH_MODE=local_principal
```

## 2. Run The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 3. Open The Builder

Open:

[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui)

Expected:

- Platform admin sees platform-scoped drafts and publish controls.
- Tenant admin sees only tenant drafts and granted platform references.
- Registry entries link to draft editor, revision history, and version detail.

## 4. Create Or Open A Draft

Create a draft through the builder create form, or seed one with the existing
JSON API:

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows \
  -d '{
    "scope_type": "platform",
    "workflow_kind": "main_workflow",
    "slug": "guided-builder-smoke",
    "display_name": "Guided Builder Smoke",
    "document": {
      "workflow_key": "guided-builder-smoke",
      "display_name": "Guided Builder Smoke",
      "description": "Reviewer smoke workflow.",
      "workflow_kind": "main_workflow",
      "entry_node_key": "intake",
      "roles": [],
      "contracts": [],
      "nodes": [
        {
          "node_key": "intake",
          "node_type": "terminal",
          "display_name": "Intake Complete"
        }
      ],
      "edges": [],
      "join_policies": [],
      "approval_gates": [],
      "subworkflow_refs": []
    }
  }'
```

Expected:

- Status `201`.
- Response includes `workflow_draft_id`, `workflow_lineage_id`, and
  `current_revision_number`.
- Opening `/admin/workflows/drafts/<workflow_draft_id>/editor` shows guided
  sections and the read-only advanced JSON inspector.

## 5. Validate Field-Level Findings

Run validation:

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/validate
```

Expected blocked drafts show field-targeted findings for missing roles,
contracts, prompt/profile references, skill readiness, graph issues, approval
gate gaps, subworkflow compatibility, provider routing readiness, or required
test status.

In the browser, confirm findings anchor to the matching section and graph
element when applicable.

## 6. Check Optimistic Concurrency

1. Open the same draft in two browser sessions.
2. Save from session A.
3. Save stale content from session B.

Expected:

- Session B receives a 409 stale revision conflict.
- No new revision is created for the stale save.
- The UI shows a non-destructive conflict banner with refresh/history options.

## 7. Run Publish Gate

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/publish-gate \
  -d '{
    "validation_result_id": "<validation_result_id>",
    "reason": "Reviewer readiness check"
  }'
```

Expected:

- `status` is `blocked` when any required validation, prompt/profile,
  provider, skill, subworkflow, contract, approval, graph, or test readiness is
  missing or failing.
- The active published bundle remains unchanged.
- Findings include stable `section_key` and `field_path` values.

## 8. Publish A Ready Draft

After fixing blocking findings and rerunning validation and publish gate:

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/publish \
  -d '{
    "validation_result_id": "<validation_result_id>",
    "publish_gate_id": "<publish_gate_id>",
    "reason": "Publish reviewer-approved builder draft"
  }'
```

Expected:

- Status `201`.
- Response includes `workflow_version_bundle_id`, `display_version`, and
  `compiled_bundle_digest`.
- Published bundle summary includes source revision, prompt/profile pins,
  provider routing provenance, skill pins, subworkflow bundle pins, contract
  compatibility, approval summary, graph summary, and test evidence.

## 9. Review Audit And History

Open:

- `/admin/workflows/drafts/<workflow_draft_id>/revisions/ui`
- `/admin/workflows/versions/<workflow_version_bundle_id>/detail`

Expected:

- Revision history shows actor, timestamp, changed sections, validation state,
  restore/copy actions, and safe summaries.
- Version detail traces the bundle to source draft revision and publish gate.
- Audit records exist for create, save, validation, publish gate, blocked
  publish or successful publish, authorization denials, restore, and copy.

## 10. Run Automated Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Targeted reviewer suites once implemented:

```bash
uv run pytest tests/unit/admin/test_workflow_builder_validation.py
uv run pytest tests/unit/admin/test_publish_gate.py
uv run pytest tests/integration/api/test_admin_workflow_builder_ui.py
uv run pytest tests/integration/workflows/test_workflow_builder_publish_gate.py
uv run pytest tests/contract/test_workflow_builder_contract.py
uv run pytest tests/docs/test_workflow_builder_docs.py
```

## 11. Reviewer QA Evidence

Record in `docs/admin-workflow-builder-pr-notes.md`:

- valid publish result
- blocked publish categories exercised
- stale save conflict result
- tenant/platform authorization checks
- graph cycle policy checks
- prompt/profile/provider/skill/subworkflow/test readiness checks
- safe audit evidence
- coverage percentage
- docs and README update confirmation
