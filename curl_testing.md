# Sequential curl API Test Plan

This document is a sequential JSON/API walkthrough for specs 001 through 025.
It is based on the implemented FastAPI route inventory in
`multi_agent_platform.api.main` and the feature QA/integration tests.

The commands assume a local QA database has been migrated and seeded with the
Acme and Globex tenants used throughout the specs. Server-rendered admin UI
pages are intentionally excluded because they return HTML, not JSON. One SSE
endpoint is included as a special non-JSON stream because it is part of the API
surface.

## 0. Local Setup

Run the API in one terminal:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Run the curl walkthrough from another terminal:

```bash
command -v jq >/dev/null || echo "Install jq before running variable-capture steps"
export BASE_URL="http://127.0.0.1:8000"
export ACME_TENANT_ID="11111111-1111-1111-1111-111111111111"
export GLOBEX_TENANT_ID="22222222-2222-2222-2222-222222222222"
export PLATFORM_HEADER="X-Local-Principal: platform-admin"
export ACME_HEADER="X-Local-Principal: tenant-admin-acme"
export GLOBEX_HEADER="X-Local-Principal: tenant-admin-globex"
export AUDITOR_HEADER="X-Local-Principal: auditor"
export JSON_HEADER="Content-Type: application/json"
export TELEGRAM_SECRET="local-dev-secret"
```

Every response example below shows the expected HTTP status and a representative
JSON body. UUIDs, timestamps, revision tokens, digests, and trace IDs vary.

## 1. Foundation And Auth

### 1.1 GET /health/live

```bash
curl -sS "$BASE_URL/health/live"
```

Expected `200`:

```json
{"service":"multi-agent-platform","status":"live","version":"0.1.0","checked_at":"2026-05-04T12:00:00+00:00"}
```

### 1.2 GET /health/ready

```bash
curl -sS "$BASE_URL/health/ready"
```

Expected `200`:

```json
{"service":"multi-agent-platform","status":"ready","checks":[{"name":"database","required":true,"status":"ready","detail":null,"checked_at":"2026-05-04T12:00:00+00:00"}],"checked_at":"2026-05-04T12:00:00+00:00"}
```

### 1.3 GET /version

```bash
curl -sS "$BASE_URL/version"
```

Expected `200`:

```json
{"service":"multi-agent-platform","version":"0.1.0","commit_sha":"dev","build_time":"1970-01-01T00:00:00+00:00","python_version":"3.12.0"}
```

### 1.4 GET /dependencies

```bash
curl -sS "$BASE_URL/dependencies"
```

Expected `200`:

```json
{"service":"multi-agent-platform","status":"ready","dependencies":[{"name":"database","required":true,"status":"ready","detail":null,"checked_at":"2026-05-04T12:00:00+00:00"}],"checked_at":"2026-05-04T12:00:00+00:00"}
```

### 1.5 GET /auth/me

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/auth/me"
```

Expected `200`:

```json
{"principal_id":"tenant-admin-acme","auth_mode":"local_principal","auth_provider":"local_principal","tenant_id":"11111111-1111-1111-1111-111111111111","org_id":"org-acme","role_codes":["tenant_admin","tenant_user"],"permission_codes":["tenant:read","tenant:admin"],"scope_type":"tenant","support_override_request_id":null}
```

### 1.6 GET /auth/tenant-context/{tenant_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/auth/tenant-context/$ACME_TENANT_ID"
```

Expected `200`:

```json
{"principal_id":"tenant-admin-acme","auth_mode":"local_principal","auth_provider":"local_principal","tenant_id":"11111111-1111-1111-1111-111111111111","org_id":"org-acme","role_codes":["tenant_admin","tenant_user"],"permission_codes":["tenant:read","tenant:admin"],"scope_type":"tenant","support_override_request_id":null}
```

### 1.7 Missing auth scenario

```bash
curl -sS -i "$BASE_URL/auth/me"
```

Expected `401`:

```json
{"detail":"missing local principal header or cookie"}
```

## 2. Membership And Platform Access Bootstrap

These commands create a persisted principal that later admin and membership
commands reuse.

### 2.1 POST /admin/memberships/api/principals/link

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/memberships/api/principals/link" \
  -d '{"auth0_subject":"auth0|curl-reviewer","email":"Reviewer@Example.com","display_name":"Curl Reviewer"}' \
  | tee /tmp/curl-principal-link.json
export PRINCIPAL_ID="$(jq -r '.principal_identity_id' /tmp/curl-principal-link.json)"
```

Expected `200`:

```json
{"principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","auth_provider":"auth0","external_subject":"auth0|curl-reviewer","subject_display":"auth0|curl-reviewer","display_name":"Curl Reviewer","masked_email":"r***@example.com","status":"active"}
```

### 2.2 POST /admin/memberships/api/invitations

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/memberships/api/invitations" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","email":"Reviewer@Example.com","requested_roles":["tenant_user"],"idempotency_key":"curl-invite-reviewer"}' \
  | tee /tmp/curl-invitation.json
export INVITATION_ID="$(jq -r '.user_invitation_id' /tmp/curl-invitation.json)"
```

Expected `201`:

```json
{"user_invitation_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","tenant_id":"11111111-1111-1111-1111-111111111111","masked_email":"r***@example.com","email_hash":"sha256:example","requested_roles":["tenant_user"],"status":"pending","idempotency_key":"curl-invite-reviewer","replayed":false}
```

### 2.3 POST /admin/memberships/api/invitations replay

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/memberships/api/invitations" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","email":" reviewer@example.COM ","requested_roles":["tenant_user"],"idempotency_key":"curl-invite-reviewer"}'
```

Expected `201`:

```json
{"user_invitation_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","tenant_id":"11111111-1111-1111-1111-111111111111","masked_email":"r***@example.com","requested_roles":["tenant_user"],"status":"pending","idempotency_key":"curl-invite-reviewer","replayed":true}
```

### 2.4 GET /admin/memberships/api/users

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/memberships/api/users?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"principals":[{"principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","external_subject":"auth0|curl-reviewer","status":"active"}],"invitations":[{"user_invitation_id":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","status":"pending"}],"memberships":[],"role_grants":[],"access_history":[],"audit_records":[]}
```

### 2.5 POST /admin/memberships/api/role-grants

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/memberships/api/role-grants" \
  -d '{"principal_identity_id":"'"$PRINCIPAL_ID"'","scope_type":"tenant","tenant_id":"'"$ACME_TENANT_ID"'","role_code":"tenant_admin"}' \
  | tee /tmp/curl-membership-role-grant.json
export MEMBERSHIP_ROLE_GRANT_ID="$(jq -r '.role_grant_id' /tmp/curl-membership-role-grant.json)"
```

Expected `201`:

```json
{"role_grant_id":"cccccccc-cccc-cccc-cccc-cccccccccccc","principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","scope_type":"tenant","tenant_id":"11111111-1111-1111-1111-111111111111","role_code":"tenant_admin","status":"active"}
```

### 2.6 POST /admin/memberships/api/role-grants/{role_grant_id}/revoke

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" \
  "$BASE_URL/admin/memberships/api/role-grants/$MEMBERSHIP_ROLE_GRANT_ID/revoke"
```

Expected `200`:

```json
{"role_grant_id":"cccccccc-cccc-cccc-cccc-cccccccccccc","status":"revoked"}
```

### 2.7 POST /admin/memberships/api/principals/{principal_identity_id}/suspend

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" \
  "$BASE_URL/admin/memberships/api/principals/$PRINCIPAL_ID/suspend"
```

Expected `200`:

```json
{"principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","status":"suspended"}
```

### 2.8 POST /admin/memberships/api/principals/{principal_identity_id}/reactivate

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" \
  "$BASE_URL/admin/memberships/api/principals/$PRINCIPAL_ID/reactivate"
```

Expected `200`:

```json
{"principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","status":"active"}
```

### 2.9 POST /admin/memberships/api/memberships/{tenant_membership_id}/{membership_status}

If your seed data creates a tenant membership, set `TENANT_MEMBERSHIP_ID` before
running this command.

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" \
  "$BASE_URL/admin/memberships/api/memberships/$TENANT_MEMBERSHIP_ID/suspended"
```

Expected `200`:

```json
{"tenant_membership_id":"dddddddd-dddd-dddd-dddd-dddddddddddd","status":"suspended"}
```

### 2.10 GET /admin/tenants/{tenant_id}/role-grants

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/tenants/$ACME_TENANT_ID/role-grants"
```

Expected `200`:

```json
[{"role_grant_id":"cccccccc-cccc-cccc-cccc-cccccccccccc","scope_type":"tenant","tenant_id":"11111111-1111-1111-1111-111111111111","role_code":"tenant_admin","status":"active"}]
```

### 2.11 POST /admin/role-grants

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/role-grants" \
  -d '{"principal_identity_id":"'"$PRINCIPAL_ID"'","scope_type":"tenant","tenant_id":"'"$ACME_TENANT_ID"'","role_code":"tenant_user"}'
```

Expected `201`:

```json
{"role_grant_id":"eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee","principal_identity_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","scope_type":"tenant","tenant_id":"11111111-1111-1111-1111-111111111111","role_code":"tenant_user","status":"active"}
```

### 2.12 POST /admin/support-overrides

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/support-overrides" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","justification":"Curl QA support test","idempotency_key":"curl-support-override-001"}' \
  | tee /tmp/curl-support-override.json
export SUPPORT_OVERRIDE_ID="$(jq -r '.support_override_request_id' /tmp/curl-support-override.json)"
```

Expected `201`:

```json
{"support_override_request_id":"ffffffff-ffff-ffff-ffff-ffffffffffff","target_tenant_id":"11111111-1111-1111-1111-111111111111","status":"pending","expires_at":null}
```

### 2.13 POST /admin/support-overrides/{support_override_request_id}/approve

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/support-overrides/$SUPPORT_OVERRIDE_ID/approve" \
  -d '{"expires_in_hours":2}'
```

Expected `200`:

```json
{"support_override_request_id":"ffffffff-ffff-ffff-ffff-ffffffffffff","target_tenant_id":"11111111-1111-1111-1111-111111111111","status":"approved","expires_at":"2026-05-04T14:00:00Z"}
```

### 2.14 GET /admin/filters/{admin_area}/{filter_id}/restore

This JSON endpoint restores an existing saved filter. Create the filter from
the admin shell first, then set `FILTER_ID`.

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/filters/workflows/$FILTER_ID/restore"
```

