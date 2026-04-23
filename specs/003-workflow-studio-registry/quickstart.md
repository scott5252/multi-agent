# Quickstart: Admin Workflow Studio And Registry

## Purpose

Validate the workflow registry feature in local-principal mode by creating a
draft, opening the admin editor, using field-help modals, running validation,
publishing an immutable version bundle, and confirming registry visibility rules
for tenant-scoped versus platform-scoped assets.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2
- A local-principal catalog entry with `platform_admin` or `tenant_admin`
  privileges
- A PostgreSQL instance started through the repo’s local infrastructure

## 1. Install dependencies

```bash
uv sync
```

## 2. Prepare environment configuration

```bash
cp .env.example .env
```

Recommended settings for the admin studio quickstart:

- `AUTH_MODE=local_principal`
- `DATABASE_URL=postgresql+psycopg://...`
- `LOCAL_PRINCIPAL_HEADER=X-Local-Principal`
- `LOCAL_PRINCIPAL_CATALOG_JSON` containing at least:
  - one `platform_admin` principal
  - one `tenant_admin` principal for a sample tenant

Expected rules:

- `platform_admin` can create platform-scoped reusable workflows and sharing
  grants.
- `tenant_admin` can create tenant-scoped drafts but cannot publish new
  platform-scoped assets or manage sharing grants.

## 3. Start infrastructure and apply migrations

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

## 4. Run the API and embedded admin Web UI

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected routes after implementation:

- JSON admin API under `/admin/workflows/...`
- embedded admin Web UI under `/admin/workflows`

## 5. Open the workflow studio and inspect field-help modals

Open the editor in a browser while authenticated as a platform admin:

```
http://127.0.0.1:8000/admin/workflows
```

Expected UI behavior:

- the registry page lists drafts and published versions visible to the current
  scope
- starting a new draft opens the draft editor
- every editable input renders a help icon button beside the field label
- selecting the help icon opens a pop-up modal that explains:
  - what the field controls
  - how the value affects validation or runtime behavior
  - example values or common mistakes

Critical fields to verify help modals for:

- workflow scope
- role input and output contracts
- skill version binding
- subworkflow version reference
- join policy strategy
- approval gate approver scope

## 6. Create and save a draft through the API

Create a platform-scoped subworkflow draft:

```bash
curl \
  -H "X-Local-Principal: platform-admin-map" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts \
  -d '{
    "scope_type": "platform",
    "workflow_kind": "subworkflow",
    "slug": "document-extraction",
    "display_name": "Document Extraction",
    "document": {
      "workflow_key": "document-extraction",
      "display_name": "Document Extraction",
      "description": "Extract core facts from uploaded documents.",
      "workflow_kind": "subworkflow",
      "entry_node_key": "extract-agent",
      "roles": [],
      "contracts": [],
      "nodes": [],
      "edges": [],
      "join_policies": [],
      "approval_gates": [],
      "subworkflow_refs": []
    }
  }'
```

Expected result:

- the response returns `workflow_draft_id`, `workflow_lineage_id`, and
  `current_revision_number = 1`
- the new draft appears in the registry list page

## 7. Validate the draft

```bash
curl \
  -H "X-Local-Principal: platform-admin-map" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/validate
```

Expected result:

- validation returns grouped blocking and advisory findings for the current
  draft revision
- drafts with missing contracts, incomplete joins, or unresolved skill runtime
  refs remain ineligible for publish

## 8. Publish an immutable version bundle

```bash
curl \
  -H "X-Local-Principal: platform-admin-map" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/publish \
  -d '{
    "validation_result_id": "<validation_result_id>"
  }'
```

Expected result:

- the response returns a `workflow_version_bundle_id`, `display_version`, and
  `compiled_bundle_digest`
- the published version becomes immutable and the source draft is no longer
  editable
- a compiled bundle artifact is created and linked from the version metadata

## 9. Verify sharing and reuse rules

As a platform admin, grant a tenant access to the platform-scoped published
version:

```bash
curl \
  -H "X-Local-Principal: platform-admin-map" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/versions/<workflow_version_bundle_id>/sharing-grants \
  -d '{
    "grantee_tenant_id": "<tenant_id>"
  }'
```

Expected result:

- the tenant can now discover the platform-scoped asset in registry lookups and
  reference it from a tenant-scoped draft
- revoking the sharing grant removes reference eligibility without altering the
  immutable published bundle

## 10. Validate optimistic concurrency

1. Open the same draft in two browser tabs.
2. Save changes in the first tab.
3. Attempt to save in the second tab without refreshing.

Expected result:

- the stale save is rejected with a conflict response
- the editor prompts the admin to refresh and reapply changes
- the latest committed revision remains authoritative

## 11. Run automated validation

Targeted feature tests:

```bash
uv run pytest \
  tests/unit/admin/test_workflow_registry_service.py \
  tests/unit/admin/test_validation.py \
  tests/unit/admin/test_compiler.py \
  tests/unit/admin/test_field_help.py \
  tests/unit/api/test_workflow_registry_schemas.py \
  tests/unit/db/test_workflow_registry_models.py \
  tests/integration/api/test_admin_workflows_api.py \
  tests/integration/api/test_admin_workflow_ui.py \
  tests/integration/admin/test_publish_compilation.py \
  tests/contract/test_workflow_registry_contract.py
```

Coverage validation:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Static validation:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## 12. Troubleshooting

- `403 Forbidden`: verify the current principal has `tenant_admin` or
  `platform_admin` scope for the requested route or page
- stale save conflict: reload the draft to pick up the latest revision number
- validation fails for skills: verify the referenced skill versions expose the
  runtime refs needed for publish
- publish fails after validation passed: verify the selected validation result is
  still current for the latest draft revision and that the artifact provider is
  healthy
- platform asset not visible to a tenant: verify an active sharing grant exists
  for the published version and tenant
- help modal missing: verify the editor metadata response includes a
  `FieldHelpDefinition` entry for that field path
