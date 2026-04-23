# Quickstart: Admin Workflow Studio And Registry

## Purpose

Validate the full workflow-registry feature in local-principal mode:

- create and save a draft
- open the embedded UI with browser-friendly local login
- review field-help modals
- validate draft readiness
- publish an immutable version bundle
- inspect version detail
- grant tenant access to a platform-scoped published version

## 1. Prepare The Environment

```bash
uv sync
cp specs/003-workflow-studio-registry/.env.qa003 .env
docker compose up -d postgres
uv run alembic upgrade head
```

## 2. Run The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 3. Open The UI

Open:

[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui)

Expected result:

- local browser login works without a header extension
- `platform-admin` can see platform drafts and versions
- `tenant-admin-acme` can see tenant drafts and granted platform versions

## 4. Create A Draft

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows \
  -d '{
    "scope_type": "platform",
    "workflow_kind": "subworkflow",
    "slug": "document-extraction",
    "display_name": "Document Extraction",
    "document": {
      "workflow_key": "document-extraction",
      "display_name": "Document Extraction",
      "description": "Extract structured facts from uploaded documents.",
      "workflow_kind": "subworkflow",
      "entry_node_key": "triage-node",
      "roles": [
        {
          "role_key": "triage-role",
          "display_name": "Triage Role",
          "purpose": "Assess the document.",
          "input_contract_key": "inbound",
          "output_contract_key": "result",
          "skill_bindings": [
            {
              "binding_key": "triage-binding",
              "skill_slug": "triage-agent",
              "skill_version": "2026.04.1",
              "purpose": "Assess"
            }
          ]
        }
      ],
      "contracts": [
        {"contract_key": "inbound", "json_schema": {"type": "object"}},
        {"contract_key": "result", "json_schema": {"type": "object"}}
      ],
      "nodes": [
        {
          "node_key": "triage-node",
          "node_type": "role",
          "display_name": "Triage",
          "role_key": "triage-role"
        }
      ],
      "edges": [],
      "join_policies": [],
      "approval_gates": [],
      "subworkflow_refs": []
    }
  }'
```

Expected result:

- status `201`
- `workflow_draft_id` and `workflow_lineage_id` returned
- `current_revision_number` is `1`

## 5. Validate The Draft

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/validate
```

Expected result:

- status `200`
- `status` is `passed` when the draft is publish-ready
- blocked drafts return field-targeted findings such as skill version, quorum,
  approval gate, or subworkflow ref errors

## 6. Publish The Draft

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/drafts/<workflow_draft_id>/publish \
  -d '{
    "validation_result_id": "<validation_result_id>"
  }'
```

Expected result:

- status `201`
- `workflow_version_bundle_id` returned
- `display_version` is `v1`
- `compiled_bundle_digest` returned
- the source draft becomes immutable

## 7. Inspect Version Detail

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  http://127.0.0.1:8000/admin/workflows/versions/<workflow_version_bundle_id>
```

Expected result:

- status `200`
- digest, compiler version, and immutable lineage metadata are present

Browser route:

[http://127.0.0.1:8000/admin/workflows/versions/<workflow_version_bundle_id>/detail](http://127.0.0.1:8000/admin/workflows/versions/<workflow_version_bundle_id>/detail)

## 8. Grant Tenant Access

```bash
curl \
  -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  -X POST \
  http://127.0.0.1:8000/admin/workflows/versions/<workflow_version_bundle_id>/sharing-grants \
  -d '{
    "grantee_tenant_id": "<tenant_id>"
  }'
```

Expected result:

- status `201`
- the tenant can discover the published platform asset in registry list calls

## 9. Evidence

Latest local evidence recorded on `2026-04-23`:

- full validation: `./scripts/check.sh`
- result: `153 passed`
- coverage: `90.53%`
- measured timings:
  list `7.36 ms`, draft detail `7.23 ms`, save `10.50 ms`, validate `8.90 ms`,
  publish `13.76 ms`, version detail `6.01 ms`

## 10. Troubleshooting

- `401 missing local principal header or cookie`: sign in through
  `/auth/local-login`.
- `409 validation result is stale or failed publish readiness`: rerun
  validation on the latest draft revision.
- `503 compiled bundle artifact persistence failed`: verify artifact storage and
  retry publish.
- tenant cannot see a platform asset: confirm the exact version has a sharing
  grant for that tenant.