Expected `200`:

```json
{"redirect_url":"/admin/workflows/ui?scope_filter=tenant"}
```

## 3. Workflow Registry And Builder APIs

### 3.1 GET /admin/workflows

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows"
```

Expected `200`:

```json
{"items":[]}
```

### 3.2 POST /admin/workflows

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows" \
  -d '{
    "scope_type":"tenant",
    "tenant_id":"'"$ACME_TENANT_ID"'",
    "workflow_kind":"main_workflow",
    "slug":"curl-triage-flow",
    "display_name":"Curl Triage Flow",
    "description":"Sequential curl QA workflow.",
    "document":{
      "workflow_key":"curl-triage-flow",
      "display_name":"Curl Triage Flow",
      "description":"Sequential curl QA workflow.",
      "workflow_kind":"main_workflow",
      "entry_node_key":"triage-node",
      "roles":[{"role_key":"triage-role","display_name":"Triage Role","purpose":"Assess intake","input_contract_key":"inbound","output_contract_key":"result","skill_bindings":[{"binding_key":"triage-binding","skill_slug":"triage-agent","skill_version":"2026.04.1","purpose":"Assess"}]}],
      "contracts":[{"contract_key":"inbound","json_schema":{"type":"object"}},{"contract_key":"result","json_schema":{"type":"object"}}],
      "nodes":[{"node_key":"triage-node","node_type":"role","display_name":"Triage","role_key":"triage-role"}],
      "edges":[],
      "join_policies":[],
      "approval_gates":[],
      "subworkflow_refs":[]
    }
  }' | tee /tmp/curl-workflow-draft.json
export WORKFLOW_DRAFT_ID="$(jq -r '.workflow_draft_id' /tmp/curl-workflow-draft.json)"
export WORKFLOW_LINEAGE_ID="$(jq -r '.workflow_lineage_id' /tmp/curl-workflow-draft.json)"
```

Expected `201`:

```json
{"workflow_draft_id":"11111111-aaaa-aaaa-aaaa-111111111111","workflow_lineage_id":"22222222-aaaa-aaaa-aaaa-222222222222","slug":"curl-triage-flow","display_name":"Curl Triage Flow","scope_type":"tenant","tenant_id":"11111111-1111-1111-1111-111111111111","workflow_kind":"main_workflow","status":"draft","current_revision_number":1}
```

### 3.3 GET /admin/workflows/editor-metadata

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/editor-metadata"
```

Expected `200`:

```json
{"node_types":["role","subworkflow","approval","join","terminal"],"contract_kinds":["workflow_input","workflow_output","handoff"],"field_help":{}}
```

### 3.4 GET /admin/workflows/editor-lookups

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/editor-lookups?workflow_draft_id=$WORKFLOW_DRAFT_ID&lookup_kind=skills&search=triage"
```

Expected `200`:

```json
{"items":[]}
```

### 3.5 GET /admin/workflows/drafts/{workflow_draft_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID"
```

Expected `200`:

```json
{"workflow_draft_id":"11111111-aaaa-aaaa-aaaa-111111111111","slug":"curl-triage-flow","display_name":"Curl Triage Flow","current_revision_number":1,"document":{"workflow_key":"curl-triage-flow","entry_node_key":"triage-node"}}
```

### 3.6 PUT /admin/workflows/drafts/{workflow_draft_id}

```bash
curl -sS -X PUT -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID" \
  -d '{
    "base_revision_number":1,
    "display_name":"Curl Triage Flow Updated",
    "description":"Updated through curl.",
    "change_summary":"Curl save",
    "document":{
      "workflow_key":"curl-triage-flow",
      "display_name":"Curl Triage Flow Updated",
      "description":"Updated through curl.",
      "workflow_kind":"main_workflow",
      "entry_node_key":"triage-node",
      "roles":[{"role_key":"triage-role","display_name":"Triage Role","purpose":"Assess intake","input_contract_key":"inbound","output_contract_key":"result"}],
      "contracts":[{"contract_key":"inbound","json_schema":{"type":"object"}},{"contract_key":"result","json_schema":{"type":"object"}}],
      "nodes":[{"node_key":"triage-node","node_type":"role","display_name":"Triage","role_key":"triage-role"}],
      "edges":[],
      "join_policies":[],
      "approval_gates":[],
      "subworkflow_refs":[]
    }
  }' | tee /tmp/curl-workflow-save.json
export WORKFLOW_REVISION="$(jq -r '.current_revision_number' /tmp/curl-workflow-save.json)"
```

Expected `200`:

```json
{"workflow_draft_id":"11111111-aaaa-aaaa-aaaa-111111111111","display_name":"Curl Triage Flow Updated","current_revision_number":2}
```

### 3.7 GET /admin/workflows/drafts/{workflow_draft_id}/graph-preview

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/graph-preview"
```

Expected `200`:

```json
{"nodes":[{"id":"triage-node","type":"role","label":"Triage"}],"edges":[],"warnings":[]}
```

### 3.8 GET /admin/workflows/drafts/{workflow_draft_id}/revisions

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/revisions"
```

Expected `200`:

```json
{"workflow_draft_id":"11111111-aaaa-aaaa-aaaa-111111111111","current_revision_number":2,"revisions":[{"revision_number":1},{"revision_number":2,"change_summary":"Curl save"}]}
```

### 3.9 POST /admin/workflows/drafts/{workflow_draft_id}/restore

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/restore" \
  -d '{"revision_number":1,"base_revision_number":'"$WORKFLOW_REVISION"',"change_summary":"Restore original curl revision"}'
```

Expected `200`:

```json
{"workflow_draft_id":"11111111-aaaa-aaaa-aaaa-111111111111","current_revision_number":3,"latest_revision":{"change_summary":"Restore original curl revision"}}
```

### 3.10 POST /admin/workflows/drafts/{workflow_draft_id}/copy

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/copy" \
  -d '{"source_revision_number":1,"new_slug":"curl-triage-flow-copy","display_name":"Curl Triage Flow Copy","description":"Copied by curl"}' \
  | tee /tmp/curl-workflow-copy.json
export WORKFLOW_COPY_DRAFT_ID="$(jq -r '.workflow_draft_id' /tmp/curl-workflow-copy.json)"
```

Expected `201`:

```json
{"workflow_draft_id":"33333333-aaaa-aaaa-aaaa-333333333333","slug":"curl-triage-flow-copy","display_name":"Curl Triage Flow Copy","current_revision_number":1}
```

### 3.11 POST /admin/workflows/drafts/{workflow_draft_id}/validate

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/validate" \
  | tee /tmp/curl-workflow-validation.json
export WORKFLOW_VALIDATION_ID="$(jq -r '.validation_result_id' /tmp/curl-workflow-validation.json)"
```

Expected `200`:

```json
{"validation_result_id":"44444444-aaaa-aaaa-aaaa-444444444444","status":"passed","blocking_issue_count":0,"advisory_issue_count":0,"findings":[],"publish_blocking":false}
```

### 3.12 POST /admin/workflows/drafts/{workflow_draft_id}/publish-gate

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/publish-gate"
```

Expected `200`:

```json
{"status":"ready","blocking_issue_count":0,"required_test_summary":{"status":"not_required"}}
```

### 3.13 POST /admin/workflows/drafts/{workflow_draft_id}/publish

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/publish" \
  -d '{"validation_result_id":"'"$WORKFLOW_VALIDATION_ID"'","reason":"Sequential curl publication"}' \
  | tee /tmp/curl-workflow-publish.json
export WORKFLOW_VERSION_BUNDLE_ID="$(jq -r '.workflow_version_bundle_id' /tmp/curl-workflow-publish.json)"
```

Expected `201`:

```json
{"workflow_version_bundle_id":"55555555-aaaa-aaaa-aaaa-555555555555","workflow_lineage_id":"22222222-aaaa-aaaa-aaaa-222222222222","slug":"curl-triage-flow","display_version":"v1","status":"published","compiled_bundle_digest":"sha256:example"}
```

### 3.14 GET /admin/workflows/versions/{workflow_version_bundle_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID"
```

Expected `200`:

```json
{"workflow_version_bundle_id":"55555555-aaaa-aaaa-aaaa-555555555555","slug":"curl-triage-flow","display_version":"v1","status":"published","compiled_bundle_digest":"sha256:example","sharing_grants":[]}
```

### 3.15 POST /admin/workflows/versions/{workflow_version_bundle_id}/sharing-grants

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/sharing-grants" \
  -d '{"grantee_tenant_id":"'"$GLOBEX_TENANT_ID"'"}'
```

Expected `201`:

```json
{"registry_sharing_grant_id":"66666666-aaaa-aaaa-aaaa-666666666666","workflow_version_bundle_id":"55555555-aaaa-aaaa-aaaa-555555555555","grantee_tenant_id":"22222222-2222-2222-2222-222222222222","status":"active"}
```

### 3.16 Workflow stale save scenario

```bash
curl -sS -i -X PUT -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID" \
  -d '{"base_revision_number":1,"display_name":"Stale Save","document":{"workflow_key":"curl-triage-flow","display_name":"Stale Save","workflow_kind":"main_workflow","entry_node_key":"missing","nodes":[]}}'
```

Expected `409` or `422`:

```json
{"detail":"stale revision or invalid workflow document"}
```

## 4. Runtime Orchestration APIs

### 4.1 POST /runtime/runs

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/runtime/runs" \
  -d '{"published_workflow_version_id":"'"$WORKFLOW_VERSION_BUNDLE_ID"'","input":{"message":"Run from curl"},"idempotency_key":"runtime-curl-001","trace_id":"trace-runtime-curl"}' \
  | tee /tmp/curl-runtime-run.json
export RUNTIME_RUN_ID="$(jq -r '.workflow_run_id' /tmp/curl-runtime-run.json)"
```

Expected `202`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","status":"pending","run_bundle_id":"88888888-aaaa-aaaa-aaaa-888888888888","bundle_digest":"sha256:example","created_at":"2026-05-04T12:00:00Z"}
```

### 4.2 GET /runtime/runs/{workflow_run_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID"
```

Expected `200`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","tenant_id":"11111111-1111-1111-1111-111111111111","status":"pending","bundle_digest":"sha256:example","pause_reason":null}
```

### 4.3 GET /runtime/runs/{workflow_run_id}/timeline

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/timeline?limit=100"
```

Expected `200`:

```json
{"items":[{"event_type":"run_started","severity":"info","payload":{"idempotency_key":"runtime-curl-001"},"trace_id":"trace-runtime-curl"}]}
```

### 4.4 GET /runtime/runs/{workflow_run_id}/lineage

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/lineage"
```

Expected `200`:

```json
{"nodes":[],"edges":[]}
```

### 4.5 GET /runtime/runs/{workflow_run_id}/approval-gates

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/approval-gates?status=pending"
```

Expected `200`:

```json
{"items":[]}
```

### 4.6 POST /runtime/runs/{workflow_run_id}/approval-gates/{approval_gate_id}/decisions

```bash
export APPROVAL_GATE_ID="99999999-aaaa-aaaa-aaaa-999999999999"
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/approval-gates/$APPROVAL_GATE_ID/decisions" \
  -d '{"decision":"approved","decision_payload":{"reviewed":true}}'
```

Expected `202`:

```json
{"approval_gate_id":"99999999-aaaa-aaaa-aaaa-999999999999","approval_decision_id":"99999999-aaaa-aaaa-aaaa-999999999999","accepted":true,"status":"approved","resume_queued":true}
```

### 4.7 GET /runtime/runs/{workflow_run_id}/handoffs

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/handoffs"
```

Expected `200`:

```json
{"items":[]}
```

### 4.8 GET /runtime/runs/{workflow_run_id}/side-effects

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/side-effects"
```

Expected `200`:

```json
{"items":[]}
```

### 4.9 POST /runtime/runs/{workflow_run_id}/cancel

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/runtime/runs/$RUNTIME_RUN_ID/cancel" \
  -d '{"reason":"Sequential curl cancellation","child_cancellation_override":"use_workflow_policy"}'
```

Expected `202`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","status":"cancelled","terminal_reason":"Sequential curl cancellation"}
```

## 5. User Interaction Channel APIs

### 5.1 POST /runs

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-curl-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs" \
  -d '{"workflow_id":"published-demo","inputs":{"topic":"rest"},"channel":"web_api"}' \
  | tee /tmp/curl-channel-run.json
export CHANNEL_RUN_ID="$(jq -r '.run_id' /tmp/curl-channel-run.json)"
```

Expected `202`:

```json
{"run_id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","state":"queued","status_url":"/runs/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/status","timeline_url":"/runs/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/timeline","events_url":"/runs/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/events","trace_id":"trace-..."}
```

### 5.2 POST /runs idempotent replay

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-curl-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs" \
  -d '{"workflow_id":"published-demo","inputs":{"topic":"rest"},"channel":"web_api"}'
```

Expected `202`:

```json
{"run_id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","state":"queued","trace_id":"trace-..."}
```

### 5.3 POST /runs idempotency conflict

```bash
curl -sS -i -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-curl-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs" \
  -d '{"workflow_id":"published-demo","inputs":{"topic":"different"},"channel":"web_api"}'
```

Expected `409`:

```json
{"error":{"category":"conflict","message":"Idempotency key already used with different request."},"trace_id":"trace-..."}
```

### 5.4 GET /runs/{run_id}/status

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$CHANNEL_RUN_ID/status"
```

Expected `200`:

```json
{"run_id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","state":"queued","progress_summary":"Queued","latest_timeline_cursor":"1","permitted_actions":["cancel"],"trace_id":"trace-...","terminal_outcome":"none","result_availability":"unavailable","artifact_availability":"none"}
```

### 5.5 GET /runs/{run_id}/timeline

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$CHANNEL_RUN_ID/timeline?limit=100"
```

Expected `200`:

```json
{"items":[{"sequence":1,"event_type":"run_queued","state":"queued","summary":"Run queued","severity":"info","trace_id":"trace-..."}],"next_cursor":null}
```

### 5.6 GET /runs/{run_id}/events

```bash
curl -sS -N -H "$ACME_HEADER" "$BASE_URL/runs/$CHANNEL_RUN_ID/events"
```

Expected `200` SSE stream:

```text
event: timeline
data: {"sequence":1,"event_type":"run_queued","state":"queued"}
```

### 5.7 GET /runs/{run_id}/result

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$CHANNEL_RUN_ID/result"
```

Expected `200`:

```json
{"run_id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","availability":"unavailable","state":"queued","trace_id":"trace-...","summary":null,"structured_result":null}
```

### 5.8 POST /runs/{run_id}/subscriptions

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-sub-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs/$CHANNEL_RUN_ID/subscriptions" \
  -d '{"channel":"web_api","event_types":["terminal"]}'
```

Expected `201`:

```json
{"subscription_id":"bbbbbbbb-bbbb-cccc-dddd-eeeeeeeeeeee","status":"active"}
```

### 5.9 POST /runs/{run_id}/callbacks

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-callback-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs/$CHANNEL_RUN_ID/callbacks" \
  -d '{"callback_url":"https://example.test/callback","event_types":["terminal","artifact_ready"]}'
```

Expected `201`:

```json
{"callback_registration_id":"cccccccc-bbbb-cccc-dddd-eeeeeeeeeeee","status":"active"}
```

### 5.10 POST /runs/{run_id}/cancel

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-cancel-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs/$CHANNEL_RUN_ID/cancel" \
  -d '{"reason":"Sequential curl cancellation"}'
```

Expected `202`:

```json
{"run_id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","state":"canceled","terminal_outcome":"canceled","trace_id":"trace-..."}
```

### 5.11 GET /runs/{run_id}/artifacts with completed run setup

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-complete-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs" \
  -d '{"workflow_id":"completed-demo","inputs":{"topic":"done","_channel_state":"completed"},"channel":"web_api"}' \
  | tee /tmp/curl-channel-completed.json
export COMPLETED_RUN_ID="$(jq -r '.run_id' /tmp/curl-channel-completed.json)"
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$COMPLETED_RUN_ID/result"
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$COMPLETED_RUN_ID/artifacts" | tee /tmp/curl-artifacts.json
export ARTIFACT_ID="$(jq -r '.items[0].artifact_id' /tmp/curl-artifacts.json)"
```

Expected `200` for result:

```json
{"run_id":"dddddddd-bbbb-cccc-dddd-eeeeeeeeeeee","availability":"available","state":"completed","summary":"Completed demo result","structured_result":{"topic":"done"}}
```

Expected `200` for artifacts:

```json
{"run_id":"dddddddd-bbbb-cccc-dddd-eeeeeeeeeeee","items":[{"artifact_id":"eeeeeeee-bbbb-cccc-dddd-eeeeeeeeeeee","name":"result.json","user_facing_type":"json","status":"available","download_url_available":true}]}
```

### 5.12 POST /runs/{run_id}/artifacts/{artifact_id}/download-url

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-download-001" \
  "$BASE_URL/runs/$COMPLETED_RUN_ID/artifacts/$ARTIFACT_ID/download-url"
```

Expected `201`:

```json
{"artifact_id":"eeeeeeee-bbbb-cccc-dddd-eeeeeeeeeeee","download_url":"http://127.0.0.1:8000/artifacts/signed/example","expires_at":"2026-05-04T12:15:00Z","trace_id":"trace-..."}
```

### 5.13 Waiting prompt and POST /runs/{run_id}/approvals/{prompt_id}/decision

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-wait-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs" \
  -d '{"workflow_id":"waiting-demo","inputs":{"topic":"approval","_channel_state":"waiting"},"channel":"web_api"}' \
  | tee /tmp/curl-channel-waiting.json
export WAITING_RUN_ID="$(jq -r '.run_id' /tmp/curl-channel-waiting.json)"
curl -sS -H "$ACME_HEADER" "$BASE_URL/runs/$WAITING_RUN_ID/status" | tee /tmp/curl-channel-waiting-status.json
export PROMPT_ID="$(jq -r '.waiting_prompt.prompt_id' /tmp/curl-channel-waiting-status.json)"
curl -sS -X POST -H "$ACME_HEADER" -H "X-Idempotency-Key: channel-decision-001" -H "$JSON_HEADER" \
  "$BASE_URL/runs/$WAITING_RUN_ID/approvals/$PROMPT_ID/decision" \
  -d '{"action":"approve","prompt_version":1,"decision_payload":{"approved_by":"qa"}}'
```

Expected `202`:

```json
{"accepted":true,"decision_id":"ffffffff-bbbb-cccc-dddd-eeeeeeeeeeee","run_status":{"run_id":"eeeeeeee-bbbb-cccc-dddd-eeeeeeeeeeee","state":"queued","waiting_prompt":null},"trace_id":"trace-..."}
```

### 5.14 Cross-tenant channel denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" "$BASE_URL/runs/$CHANNEL_RUN_ID/status"
```

Expected `404`:

```json
{"error":{"category":"not_found","message":"run not found"},"trace_id":"trace-..."}
```

### 5.15 POST /channels/telegram/link-token

This channel-level helper issues a Telegram link token for the authenticated
tenant principal. The admin Telegram section later exercises the admin-scoped
link-token lifecycle.

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/channels/telegram/link-token" \
  | tee /tmp/curl-channel-telegram-link-token.json
export CHANNEL_TELEGRAM_LINK_TOKEN="$(jq -r '.link_token' /tmp/curl-channel-telegram-link-token.json)"
```

Expected `201`:

```json
{"link_token":"link_...","expires_at":"2026-05-04T12:10:00Z","channel":"telegram"}
```

## 6. Memory APIs

### 6.1 POST /memory/versions

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/memory/versions" \
  -d '{"scope":{"workflow_lineage_id":"workflow.demo","agent_key":"triage","memory_key":"prefs"},"assert_no_current_head":true,"content":{"preferred_contact":"sms"},"change_summary_redacted":"Captured preference"}' \
  | tee /tmp/curl-memory-first.json
export MEMORY_SCOPE_ID="$(jq -r '.scope.memory_scope_id' /tmp/curl-memory-first.json)"
export MEMORY_VERSION_1_ID="$(jq -r '.version.memory_version_id' /tmp/curl-memory-first.json)"
```

Expected `201`:

```json
{"scope":{"memory_scope_id":"11111111-bbbb-bbbb-bbbb-111111111111","workflow_lineage_id":"workflow.demo","agent_key":"triage","memory_key":"prefs"},"version":{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222","previous_memory_version_id":null},"head_advanced":true}
```

### 6.2 GET /memory/head

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/memory/head?workflow_lineage_id=workflow.demo&agent_key=triage&memory_key=prefs"
```

Expected `200`:

```json
{"has_memory":true,"scope":{"memory_scope_id":"11111111-bbbb-bbbb-bbbb-111111111111"},"head":{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"},"content":{"preferred_contact":"sms"}}
```

### 6.3 POST /memory/versions second write

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/memory/versions" \
  -d '{"scope":{"workflow_lineage_id":"workflow.demo","agent_key":"triage","memory_key":"prefs"},"expected_current_version_id":"'"$MEMORY_VERSION_1_ID"'","content":{"preferred_contact":"email"},"change_summary_redacted":"Updated preference"}' \
  | tee /tmp/curl-memory-second.json
export MEMORY_VERSION_2_ID="$(jq -r '.version.memory_version_id' /tmp/curl-memory-second.json)"
```

Expected `201`:

```json
{"scope":{"memory_scope_id":"11111111-bbbb-bbbb-bbbb-111111111111"},"version":{"memory_version_id":"33333333-bbbb-bbbb-bbbb-333333333333","previous_memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"},"head_advanced":true}
```

### 6.4 GET /memory/versions/{memory_version_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/memory/versions/$MEMORY_VERSION_1_ID?include_content=true"
```

Expected `200`:

```json
{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222","previous_memory_version_id":null,"content":{"preferred_contact":"sms"},"change_summary_redacted":"Captured preference"}
```

### 6.5 GET /memory/scopes/{memory_scope_id}/versions

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/memory/scopes/$MEMORY_SCOPE_ID/versions?include_content=false"
```

Expected `200`:

```json
{"scope":{"memory_scope_id":"11111111-bbbb-bbbb-bbbb-111111111111"},"versions":[{"memory_version_id":"33333333-bbbb-bbbb-bbbb-333333333333"},{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"}],"next_cursor":null}
```

### 6.6 GET /memory/versions/{memory_version_id}/replay

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/memory/versions/$MEMORY_VERSION_1_ID/replay"
```

Expected `200`:

```json
{"target":{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"},"content":{"preferred_contact":"sms"},"lineage":[{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"}]}
```

### 6.7 POST /memory/diffs

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/memory/diffs" \
  -d '{"base_memory_version_id":"'"$MEMORY_VERSION_1_ID"'","compare_memory_version_id":"'"$MEMORY_VERSION_2_ID"'"}'
```

Expected `200`:

```json
{"base":{"memory_version_id":"22222222-bbbb-bbbb-bbbb-222222222222"},"compare":{"memory_version_id":"33333333-bbbb-bbbb-bbbb-333333333333"},"additions":[],"removals":[],"changes":[{"path":"/preferred_contact","before":"sms","after":"email"}]}
```

### 6.8 GET /memory/audit

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/memory/audit?memory_scope_id=$MEMORY_SCOPE_ID"
```

Expected `200`:

```json
{"events":[{"action_type":"write","outcome":"allowed","memory_scope_id":"11111111-bbbb-bbbb-bbbb-111111111111","safe_summary":"Captured preference"}]}
```

### 6.9 Memory conflict scenario

```bash
curl -sS -i -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/memory/versions" \
  -d '{"scope":{"workflow_lineage_id":"workflow.demo","agent_key":"triage","memory_key":"prefs"},"expected_current_version_id":"'"$MEMORY_VERSION_1_ID"'","content":{"preferred_contact":"phone"}}'
```

Expected `409`:

```json
{"detail":{"detail":"current head does not match expected version","conflict_type":"head_mismatch","latest_memory_version_id":"33333333-bbbb-bbbb-bbbb-333333333333"}}
```

## 7. Prompt Runtime APIs

### 7.1 GET /admin/prompt-runtime/api/prompts

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/prompts?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 7.2 POST /admin/prompt-runtime/api/prompts

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts" \
  -d '{"scope_type":"tenant","tenant_id":"'"$ACME_TENANT_ID"'","slug":"curl-triage-summary","display_name":"Curl Triage Summary","purpose":"Summarize intake"}' \
  | tee /tmp/curl-prompt-create.json
export PROMPT_LINEAGE_ID="$(jq -r '.prompt_lineage_id' /tmp/curl-prompt-create.json)"
```

Expected `201`:

```json
{"prompt_lineage_id":"11111111-cccc-cccc-cccc-111111111111","scope_type":"tenant","tenant_id":"11111111-1111-1111-1111-111111111111","slug":"curl-triage-summary","display_name":"Curl Triage Summary","current_revision_number":0}
```

### 7.3 GET /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/prompts/$PROMPT_LINEAGE_ID/draft"
```

Expected `200`:

```json
{"prompt_lineage_id":"11111111-cccc-cccc-cccc-111111111111","current_revision_number":0,"draft":null}
```

### 7.4 PUT /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft

```bash
curl -sS -X PUT -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/$PROMPT_LINEAGE_ID/draft" \
  -d '{"expected_revision_number":0,"prompt_title":"Curl Triage Summary","purpose":"Summarize intake","usage_notes":"Sequential curl QA","template_content":"Hello {{name}}","variables":[{"name":"name","purpose":"Recipient","required":true}],"fixture_sets":[{"fixture_set_id":"default","label":"Default","values_by_variable":{"name":"Ada"}}]}' \
  | tee /tmp/curl-prompt-save.json
```

Expected `200`:

```json
{"prompt_lineage_id":"11111111-cccc-cccc-cccc-111111111111","current_revision_number":1,"status":"draft"}
```

### 7.5 POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/prompts/$PROMPT_LINEAGE_ID/validate"
```

Expected `200`:

```json
{"status":"passed","blocking_issue_count":0,"findings":[]}
```

### 7.6 POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/$PROMPT_LINEAGE_ID/preview" \
  -d '{"fixture_set_id":"default"}'
```

Expected `200`:

```json
{"fixture_set_id":"default","rendered_preview":"Hello Ada","redaction_applied":false}
```

### 7.7 POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/$PROMPT_LINEAGE_ID/publish" \
  -d '{"reason":"Initial curl publication"}' \
  | tee /tmp/curl-prompt-publish.json
export PROMPT_VERSION_ID="$(jq -r '.prompt_version_id' /tmp/curl-prompt-publish.json)"
export PROMPT_ID="$(jq -r '.prompt_id' /tmp/curl-prompt-publish.json)"
```

Expected `201`:

```json
{"prompt_version_id":"22222222-cccc-cccc-cccc-222222222222","prompt_id":"33333333-cccc-cccc-cccc-333333333333","display_version":"v1","status":"published","template_digest":"sha256:example"}
```

### 7.8 POST /admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/versions/$PROMPT_VERSION_ID/grants" \
  -d '{"tenant_id":"'"$GLOBEX_TENANT_ID"'","reason":"Share curl prompt"}'
```

Expected `201`:

```json
{"prompt_version_id":"22222222-cccc-cccc-cccc-222222222222","tenant_id":"22222222-2222-2222-2222-222222222222","status":"active"}
```

### 7.9 Prompt version cleanup note

Do not retire `PROMPT_VERSION_ID` yet. Later profile and model-skill checks use
that version. The actual retire curl command is in Section 8.19.

### 7.10 GET /admin/prompt-runtime/api/profiles

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/profiles?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 7.11 POST /admin/prompt-runtime/api/profiles

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles" \
  -d '{"scope_type":"tenant","tenant_id":"'"$ACME_TENANT_ID"'","agent_key":"planner","agent_kind":"agent","display_name":"Planner","purpose":"Plan work"}' \
  | tee /tmp/curl-profile-create.json
export AGENT_PROFILE_ID="$(jq -r '.agent_runtime_profile_id' /tmp/curl-profile-create.json)"
```

Expected `201`:

```json
{"agent_runtime_profile_id":"44444444-cccc-cccc-cccc-444444444444","agent_key":"planner","agent_kind":"agent","display_name":"Planner","current_revision_number":0}
```

### 7.12 PUT /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft

```bash
curl -sS -X PUT -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles/$AGENT_PROFILE_ID/draft" \
  -d '{"expected_revision_number":0,"purpose":"Plan work","prompt_references":[{"purpose":"planner","required_purpose":"planner","prompt_version_id":"'"$PROMPT_VERSION_ID"'","required":true}],"model_routing_hints":{"provider":"openai","model":"gpt-4.1-mini"},"memory_scope_policy":{"scope_mode":"read_only","retention_mode":"run"},"skill_requirements":[{"skill":"planning"}],"tool_policy_expectations":[{"category":"read"}],"output_contract_expectations":{"type":"object"},"test_suite_requirements":[{"suite":"planner-smoke"}]}'
```

Expected `200`:

```json
{"agent_runtime_profile_id":"44444444-cccc-cccc-cccc-444444444444","current_revision_number":1,"status":"draft"}
```

### 7.13 POST /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/validate

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/profiles/$AGENT_PROFILE_ID/validate"
```

Expected `200`:

```json
{"status":"passed","blocking_issue_count":0,"findings":[]}
```

### 7.14 POST /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/activate

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles/$AGENT_PROFILE_ID/activate" \
  -d '{"reason":"Activate curl profile"}' \
  | tee /tmp/curl-profile-activate.json
export AGENT_PROFILE_VERSION_ID="$(jq -r '.agent_profile_version_id' /tmp/curl-profile-activate.json)"
```

Expected `201`:

```json
{"agent_profile_version_id":"55555555-cccc-cccc-cccc-555555555555","agent_runtime_profile_id":"44444444-cccc-cccc-cccc-444444444444","display_version":"v1","status":"active"}
```

### 7.15 POST /admin/prompt-runtime/api/profiles/versions/{agent_profile_version_id}/grants

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles/versions/$AGENT_PROFILE_VERSION_ID/grants" \
  -d '{"tenant_id":"'"$GLOBEX_TENANT_ID"'","reason":"Share curl profile"}'
```

Expected `201`:

```json
{"agent_profile_version_id":"55555555-cccc-cccc-cccc-555555555555","tenant_id":"22222222-2222-2222-2222-222222222222","status":"active"}
```

### 7.16 POST /admin/prompt-runtime/api/resolve-profile

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/resolve-profile" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","agent_key":"planner","agent_kind":"agent"}'
```

Expected `200`:

```json
{"agent_key":"planner","agent_kind":"agent","resolved_profile_version_id":"55555555-cccc-cccc-cccc-555555555555","source_scope":"tenant"}
```

### 7.17 POST /admin/prompt-runtime/api/profiles/versions/{agent_profile_version_id}/retire

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles/versions/$AGENT_PROFILE_VERSION_ID/retire" \
  -d '{"reason":"Retire after curl verification"}'
```

Expected `200`:

```json
{"agent_profile_version_id":"55555555-cccc-cccc-cccc-555555555555","status":"retired"}
```

### 7.18 GET /admin/prompt-runtime/api/history

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/prompt-runtime/api/history?tenant_id=$ACME_TENANT_ID&limit=20"
```

Expected `200`:

```json
{"items":[{"action":"prompt_published","tenant_id":"11111111-1111-1111-1111-111111111111"},{"action":"profile_activated","tenant_id":"11111111-1111-1111-1111-111111111111"}]}
```

## 8. Model Provider And Model-Skill Configuration APIs

### 8.1 GET /admin/model-providers/api/connections

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/model-providers/api/connections"
```

Expected `200`:

```json
{"items":[]}
```

### 8.2 POST /admin/model-providers/api/connections

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/model-providers/api/connections" \
  -d '{"provider_type":"openai","display_name":"Curl OpenAI Provider","models":[{"model_id":"gpt-test"}],"credential_secret_reference_ids":["qa/openai-placeholder"],"active":true}' \
  | tee /tmp/curl-provider-create.json
export PROVIDER_CONNECTION_ID="$(jq -r '.provider_connection_id' /tmp/curl-provider-create.json)"
```

Expected `200`:

```json
{"provider_connection_id":"11111111-dddd-dddd-dddd-111111111111","provider_type":"openai","display_name":"Curl OpenAI Provider","active":true,"models":[{"model_id":"gpt-test"}],"health_state":"unknown"}
```

### 8.3 PUT /admin/model-providers/api/connections/{connection_id}

```bash
curl -sS -X PUT -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/model-providers/api/connections/$PROVIDER_CONNECTION_ID" \
  -d '{"provider_type":"openai","display_name":"Curl OpenAI Provider Updated","models":[{"model_id":"gpt-test-updated"}],"credential_secret_reference_ids":["qa/openai-placeholder"],"active":true}'
```

Expected `200`:

```json
{"provider_connection_id":"11111111-dddd-dddd-dddd-111111111111","display_name":"Curl OpenAI Provider Updated","models":[{"model_id":"gpt-test-updated"}],"active":true}
```

### 8.4 POST /admin/model-providers/{connection_id}/test

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" "$BASE_URL/admin/model-providers/$PROVIDER_CONNECTION_ID/test"
```

Expected `200`:

```json
{"provider_connection_id":"11111111-dddd-dddd-dddd-111111111111","outcome":"success","health_state":"healthy","safe_summary":"Provider test completed"}
```

### 8.5 POST /admin/model-providers/{connection_id}/sync-catalog

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" "$BASE_URL/admin/model-providers/$PROVIDER_CONNECTION_ID/sync-catalog"
```

Expected `200`:

```json
{"provider_connection_id":"11111111-dddd-dddd-dddd-111111111111","status":"completed","model_count":1}
```

### 8.6 POST /admin/config/model-routing

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/model-routing" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"provider_key":"openai","model_id":"gpt-5.4","activate":true,"reason":"Set tenant default model"}' \
  | tee /tmp/curl-model-routing.json
export MODEL_ROUTING_VERSION_ID="$(jq -r '.version_id' /tmp/curl-model-routing.json)"
```

Expected `201`:

```json
{"config_kind":"model_routing","version_id":"22222222-dddd-dddd-dddd-222222222222","tenant_id":"11111111-1111-1111-1111-111111111111","status":"active","active":true,"version_sequence":1,"activation_reason":"Set tenant default model"}
```

### 8.7 POST /admin/config/model-routing/{version_id}/activate

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/model-routing/$MODEL_ROUTING_VERSION_ID/activate?tenant_id=$ACME_TENANT_ID" \
  -d '{"reason":"Re-activate reviewed default"}'
```

Expected `200`:

```json
{"active_configuration_pointer_id":"33333333-dddd-dddd-dddd-333333333333","active_version_id":"22222222-dddd-dddd-dddd-222222222222","config_kind":"model_routing","scope_hash":"tenant:11111111-1111-1111-1111-111111111111"}
```

### 8.8 POST /admin/config/prompt-references

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/prompt-references" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'","workflow_lineage_id":"'"$WORKFLOW_LINEAGE_ID"'"},"prompt_id":"'"$PROMPT_ID"'","prompt_version_id":"'"$PROMPT_VERSION_ID"'","prompt_digest":"sha256:curl-prompt","activate":true,"reason":"Bind workflow prompt"}'
```

Expected `201`:

```json
{"config_kind":"prompt_reference","version_id":"44444444-dddd-dddd-dddd-444444444444","status":"active","active":true,"version_sequence":1}
```

### 8.9 POST /admin/config/skill-bindings

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/skill-bindings" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"skill_slug":"planning","skill_version":"1.0.0","allowed_contexts":["runtime_step"],"activate":true,"reason":"Allow planner skill"}'
```

Expected `201`:

```json
{"config_kind":"skill_binding","version_id":"55555555-dddd-dddd-dddd-555555555555","status":"active","active":true}
```

### 8.10 POST /admin/config/tool-policies

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/tool-policies" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"skill_slug":"planning","tool_id":"http.fetch","allowed_action_categories":["read"],"activate":true,"reason":"Allow read tool use"}'
```

Expected `201`:

```json
{"config_kind":"tool_policy","version_id":"66666666-dddd-dddd-dddd-666666666666","status":"active","active":true}
```

### 8.11 POST /admin/config/outbound-domain-policies

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/outbound-domain-policies" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"tool_id":"http.fetch","action_category":"read","allowed_domain_patterns":["example.com"],"allowed_schemes":["https"],"allowed_ports":[443],"activate":true,"reason":"Allow example.com fetches"}'
```

Expected `201`:

```json
{"config_kind":"outbound_domain_policy","version_id":"77777777-dddd-dddd-dddd-777777777777","status":"active","active":true}
```

### 8.12 POST /admin/config/secret-references

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/secret-references" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"secret_reference_id":"example-api-key","provider_key":"static","external_reference":"example/api-key","allowed_scopes":{"host":"example.com"},"activate":true,"reason":"Use managed secret reference"}' \
  | tee /tmp/curl-secret-reference.json
export SECRET_REFERENCE_VERSION_ID="$(jq -r '.version_id' /tmp/curl-secret-reference.json)"
```

Expected `201`:

```json
{"config_kind":"secret_reference","version_id":"88888888-dddd-dddd-dddd-888888888888","status":"active","active":true,"redacted_summary":{"secret_reference_id":"example-api-key"}}
```

### 8.13 POST /admin/config/credential-requirements

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/credential-requirements" \
  -d '{"scope":{"tenant_id":"'"$ACME_TENANT_ID"'"},"tool_id":"http.fetch","action_category":"read","credential_kind":"secret_reference","secret_reference_version_id":"'"$SECRET_REFERENCE_VERSION_ID"'","activate":true,"reason":"Require managed credential"}'
```

Expected `201`:

```json
{"config_kind":"credential_requirement","version_id":"99999999-dddd-dddd-dddd-999999999999","status":"active","active":true}
```

### 8.14 POST /admin/config/preview/model

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/preview/model" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","workflow_lineage_id":"'"$WORKFLOW_LINEAGE_ID"'"}'
```

Expected `200`:

```json
{"model_routing_version_id":"22222222-dddd-dddd-dddd-222222222222","model_provider_key":"openai","model_id":"gpt-5.4","model_source_scope":"tenant","prompt_reference_version_id":"44444444-dddd-dddd-dddd-444444444444","prompt_id":"33333333-cccc-cccc-cccc-333333333333","prompt_version_id":"22222222-cccc-cccc-cccc-222222222222","evaluated_version_ids":["22222222-dddd-dddd-dddd-222222222222"]}
```

### 8.15 POST /admin/config/preview/tool

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/preview/tool" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","skill_slug":"planning","skill_version":"1.0.0","tool_id":"http.fetch","action_category":"read","destination_url":"https://example.com:443/resource"}'
```

Expected `200`:

```json
{"outcome":"allow","safe_reason":"Allowed by active tool and outbound policies.","evaluated_version_ids":["66666666-dddd-dddd-dddd-666666666666"],"winning_version_ids":["66666666-dddd-dddd-dddd-666666666666"],"authorized_secret_reference_ids":["example-api-key"]}
```

### 8.16 GET /admin/config/history

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/config/history?tenant_id=$ACME_TENANT_ID&limit=10"
```

Expected `200`:

```json
{"items":[{"action":"created","config_kind":"model_routing","reason":"Set tenant default model"},{"action":"created","config_kind":"tool_policy","reason":"Allow read tool use"}]}
```

### 8.17 GET /admin/config/runs/{workflow_run_id}/provenance

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/config/runs/$RUNTIME_RUN_ID/provenance?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","resolved_execution_configuration_id":null,"resolution_digest":null,"decisions":[],"migrations":[]}
```

### 8.18 POST /admin/config/{config_kind}/{version_id}/rollback

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/config/model_routing/$MODEL_ROUTING_VERSION_ID/rollback?tenant_id=$ACME_TENANT_ID" \
  -d '{"target_version_id":"'"$MODEL_ROUTING_VERSION_ID"'","reason":"Confirm rollback flow"}'
```

Expected `200`:

```json
{"rollback_record_id":"aaaaaaaa-dddd-dddd-dddd-aaaaaaaaaaaa","active_version_id":"22222222-dddd-dddd-dddd-222222222222","audit_record_id":"bbbbbbbb-dddd-dddd-dddd-bbbbbbbbbbbb"}
```

### 8.19 POST /admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/retire

Now that the prompt version has been used by profile and model-skill checks, run
the cleanup endpoint.

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/versions/$PROMPT_VERSION_ID/retire" \
  -d '{"reason":"Retire after curl verification"}'
```

Expected `200`:

```json
{"prompt_version_id":"22222222-cccc-cccc-cccc-222222222222","status":"retired"}
```

## 9. Skill Registry And Skill Execution APIs

### 9.1 POST /admin/skill-registry/packages

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages" \
  -d '{"slug":"calendar-assistant","display_name":"Calendar Assistant","description":"Safe skill.","owner_principal_id":"platform-admin"}'
```

Expected `200`:

```json
{"slug":"calendar-assistant","display_name":"Calendar Assistant","description":"Safe skill.","lifecycle_state":"draft","owner_principal_id":"platform-admin"}
```

### 9.2 POST /admin/skill-registry/packages/{slug}/versions/validate

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions/validate" \
  -d '{"manifest":{"slug":"calendar-assistant","semantic_version":"1.2.3","display_name":"Calendar Assistant","description":"Calendar assistant skill","credential_requirements":[{"requirement_key":"calendar-oauth","credential_kind":"delegated_credential"}],"tools":[{"tool_id":"calendar.events.list","action_category":"read","integration_ref":"tool:calendar:v1"}]},"approved_integration_refs":["tool:calendar:v1"]}'
```

Expected `200`:

```json
{"status":"passed","safe_summary":{"slug":"calendar-assistant","semantic_version":"1.2.3"},"findings":[]}
```

### 9.3 POST /admin/skill-registry/packages/{slug}/versions

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions" \
  -d '{"manifest":{"slug":"calendar-assistant","semantic_version":"1.2.3","display_name":"Calendar Assistant","description":"Calendar assistant skill","credential_requirements":[{"requirement_key":"calendar-oauth","credential_kind":"delegated_credential"}],"tools":[{"tool_id":"calendar.events.list","action_category":"read","integration_ref":"tool:calendar:v1"}]},"approved_integration_refs":["tool:calendar:v1"],"artifact_digest":"sha256:artifact"}'
```

Expected `200`:

```json
{"slug":"calendar-assistant","semantic_version":"1.2.3","lifecycle_state":"published","artifact_digest":"sha256:artifact","readiness_state":"ready"}
```

### 9.4 POST /admin/skill-registry/packages/{slug}/versions/{semantic_version}/availability

```bash
curl -sS -i -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions/1.2.3/availability" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'"}'
```

Expected `204` with empty body.

### 9.5 GET /admin/skill-registry/tenants/{tenant_id}/available-versions

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/skill-registry/tenants/$ACME_TENANT_ID/available-versions"
```

Expected `200`:

```json
[{"slug":"calendar-assistant","semantic_version":"1.2.3","display_name":"Calendar Assistant","lifecycle_state":"published"}]
```

### 9.6 POST /admin/skill-registry/installations

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/installations" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","slug":"calendar-assistant","semantic_version":"1.2.3"}' \
  | tee /tmp/curl-skill-installation.json
export SKILL_INSTALLATION_ID="$(jq -r '.installation_id' /tmp/curl-skill-installation.json)"
export SKILL_INSTALLATION_REVISION="$(jq -r '.revision_token' /tmp/curl-skill-installation.json)"
```

Expected `200`:

```json
{"installation_id":"11111111-eeee-eeee-eeee-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","slug":"calendar-assistant","semantic_version":"1.2.3","readiness_state":"credentials_required","revision_token":"rev-1"}
```

### 9.7 POST /admin/skill-registry/installations/{installation_id}/credentials

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/installations/$SKILL_INSTALLATION_ID/credentials" \
  -d '{"revision_token":"'"$SKILL_INSTALLATION_REVISION"'","credentials":[{"requirement_key":"calendar-oauth","credential_kind":"delegated_credential","reference_id":"delegated-1","status":"ready"}]}' \
  | tee /tmp/curl-skill-credentials.json
export SKILL_INSTALLATION_REVISION="$(jq -r '.revision_token' /tmp/curl-skill-credentials.json)"
```

Expected `200`:

```json
{"installation_id":"11111111-eeee-eeee-eeee-111111111111","readiness_state":"ready","credential_readiness":[{"requirement_key":"calendar-oauth","status":"ready"}],"revision_token":"rev-2"}
```

### 9.8 GET /admin/skill-registry/installations/{installation_id}/eligibility

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/skill-registry/installations/$SKILL_INSTALLATION_ID/eligibility"
```

Expected `200`:

```json
{"installation_id":"11111111-eeee-eeee-eeee-111111111111","allowed":true,"readiness_state":"ready","findings":[]}
```

### 9.9 GET /admin/skill-execution/api/diagnostics

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/skill-execution/api/diagnostics"
```

Expected `200`:

```json
{"items":[{"tool_name":"google_calendar.events.read","display_name":"Google Calendar Events","mode":"mock","readiness":"ready","requires_credential":true,"latest_status":"succeeded"},{"tool_name":"gmail.messages.read","display_name":"Gmail Messages","mode":"mock","readiness":"ready","requires_credential":true,"latest_status":"succeeded"},{"tool_name":"weather.forecast.read","display_name":"Weather Forecast","mode":"mock","readiness":"ready","requires_credential":true,"latest_status":"succeeded"}]}
```

### 9.10 POST /admin/skill-execution/api/diagnostics/run

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-execution/api/diagnostics/run" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","tool_names":["weather.forecast.read"]}'
```

Expected `200`:

```json
{"items":[{"status":"succeeded","tool_name":"weather.forecast.read","execution_mode":"mock","request_summary":"weather.forecast.read mock diagnostic","response_summary":"Weather forecast retrieved with safe sample data","policy_decisions":[],"latency_ms":0}]}
```

## 10. Agent Test Bench APIs

### 10.1 GET /admin/agent-tests/suites

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/agent-tests/suites?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
[]
```

### 10.2 POST /admin/agent-tests/suites

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/agent-tests/suites" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","name":"Curl Draft Workflow Guard","target_type":"workflow_draft","target_id":"curl-triage-flow","target_version":"draft-rev-1","required_for_publish":true}' \
  | tee /tmp/curl-agent-suite.json
export AGENT_SUITE_ID="$(jq -r '.suite_id' /tmp/curl-agent-suite.json)"
```

Expected `201`:

```json
{"suite_id":"11111111-ffff-ffff-ffff-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","name":"Curl Draft Workflow Guard","target_type":"workflow_draft","target_id":"curl-triage-flow","required_for_publish":true}
```

### 10.3 GET /admin/agent-tests/suites/{suite_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/agent-tests/suites/$AGENT_SUITE_ID"
```

Expected `200`:

```json
{"suite_id":"11111111-ffff-ffff-ffff-111111111111","name":"Curl Draft Workflow Guard","cases":[]}
```

### 10.4 PATCH /admin/agent-tests/suites/{suite_id}

```bash
curl -sS -X PATCH -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/agent-tests/suites/$AGENT_SUITE_ID" \
  -d '{"name":"Curl Draft Workflow Guard Updated","required_for_publish":true}'
```

Expected `200`:

```json
{"suite_id":"11111111-ffff-ffff-ffff-111111111111","name":"Curl Draft Workflow Guard Updated","required_for_publish":true}
```

### 10.5 POST /admin/agent-tests/suites/{suite_id}/cases

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/agent-tests/suites/$AGENT_SUITE_ID/cases" \
  -d '{"name":"Passing intake case","fixture":{"request":"summarize intake","api_key":"secret"},"expected_contract_shape":{"status":{},"contract":{}},"assertions":[{"kind":"deterministic","path":"contract.summary","comparator":"contains","expected_value":"intake"}]}' \
  | tee /tmp/curl-agent-case.json
export AGENT_CASE_ID="$(jq -r '.case_id' /tmp/curl-agent-case.json)"
```

Expected `201`:

```json
{"case_id":"22222222-ffff-ffff-ffff-222222222222","name":"Passing intake case","fixture_summary":{"preview":{"api_key":"[redacted]"}}}
```

### 10.6 POST /admin/agent-tests/suites/{suite_id}/runs

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/agent-tests/suites/$AGENT_SUITE_ID/runs" \
  -d '{"safe_mode":"real_model_side_effects_disabled","target_version":"draft-rev-1","idempotency_key":"agent-run-curl-001"}' \
  | tee /tmp/curl-agent-run.json
export AGENT_RUN_ID="$(jq -r '.run_id' /tmp/curl-agent-run.json)"
```

Expected `202`:

```json
{"run_id":"33333333-ffff-ffff-ffff-333333333333","suite_id":"11111111-ffff-ffff-ffff-111111111111","status":"passed","safe_mode":"real_model_side_effects_disabled","blocked_side_effect_count":1,"steps":[{"model_provider":"mocked-gateway"}]}
```

### 10.7 GET /admin/agent-tests/runs

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/agent-tests/runs?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
[{"run_id":"33333333-ffff-ffff-ffff-333333333333","suite_id":"11111111-ffff-ffff-ffff-111111111111","status":"passed"}]
```

### 10.8 GET /admin/agent-tests/runs/{run_id}

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/agent-tests/runs/$AGENT_RUN_ID"
```

Expected `200`:

```json
{"run_id":"33333333-ffff-ffff-ffff-333333333333","status":"passed","blocked_side_effect_count":1,"safe_summary":"All assertions passed"}
```

### 10.9 POST /admin/agent-tests/publish-gates/evaluate

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/agent-tests/publish-gates/evaluate" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","target_type":"workflow_draft","target_id":"curl-triage-flow","target_version":"draft-rev-1"}'
```

Expected `200`:

```json
{"status":"ready","required_count":1,"passing_count":1,"blocking_findings":[]}
```

## 11. Briefing Preferences APIs

### 11.1 GET /admin/briefing-preferences/api/profile

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/briefing-preferences/api/profile?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"profile":null}
```

### 11.2 POST /admin/briefing-preferences/api/profile

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/briefing-preferences/api/profile" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","location_label":"Providence, RI","timezone":"America/New_York","news_topics":["AI","markets"],"vip_senders":["sarah@example.com"],"workday_start":"09:00","workday_end":"17:30","commute_mode":"driving","calendar_account_ref":"delegated:calendar:primary","email_account_ref":"delegated:gmail:primary","output_style":"standard","scheduled_enabled":true,"scheduled_time":"08:00"}' \
  | tee /tmp/curl-briefing-profile.json
export BRIEFING_REVISION_TOKEN="$(jq -r '.revision_token' /tmp/curl-briefing-profile.json)"
```

Expected `200`:

```json
{"briefing_preference_profile_id":"11111111-1111-2323-1111-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","location_label":"Providence, RI","timezone":"America/New_York","news_topics":["AI","markets"],"vip_senders":["sarah@example.com"],"output_style":"standard","revision_number":1,"revision_token":"rev-1","safe_summary":{"vip_senders":["s***@example.com"]}}
```

### 11.3 GET /admin/briefing-preferences/api/summaries

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/briefing-preferences/api/summaries?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[{"briefing_preference_profile_id":"11111111-1111-2323-1111-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","revision_number":1,"content_digest":"sha256:example","safe_summary":{"vip_senders":["s***@example.com"],"delegated_refs":"[redacted]"}}]}
```

### 11.4 GET /admin/briefing-preferences/api/export

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/briefing-preferences/api/export?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-briefing-export.json
```

Expected `200`:

```json
{"document":{"tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","preferences":{"timezone":"America/New_York","output_style":"standard"}}}
```

### 11.5 POST /admin/briefing-preferences/api/import

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/briefing-preferences/api/import" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","document":{"tenant_id":"'"$ACME_TENANT_ID"'","principal_id":"tenant-admin-acme","preferences":{"location_label":"Providence, RI","timezone":"America/New_York","news_topics":["AI"],"output_style":"executive"}},"revision_token":"'"$BRIEFING_REVISION_TOKEN"'"}'
```

Expected `200`:

```json
{"briefing_preference_profile_id":"11111111-1111-2323-1111-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","location_label":"Providence, RI","timezone":"America/New_York","news_topics":["AI"],"output_style":"executive","revision_number":2,"revision_token":"rev-2"}
```

### 11.6 POST /admin/briefing-preferences/api/resolve

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/briefing-preferences/api/resolve" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","principal_id":"tenant-admin-acme","source_channel":"telegram","trace_id":"trace-briefing-curl"}'
```

Expected `200`:

```json
{"available":true,"tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","preferences":{"timezone":"America/New_York","output_style":"executive"}}
```

### 11.7 Briefing cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" "$BASE_URL/admin/briefing-preferences/api/profile?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":"cross_tenant"}
```

## 12. Usage Analytics APIs

### 12.1 GET /admin/usage/api/summary

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/usage/api/summary"
```

Expected `200`:

```json
{"total_events":2,"total_tokens":100,"input_tokens":0,"output_tokens":0,"cached_tokens":0,"reasoning_tokens":0,"provider_billable_units":0,"estimated_cost_micros":300,"currency":"USD","estimated_event_count":2,"confirmed_event_count":0,"unavailable_event_count":0,"rollups":[{"bucket":"2026-05-04","total_tokens":100,"estimated_cost_micros":300}]}
```

### 12.2 GET /admin/usage/api/summary tenant scope

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/usage/api/summary?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"total_events":1,"total_tokens":10,"input_tokens":0,"output_tokens":0,"cached_tokens":0,"reasoning_tokens":0,"provider_billable_units":0,"estimated_cost_micros":30,"currency":"USD","estimated_event_count":1,"confirmed_event_count":0,"unavailable_event_count":0,"rollups":[{"bucket":"2026-05-04","total_tokens":10}]}
```

### 12.3 GET /admin/usage/api/events

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/usage/api/events?tenant_id=$ACME_TENANT_ID&limit=25"
```

Expected `200`:

```json
{"events":[{"tenant_id":"11111111-1111-1111-1111-111111111111","provider_key":"openai","model_id":"gpt-test","total_tokens":10,"usage_status":"estimated"}]}
```

### 12.4 POST /admin/usage/api/exports

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/usage/api/exports" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","filters":{"model_id":"gpt-test"}}'
```

Expected `201`:

```json
{"usage_export_request_id":"11111111-1212-1212-1212-111111111111","status":"completed","row_count":1,"artifact_uri":"file://.data/artifacts/usage-export.csv","artifact_sha256":"sha256:example","artifact_size_bytes":512}
```

### 12.5 Usage cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" "$BASE_URL/admin/usage/api/summary?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":"cross_tenant"}
```

## 13. Telegram Configuration And Webhook APIs

### 13.1 GET /admin/telegram/api/readiness

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/telegram/api/readiness"
```

Expected `200`:

```json
{"token_reference_configured":true,"webhook_secret_configured":true,"token_reference_safe":true,"webhook_secret_safe":true,"production_guardrails_ready":true,"local_validation_only":true,"ready":true,"token_reference_label":"env:QA017_TELEGRAM_TOKEN","webhook_secret_label":"[configured]","protected_commands":["/run","/status"]}
```

### 13.2 GET /admin/telegram/api/config

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/config?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-telegram-config.json
export TELEGRAM_CONFIG_REVISION="$(jq -r '.revision_token' /tmp/curl-telegram-config.json)"
```

Expected `200`:

```json
{"telegram_tenant_config_id":"11111111-1313-aaaa-1313-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","enabled":false,"protected_commands":["/run","/status"],"status_note":null,"revision_token":"rev-1","updated_by_principal_id":"tenant-admin-acme","command_ready":false}
```

### 13.3 POST /admin/telegram/api/config

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/telegram/api/config" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","enabled":true,"protected_commands":["/run","/status"],"status_note":"Ready for QA","revision_token":"'"$TELEGRAM_CONFIG_REVISION"'"}'
```

Expected `200`:

```json
{"telegram_tenant_config_id":"11111111-1313-aaaa-1313-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","enabled":true,"protected_commands":["/run","/status"],"status_note":"Ready for QA","revision_token":"rev-2","updated_by_principal_id":"tenant-admin-acme","command_ready":true}
```

### 13.4 POST /admin/telegram/api/webhook/validate

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/webhook/validate?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"telegram_diagnostic_event_id":"11111111-1313-bbbb-1313-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","category":"webhook","status":"passed","summary":"Webhook validation completed","trace_id":"trace-...","redacted_metadata":{"external_call_performed":false}}
```

### 13.5 GET /admin/telegram/api/aliases

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/aliases?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 13.6 POST /admin/telegram/api/aliases

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/telegram/api/aliases" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","alias_text":"Morning briefing","published_workflow_version_id":"'"$WORKFLOW_VERSION_BUNDLE_ID"'","description":"Daily Intelligence Briefing","protected":true,"enabled":true}' \
  | tee /tmp/curl-telegram-alias.json
export TELEGRAM_ALIAS_ID="$(jq -r '.telegram_command_alias_id' /tmp/curl-telegram-alias.json)"
```

Expected `200`:

```json
{"telegram_command_alias_id":"11111111-1313-1313-1313-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","alias_text":"Morning briefing","alias_normalized":"morning briefing","published_workflow_version_id":"55555555-aaaa-aaaa-aaaa-555555555555","protected":true,"enabled":true,"revision_token":"rev-1"}
```

### 13.7 GET /admin/telegram/api/diagnostics

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/diagnostics?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[{"telegram_diagnostic_event_id":"11111111-1313-bbbb-1313-111111111111","category":"webhook","status":"passed","summary":"Webhook validation completed","redacted_metadata":{"external_call_performed":false}}]}
```

### 13.8 GET /admin/telegram/api/link-tokens

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/link-tokens?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 13.9 POST /admin/telegram/api/link-tokens

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/link-tokens?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-telegram-link-token.json
export TELEGRAM_LINK_TOKEN="$(jq -r '.link_token' /tmp/curl-telegram-link-token.json)"
export TELEGRAM_TOKEN_AUDIT_ID="$(jq -r '.token_audit.telegram_link_token_audit_id' /tmp/curl-telegram-link-token.json)"
```

Expected `201`:

```json
{"link_token":"link_...","token_audit":{"telegram_link_token_audit_id":"22222222-1313-1313-1313-222222222222","tenant_id":"11111111-1111-1111-1111-111111111111","issued_by_principal_id":"tenant-admin-acme","token_fingerprint":"sha256:...","status":"issued","expires_at":"2026-05-04T12:10:00Z","trace_id":"trace-..."}}
```

### 13.10 POST /channels/telegram/webhook/{secret} link identity

```bash
curl -sS -X POST -H "$JSON_HEADER" "$BASE_URL/channels/telegram/webhook/$TELEGRAM_SECRET" \
  -d '{"update_id":501,"message":{"chat":{"id":123456789},"from":{"id":987654321},"text":"/link '"$TELEGRAM_LINK_TOKEN"'"}}'
```

Expected `200`:

```json
{"ok":true,"action":"linked","tenant_id":"11111111-1111-1111-1111-111111111111"}
```

### 13.11 GET /admin/telegram/api/identities

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/identities?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[{"telegram_linked_identity_summary_id":"33333333-1313-1313-1313-333333333333","tenant_id":"11111111-1111-1111-1111-111111111111","platform_identity_id":"tenant-admin-acme","telegram_user_display":"987***321","telegram_chat_display":"123***789","status":"linked","command_ready":true,"trace_id":"trace-..."}]}
```

### 13.12 POST /channels/telegram/webhook/{secret} alias trigger

```bash
curl -sS -X POST -H "$JSON_HEADER" "$BASE_URL/channels/telegram/webhook/$TELEGRAM_SECRET" \
  -d '{"update_id":502,"message":{"chat":{"id":123456789},"from":{"id":987654321},"text":"Morning briefing"}}'
```

Expected `200`:

```json
{"ok":true,"alias":"Morning briefing","run_id":"44444444-1313-1313-1313-444444444444","delivered":true}
```

### 13.13 POST /channels/telegram/webhook/{secret} duplicate delivery

```bash
curl -sS -X POST -H "$JSON_HEADER" "$BASE_URL/channels/telegram/webhook/$TELEGRAM_SECRET" \
  -d '{"update_id":502,"message":{"chat":{"id":123456789},"from":{"id":987654321},"text":"Morning briefing"}}'
```

Expected `200`:

```json
{"ok":true,"alias":"Morning briefing","run_id":"44444444-1313-1313-1313-444444444444","delivered":true}
```

### 13.14 POST /admin/telegram/api/link-tokens/{token_audit_id}/revoke

```bash
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/link-tokens/$TELEGRAM_TOKEN_AUDIT_ID/revoke"
```

Expected `200`:

```json
{"telegram_link_token_audit_id":"22222222-1313-1313-1313-222222222222","tenant_id":"11111111-1111-1111-1111-111111111111","status":"revoked","token_fingerprint":"sha256:...","trace_id":"trace-..."}
```

### 13.15 POST /admin/telegram/api/identities/{identity_id}/revoke

```bash
export TELEGRAM_IDENTITY_ID="$(curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/identities?tenant_id=$ACME_TENANT_ID" | jq -r '.items[0].telegram_linked_identity_summary_id')"
curl -sS -X POST -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/identities/$TELEGRAM_IDENTITY_ID/revoke"
```

Expected `200`:

```json
{"telegram_linked_identity_summary_id":"33333333-1313-1313-1313-333333333333","tenant_id":"11111111-1111-1111-1111-111111111111","status":"revoked","telegram_user_display":"987***321","telegram_chat_display":"123***789","command_ready":false}
```

### 13.16 GET /admin/telegram/api/snapshot

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/telegram/api/snapshot?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"readiness":{"ready":true},"tenant_config":{"enabled":true,"command_ready":true},"aliases":[{"alias_text":"Morning briefing","enabled":true}],"token_audits":[{"status":"revoked"}],"identities":[{"status":"revoked"}],"diagnostics":[{"status":"passed"}]}
```

### 13.17 Telegram wrong-secret scenario

```bash
curl -sS -i -X POST -H "$JSON_HEADER" "$BASE_URL/channels/telegram/webhook/wrong-secret" \
  -d '{"update_id":999,"message":{"chat":{"id":1},"from":{"id":2},"text":"/status"}}'
```

Expected `403`:

```json
{"detail":"invalid telegram webhook secret"}
```

## 14. Operations Console APIs

### 14.1 GET /admin/operations/api/dashboard

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/operations/api/dashboard"
```

Expected `200`:

```json
{"status_cards":[{"label":"System Health","status":"ready"},{"label":"Token Throughput","status":"ready"},{"label":"Model Providers","status":"ready"}],"usage":{"total_tokens":25},"queue":{"runnable_depth":6}}
```

### 14.2 GET /admin/operations/api/logs

```bash
curl -sS -H "$AUDITOR_HEADER" "$BASE_URL/admin/operations/api/logs?trace_id=trace-ops&component=model_provider&limit=25"
```

Expected `200`:

```json
{"items":[{"source":"gateway_attempt","trace_id":"trace-ops","component":"model_provider","severity":"info","safe_summary":"Gateway completed safely"}],"next_cursor":null}
```

### 14.3 POST /admin/operations/api/logs/export

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/operations/api/logs/export" \
  -d '{"filters":{"trace_id":"trace-ops","limit":10}}'
```

Expected `201`:

```json
{"export_id":"11111111-1414-1414-1414-111111111111","row_count":1,"artifact_uri":"file://.data/artifacts/operations-export.csv","redaction_applied":true}
```

### 14.4 Operations tenant denial

```bash
curl -sS -i -H "$ACME_HEADER" "$BASE_URL/admin/operations/api/dashboard"
```

Expected `403`:

```json
{"detail":"insufficient_permission"}
```

## 15. Reliability APIs

### 15.1 GET /admin/reliability/dashboard

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/dashboard"
```

Expected `200`:

```json
{"tenant_id":null,"status":"available","runnable_depth":0,"delayed_depth":0,"active_leases":0,"retry_backlog":0,"compensation_backlog":0,"dead_letter_count":0,"db_pool_wait_p95_ms":0,"open_breaker_count":0,"partial":false,"redacted":false}
```

### 15.2 GET /admin/reliability/policies

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/policies?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 15.3 POST /admin/reliability/policies

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/reliability/policies" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","scope_type":"tenant","scope_key":"default","settings":{"max_active_work":25},"reason":"Sequential curl reliability policy"}' \
  | tee /tmp/curl-reliability-policy.json
export RELIABILITY_POLICY_ID="$(jq -r '.control_change_id // .policy_id' /tmp/curl-reliability-policy.json)"
```

Expected `202`:

```json
{"control_change_id":"11111111-1515-1515-1515-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","policy_id":"22222222-1515-1515-1515-222222222222","actor_id":"local-principal","actor_role":"admin","scope_type":"tenant","scope_key":"default","validation_outcome":"accepted"}
```

### 15.4 GET /admin/reliability/admission-decisions

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/admission-decisions?tenant_id=$ACME_TENANT_ID&limit=25"
```

Expected `200`:

```json
{"items":[]}
```

### 15.5 GET /admin/reliability/breakers

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/breakers?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 15.6 POST /admin/reliability/breakers/{breaker_id}/reset

Set `BREAKER_ID` from the previous list if a breaker exists.

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/reliability/breakers/$BREAKER_ID/reset" \
  -d '{"reason":"Sequential curl breaker reset","target_state":"closed"}'
```

Expected `202`:

```json
{"circuit_breaker_id":"22222222-1515-1515-1515-222222222222","tenant_id":null,"scope_type":"dependency","scope_key":"unknown","state":"closed","reason_code":"operator_reset","cooldown_until":null,"half_open_tokens":0}
```

### 15.7 GET /admin/reliability/retries

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/retries?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 15.8 GET /admin/reliability/compensations

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/compensations?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 15.9 GET /admin/reliability/dead-letters

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/dead-letters?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

### 15.10 POST /admin/reliability/dead-letters/{dead_letter_id}/actions

Set `DEAD_LETTER_ID` from the previous list if one exists.

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/reliability/dead-letters/$DEAD_LETTER_ID/actions?action=requeue"
```

Expected `202`:

```json
{"dead_letter_id":"33333333-1515-1515-1515-333333333333","action":"requeue","status":"accepted"}
```

### 15.11 GET /admin/reliability/load-test-reports

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/reliability/load-test-reports?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"items":[]}
```

## 16. Production Audit And Debugging APIs

These endpoints require runtime audit evidence. If the local database has no
audit timeline for `RUNTIME_RUN_ID`, first use the feature QA seed for spec 008
or inspect a run that already has audit events.

### 16.1 GET /admin/runs/debug-search

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/runs/debug-search?tenant_id=$ACME_TENANT_ID&limit=50"
```

Expected `200`:

```json
{"items":[{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","tenant_id":"11111111-1111-1111-1111-111111111111","status":"running","trace_id":"trace-runtime-curl","bundle":{}}],"next_cursor":null}
```

### 16.2 GET /admin/runs/{workflow_run_id}/timeline

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/timeline?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","tenant_id":"11111111-1111-1111-1111-111111111111","events":[{"sequence":1,"event_category":"runtime","safe_summary":"Run moved to running","trace_id":"trace-runtime-curl"}],"lineage":{"nodes":[],"edges":[]}}
```

### 16.3 GET /admin/runs/{workflow_run_id}/replay

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/replay?tenant_id=$ACME_TENANT_ID&from_sequence=0&to_sequence=100"
```

Expected `200`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","tenant_id":"11111111-1111-1111-1111-111111111111","events":[{"sequence":1,"event_category":"runtime","safe_summary":"Run moved to running"}]}
```

### 16.4 GET /admin/runs/{workflow_run_id}/lineage

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/lineage?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"nodes":[],"edges":[]}
```

### 16.5 GET /admin/runs/{workflow_run_id}/bundle

```bash
curl -sS -H "$PLATFORM_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/bundle?tenant_id=$ACME_TENANT_ID"
```

Expected `200`:

```json
{"workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","workflow_version_bundle_id":"55555555-aaaa-aaaa-aaaa-555555555555","bundle_digest":"sha256:example","redaction_applied":true}
```

### 16.6 POST /admin/runs/{workflow_run_id}/exports

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/exports" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","lineage_scope":"single_run","recipient_scope":"tenant_auditor","included_sections":["timeline","bundle"],"excluded_sections":[]}'
```

Expected `202`:

```json
{"debug_evidence_export_id":"11111111-1616-1616-1616-111111111111","workflow_run_id":"77777777-aaaa-aaaa-aaaa-777777777777","recipient_scope":"tenant_auditor","status":"created","artifact_uri":"file://.data/artifacts/debug-export.json"}
```

### 16.7 Audit cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/timeline?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":{"category":"forbidden","message":"cross tenant access denied","trace_id":"trace-..."}}
```

## 17. Coverage Checklist

The walkthrough covers the JSON/API endpoints from specs 001 through 025:

- Operations foundation: `/health/live`, `/health/ready`, `/version`, `/dependencies`
- Auth and access: `/auth/me`, `/auth/tenant-context/{tenant_id}`, `/admin/tenants/{tenant_id}/role-grants`, `/admin/role-grants`, `/admin/support-overrides`, `/admin/support-overrides/{support_override_request_id}/approve`
- Admin saved-filter JSON restore: `/admin/filters/{admin_area}/{filter_id}/restore`
- Workflow registry: all `/admin/workflows` JSON endpoints
- Durable runtime: all `/runtime/runs` JSON endpoints
- Immutable memory: all `/memory` JSON endpoints
- Channels: all `/runs` JSON endpoints, `/runs/{run_id}/events` SSE, `/channels/telegram/link-token`, `/channels/telegram/webhook/{secret}`
- Model and skill routing: all `/admin/config` JSON endpoints
- Model providers: all `/admin/model-providers` JSON endpoints
- Prompt runtime: all `/admin/prompt-runtime/api/prompts`, `/api/profiles`, `/api/resolve-profile`, and `/api/history` endpoints
- Skill registry and execution: all `/admin/skill-registry` JSON endpoints and `/admin/skill-execution/api` endpoints
- Agent test bench: all `/admin/agent-tests` JSON endpoints
- Briefing preferences: all `/admin/briefing-preferences/api` endpoints
- Usage analytics: all `/admin/usage/api` endpoints
- Membership administration: all `/admin/memberships/api` endpoints
- Telegram configuration: all `/admin/telegram/api` endpoints
- Operations console: all `/admin/operations/api` endpoints
- Reliability controls: all `/admin/reliability` JSON endpoints
- Audit and debugging: all `/admin/runs` JSON endpoints

Known non-JSON API-adjacent routes, such as admin shell pages, prompt/profile
form pages, workflow UI pages, reliability UI pages, and model-provider form
pages, return HTML and are validated in the browser/UI QA guides instead of
this JSON curl sequence.
