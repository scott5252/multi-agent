# Sequential curl API Test Plan

This document is a sequential JSON/API walkthrough for specs 001 through 069.
It is based on the implemented FastAPI route inventory in
`multi_agent_platform.api.main` and the feature QA/integration tests.

The commands assume a local QA database has been migrated and seeded with the
Acme and Globex tenants used throughout the specs. The primary coverage is the
JSON/SSE API surface; read-only React admin URLs and legacy redirect/page URLs
are included as smoke scenarios so the walkthrough stays aligned with the full
FastAPI URL inventory.

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
export PLATFORM_APPROVER_HEADER="X-Local-Principal: platform-approver"
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

### 1.8 Local principal login and logout URLs

```bash
curl -sS "$BASE_URL/auth/local-login.json?redirect_to=/admin/app" \
  | jq -e '.auth_mode == "local_principal" and (.principals | length) >= 4'
curl -sS "$BASE_URL/auth/local-login?redirect_to=/admin/app" >/dev/null
curl -sS -i -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
  "$BASE_URL/auth/local-login" \
  --data-urlencode 'principal=tenant-admin-acme' \
  --data-urlencode 'redirect_to=/admin/app' \
  --data-urlencode 'action_token=local-principal-login'
curl -sS -i "$BASE_URL/auth/local-logout?redirect_to=/auth/local-login"
```

Expected `303`:

```json
true
```

## 2. Membership And Platform Access Bootstrap

These commands create a persisted principal that later admin and membership
commands reuse.

### 2.1 POST /admin/memberships/api/principals/link

```bash
curl -sS -X POST -H "$PLATFORM_APPROVER_HEADER" -H "$JSON_HEADER" \
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
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
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
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
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
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
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
  "$BASE_URL/admin/memberships/api/memberships/$TENANT_MEMBERSHIP_ID/suspended?tenant_id=$ACME_TENANT_ID"
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
curl -sS -X POST -H "$PLATFORM_APPROVER_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/support-overrides/$SUPPORT_OVERRIDE_ID/approve" \
  -d '{"expires_in_hours":2}'
```

Expected `200`:

```json
{"support_override_request_id":"ffffffff-ffff-ffff-ffff-ffffffffffff","target_tenant_id":"11111111-1111-1111-1111-111111111111","status":"approved","expires_at":"2026-05-04T14:00:00Z"}
```

### 2.14 GET /admin/filters/{admin_area}/{filter_id}/restore

This admin shell endpoint restores an existing saved filter and redirects to
the filtered destination. Create the filter from the admin shell first, then set
`FILTER_ID`.

```bash
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/filters/workflows/$FILTER_ID/restore"
```

Expected `303` redirect to `/admin/workflows/ui?tenant_id=...&status=draft`.

### 2.15 GET and POST /admin/filters/{admin_area}

The saved-filter envelope is JSON. The HTML form-compatible save endpoint
redirects after persisting sanitized criteria.

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/filters/workflows.json?tenant_id=$ACME_TENANT_ID" \
  >/dev/null
curl -sS -i -X POST -H "$ACME_HEADER" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  "$BASE_URL/admin/filters/workflows?tenant_id=$ACME_TENANT_ID" \
  --data-urlencode 'filter_key=curl-workflows-extra' \
  --data-urlencode 'display_name=Curl extra workflow filter' \
  --data-urlencode 'criteria={"status":"published"}' \
  --data-urlencode 'return_to=/admin/app/workflows'
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/filters/workflows.json?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-filters-after-save.json
export EXTRA_FILTER_ID="$(jq -r '.saved_filters[] | select(.filter_key == "curl-workflows-extra") | .filter_id' /tmp/curl-filters-after-save.json)"
```

Expected `200`:

```json
{"admin_area":"workflows","saved_filters":[{"filter_key":"curl-workflows-extra"}]}
```

### 2.16 GET, DELETE, and POST-delete /admin/filters/{admin_area}/{filter_id}

```bash
curl -sS -i -H "$ACME_HEADER" \
  "$BASE_URL/admin/filters/workflows?tenant_id=$ACME_TENANT_ID"
curl -sS -i -X DELETE -H "$ACME_HEADER" \
  "$BASE_URL/admin/filters/workflows/$EXTRA_FILTER_ID?tenant_id=$ACME_TENANT_ID"
curl -sS -i -X POST -H "$ACME_HEADER" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  "$BASE_URL/admin/filters/workflows?tenant_id=$ACME_TENANT_ID" \
  --data-urlencode 'filter_key=curl-workflows-post-delete' \
  --data-urlencode 'display_name=Curl post-delete workflow filter' \
  --data-urlencode 'criteria={"status":"draft"}' \
  --data-urlencode 'return_to=/admin/app/workflows'
export POST_DELETE_FILTER_ID="$(curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/filters/workflows.json?tenant_id=$ACME_TENANT_ID" | jq -r '.saved_filters[] | select(.filter_key == "curl-workflows-post-delete") | .filter_id')"
curl -sS -i -X POST -H "$ACME_HEADER" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  "$BASE_URL/admin/filters/workflows/$POST_DELETE_FILTER_ID?tenant_id=$ACME_TENANT_ID" \
  --data-urlencode 'return_to=/admin/app/workflows'
```

Expected `303`:

```json
{"detail":"redirect after saved-filter URL operation"}
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

### 3.7a GET /admin/workflows/drafts/{workflow_draft_id}/agent-graph

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/agent-graph" \
  | jq -e '.source == "draft" and .state == "ready" and .partial == false and (.nodes | length) >= 1 and .nodes[0].category == "coordinator_agent" and (.accessibility.node_summaries | length) >= 1'
```

Expected `200`:

```json
true
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

### 3.14a GET /admin/workflows/versions/{workflow_version_bundle_id}/agent-graph

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/agent-graph" \
  | jq -e '.source == "published_version" and .partial == false and .provenance.workflow_version_bundle_id == env.WORKFLOW_VERSION_BUNDLE_ID and (.nodes | length) >= 1 and (.accessibility.node_summaries | length) >= 1'
```

Expected `200`:

```json
true
```

### 3.15 POST /admin/workflows/versions/{workflow_version_bundle_id}/sharing-grants

Tenant-scoped workflow versions cannot be shared; sharing grants are only valid
for platform-scoped versions.

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/sharing-grants" \
  -d '{"grantee_tenant_id":"'"$GLOBEX_TENANT_ID"'"}'
```

Expected `403`:

```json
{"detail":"only platform-scoped versions can be shared"}
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
export PROMPT_ID="$(jq -r '.prompt_lineage_id' /tmp/curl-prompt-publish.json)"
```

Expected `201`:

```json
{"prompt_version_id":"22222222-cccc-cccc-cccc-222222222222","prompt_id":"33333333-cccc-cccc-cccc-333333333333","display_version":"v1","status":"published","template_digest":"sha256:example"}
```

### 7.8 POST /admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants

Tenant-scoped prompt versions cannot be granted to other tenants; grants are
only valid for platform-scoped prompt versions.

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/prompts/versions/$PROMPT_VERSION_ID/grants" \
  -d '{"tenant_ids":["'"$GLOBEX_TENANT_ID"'"],"reason":"Share curl prompt"}'
```

Expected `409`:

```json
{"detail":{"code":"grant_not_allowed"}}
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

Tenant-scoped agent profile versions cannot be granted to other tenants; grants
are only valid for platform-scoped profile versions.

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/prompt-runtime/api/profiles/versions/$AGENT_PROFILE_VERSION_ID/grants" \
  -d '{"tenant_ids":["'"$GLOBEX_TENANT_ID"'"],"reason":"Share curl profile"}'
```

Expected `409`:

```json
{"detail":{"code":"grant_not_allowed"}}
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
export CALENDAR_SKILL_MANIFEST='{"schema_version":"1.0","slug":"calendar-assistant","semantic_version":"1.2.3","description":"Calendar assistant for safe scheduling operations.","entrypoint":{"type":"approved_tool_ref","approved_integration_ref":"tool:calendar:v1"},"tools":[{"tool_id":"calendar.list","approved_integration_ref":"tool:calendar:v1","display_name":"List calendars","description":"Lists calendar metadata.","action_categories":["read"],"side_effect_profile":"read_only","safe_usage":"Use for tenant-scoped calendar listing."}],"action_categories":["read"],"network_requirements":[{"tool_id":"calendar.list","action_category":"read","allowed_schemes":["https"],"allowed_domain_patterns":["calendar.example.com"],"allowed_ports":[443],"required":true,"safe_description":"Calendar API endpoint."}],"credential_requirements":[{"requirement_key":"calendar-oauth","credential_kind":"delegated_credential","tool_id":"calendar.list","action_category":"read","required":true,"delegated_credential_scopes":["calendar.readonly"],"safe_description":"Delegated calendar read access."}],"runtime_permissions":[{"permission_key":"calendar-read","permission_type":"tool_access","tool_id":"calendar.list","action_category":"read","side_effect_level":"read_only","required":true,"safe_description":"Read calendar metadata."}],"test_fixtures":[{"fixture_key":"list-calendars","tool_id":"calendar.list","action_category":"read","fixture_kind":"policy_preview","safe_input_summary":"Policy-only calendar list probe.","fixture_digest":"sha256:fixture","requires_credentials":true,"expected_outcome":"passed","timeout_seconds":10}],"compatibility":{"platform_min_version":"0.1.0"},"safe_documentation":{"summary":"Safe operator documentation.","documentation_digest":"sha256:docs","redaction_classification":"safe","support_contacts":["ops@example.com"]},"artifact_digests":{"package":"sha256:artifact","documentation":"sha256:docs"}}'
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions/validate" \
  -d '{"manifest":'"$CALENDAR_SKILL_MANIFEST"',"approved_integration_refs":["tool:calendar:v1"]}'
```

Expected `200`:

```json
{"status":"passed","safe_summary":{"slug":"calendar-assistant","semantic_version":"1.2.3"},"findings":[]}
```

### 9.3 POST /admin/skill-registry/packages/{slug}/versions

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions" \
  -d '{"manifest":'"$CALENDAR_SKILL_MANIFEST"',"approved_integration_refs":["tool:calendar:v1"],"artifact_digest":"sha256:artifact"}'
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
export AGENT_SUITE_REVISION="$(jq -r '.revision' /tmp/curl-agent-suite.json)"
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
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","name":"Curl Draft Workflow Guard Updated","target_type":"workflow_draft","target_id":"curl-triage-flow","target_version":"draft-rev-1","required_for_publish":true,"revision":'"$AGENT_SUITE_REVISION"'}' \
  | tee /tmp/curl-agent-suite-updated.json
export AGENT_SUITE_REVISION="$(jq -r '.revision' /tmp/curl-agent-suite-updated.json)"
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
curl -sS -H "$ACME_HEADER" "$BASE_URL/admin/agent-tests/runs?suite_id=$AGENT_SUITE_ID"
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
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","filters":{"model_id":"gpt-test"}}' \
  | tee /tmp/curl-usage-export.json
export USAGE_EXPORT_ID="$(jq -r '.usage_export_request_id' /tmp/curl-usage-export.json)"
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

Expected `200`:

```json
{"ok":true,"messages":["ignored"]}
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

### 16.5a GET /admin/runs/{workflow_run_id}/agent-graph with replay evidence

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/agent-graph?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.source == "runtime_run" and .provenance.workflow_run_id == env.RUNTIME_RUN_ID and (.nodes | length) >= 4 and (.edges | length) >= 3 and ([.nodes[].status] | index("succeeded")) != null and ([.nodes[].status] | index("retry_scheduled")) != null and (.provenance.evidence_counts.interaction_evidence // 0) >= 1 and ([.edges[].references[]? | select(.reference_type == "interaction_evidence")] | length) >= 1'
```

Expected `200`:

```json
true
```

### 16.6 POST /admin/runs/{workflow_run_id}/exports

```bash
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/exports" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","lineage_scope":"single_run","recipient_scope":"tenant_auditor","included_sections":["timeline","bundle"],"excluded_sections":[],"reason":"curl audit evidence validation"}'
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

### 16.8 Runtime agent graph cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" "$BASE_URL/admin/runs/$RUNTIME_RUN_ID/agent-graph?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":{"category":"forbidden","message":"admin inspection denied","trace_id":"trace-..."}}
```

## 17. Design Review Domain APIs

These endpoints cover the Spec 060 design review domain foundation. The first
step seeds reviewer round evidence that is not yet created through a public
route, then creates an API session used by the remaining session commands.

### 17.1 POST /admin/design-reviews/sessions

```bash
QA060_SEED_OUTPUT="$(uv run python scripts/qa/seed_design_review_qa060.py)"
printf '%s\n' "$QA060_SEED_OUTPUT"
export DESIGN_REVIEW_SEEDED_SESSION_ID="$(printf '%s\n' "$QA060_SEED_OUTPUT" | sed -n 's/^design_review_session_id=//p')"
export DESIGN_REVIEW_SEEDED_ROUND_ID="$(printf '%s\n' "$QA060_SEED_OUTPUT" | sed -n 's/^design_review_round_id=//p')"
DESIGN_REVIEW_CREATE_RESPONSE="$(curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","request_summary":"QA060 curl design review session.","quorum_policy_key":"four_of_five_no_blockers","idempotency_key":"qa060-curl-create"}')"
printf '%s\n' "$DESIGN_REVIEW_CREATE_RESPONSE" | jq .
export DESIGN_REVIEW_SESSION_ID="$(printf '%s\n' "$DESIGN_REVIEW_CREATE_RESPONSE" | jq -r '.design_review_session_id')"
export DESIGN_REVIEW_REVISION_ID="$(printf '%s\n' "$DESIGN_REVIEW_CREATE_RESPONSE" | jq -r '.current_revision.design_revision_id')"
test "$DESIGN_REVIEW_SESSION_ID" != "null"
test "$DESIGN_REVIEW_REVISION_ID" != "null"
```

Expected `201`:

```json
{"design_review_session_id":"11111111-1717-1717-1717-111111111111","tenant_id":"11111111-1111-1111-1111-111111111111","status":"draft","replayed":false,"current_revision":{"revision_number":1}}
```

### 17.2 POST /admin/design-reviews/sessions idempotent replay

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","request_summary":"QA060 curl replay should return the existing session.","quorum_policy_key":"four_of_five_no_blockers","idempotency_key":"qa060-curl-create"}' \
  | jq -e --arg session_id "$DESIGN_REVIEW_SESSION_ID" '.design_review_session_id == $session_id and .replayed == true'
```

Expected `200`:

```json
true
```

### 17.3 GET /admin/design-reviews/sessions

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.items | length >= 1'
```

Expected `200`:

```json
true
```

### 17.4 GET /admin/design-reviews/sessions/{session_id}

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SESSION_ID?tenant_id=$ACME_TENANT_ID" \
  | jq -e --arg session_id "$DESIGN_REVIEW_SESSION_ID" '.design_review_session_id == $session_id and (.revisions | length) == 1'
```

Expected `200`:

```json
true
```

### 17.5 GET /admin/design-reviews/sessions/{session_id}/revisions

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SESSION_ID/revisions?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.items[0].revision_number == 1'
```

Expected `200`:

```json
true
```

### 17.6 GET /admin/design-reviews/sessions/{session_id}/rounds

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SEEDED_SESSION_ID/rounds?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.items[0].round_number == 1'
```

Expected `200`:

```json
true
```

### 17.7 GET /admin/design-reviews/rounds/{round_id}

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/rounds/$DESIGN_REVIEW_SEEDED_ROUND_ID?tenant_id=$ACME_TENANT_ID" \
  | jq -e '(.assignments | length) >= 2 and (.verdicts | length) >= 2'
```

Expected `200`:

```json
true
```

### 17.8 GET /admin/design-reviews/rounds/{round_id}/quorum-decision

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/rounds/$DESIGN_REVIEW_SEEDED_ROUND_ID/quorum-decision?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.status == "revision_required" and .next_action == "revise"'
```

Expected `200`:

```json
true
```

### 17.9 POST /admin/design-reviews/sessions/{session_id}/manual-decisions

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SESSION_ID/manual-decisions" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","decision_type":"revise","safe_rationale":"QA060 curl asks for clearer design notes.","idempotency_key":"qa060-curl-manual"}' \
  | jq -e '.decision_type == "revise" and .replayed == false'
```

Expected `201`:

```json
true
```

### 17.10 GET /admin/design-reviews/sessions/{session_id}/manual-decisions

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SESSION_ID/manual-decisions?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.items | length == 1'
```

Expected `200`:

```json
true
```

### 17.11 GET /admin/design-reviews/sessions/{session_id}/handoff

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SEEDED_SESSION_ID/handoff?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.status == "ready" and .state.kind == "ready"'
```

Expected `200`:

```json
true
```

### 17.12 GET /admin/design-reviews/sessions empty tenant state

```bash
curl -sS -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions?tenant_id=$GLOBEX_TENANT_ID" \
  | jq -e '.items == [] and .state.kind == "empty"'
```

Expected `200`:

```json
true
```

### 17.13 Design review cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_REVIEW_SESSION_ID?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":"design review access denied"}
```

### 17.14 Seed QA062 design review coordinator loop

```bash
QA062_SEED_OUTPUT="$(uv run python scripts/qa/seed_design_review_coordinator_qa062.py)"
printf '%s\n' "$QA062_SEED_OUTPUT"
export DESIGN_COORDINATOR_SEEDED_SESSION_ID="$(printf '%s\n' "$QA062_SEED_OUTPUT" | sed -n 's/^design_review_session_id=//p')"
export DESIGN_COORDINATOR_SEEDED_ROUND_ID="$(printf '%s\n' "$QA062_SEED_OUTPUT" | sed -n 's/^design_review_round_id=//p')"
export DESIGN_COORDINATOR_WORKFLOW_BUNDLE_ID="62626262-6262-6262-6262-626262626262"
test "$DESIGN_COORDINATOR_SEEDED_SESSION_ID" != ""
test "$DESIGN_COORDINATOR_SEEDED_ROUND_ID" != ""
curl -sS "$BASE_URL/health/live" >/dev/null
```

Expected `200`:

```json
{"quorum_status":"passed","handoff_state":"ready"}
```

### 17.15 GET /admin/design-reviews/sessions/{session_id}/coordinator

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SEEDED_SESSION_ID/coordinator?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.session.status == "approved" and .handoff.state.kind == "ready" and .latest_quorum_decision.status == "passed"'
```

Expected `200`:

```json
true
```

### 17.16 POST /admin/design-reviews/sessions for coordinator revision flow

```bash
DESIGN_COORDINATOR_CREATE_RESPONSE="$(curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","request_summary":"QA062 curl coordinator revision flow.","quorum_policy_key":"four_of_five_no_blockers","workflow_version_bundle_id":"'"$DESIGN_COORDINATOR_WORKFLOW_BUNDLE_ID"'","idempotency_key":"qa062-curl-session"}')"
printf '%s\n' "$DESIGN_COORDINATOR_CREATE_RESPONSE" | jq .
export DESIGN_COORDINATOR_SESSION_ID="$(printf '%s\n' "$DESIGN_COORDINATOR_CREATE_RESPONSE" | jq -r '.design_review_session_id')"
test "$DESIGN_COORDINATOR_SESSION_ID" != "null"
```

Expected `201`:

```json
{"status":"draft","replayed":false}
```

### 17.17 POST /admin/design-reviews/sessions/{session_id}/coordinator/launch-round

```bash
DESIGN_COORDINATOR_LAUNCH_RESPONSE="$(curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SESSION_ID/coordinator/launch-round" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","workflow_version_bundle_id":"'"$DESIGN_COORDINATOR_WORKFLOW_BUNDLE_ID"'","reviewers":[{"reviewer_key":"reviewer-0","role_key":"reviewer-role-0","enabled":true},{"reviewer_key":"reviewer-1","role_key":"reviewer-role-1","enabled":true},{"reviewer_key":"reviewer-2","role_key":"reviewer-role-2","enabled":true},{"reviewer_key":"reviewer-3","role_key":"reviewer-role-3","enabled":true},{"reviewer_key":"reviewer-4","role_key":"reviewer-role-4","enabled":true}],"idempotency_key":"qa062-curl-launch"}')"
printf '%s\n' "$DESIGN_COORDINATOR_LAUNCH_RESPONSE" | jq .
export DESIGN_COORDINATOR_ROUND_ID="$(printf '%s\n' "$DESIGN_COORDINATOR_LAUNCH_RESPONSE" | jq -r '.round.design_review_round_id')"
export DESIGN_COORDINATOR_RUN_ID="$(printf '%s\n' "$DESIGN_COORDINATOR_LAUNCH_RESPONSE" | jq -r '.workflow_run_id')"
test "$DESIGN_COORDINATOR_ROUND_ID" != "null"
test "$DESIGN_COORDINATOR_RUN_ID" != "null"
```

Expected `201`:

```json
{"next_action":"wait_for_runtime","replayed":false}
```

### 17.18 GET coordinator state after launch

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SESSION_ID/coordinator?tenant_id=$ACME_TENANT_ID" \
  | jq -e --arg round_id "$DESIGN_COORDINATOR_ROUND_ID" '.session.status == "reviewing" and .latest_round.design_review_round_id == $round_id'
```

Expected `200`:

```json
true
```

### 17.19 POST /admin/design-reviews/rounds/{round_id}/coordinator/complete revision required

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/rounds/$DESIGN_COORDINATOR_ROUND_ID/coordinator/complete" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","safe_synthesis_summary":"QA062 curl council requests revision.","next_revision_summary":"QA062 curl revision summary.","idempotency_key":"qa062-curl-complete-revision","verdicts":[{"reviewer_key":"reviewer-0","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer zero approved.","output_digest":"qa062-r0"},{"reviewer_key":"reviewer-1","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer one approved.","output_digest":"qa062-r1"},{"reviewer_key":"reviewer-2","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer two approved.","output_digest":"qa062-r2"},{"reviewer_key":"reviewer-3","verdict":"changes_requested","score":3,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer three requested changes.","output_digest":"qa062-r3"},{"reviewer_key":"reviewer-4","verdict":"changes_requested","score":3,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer four requested changes.","output_digest":"qa062-r4"}]}' \
  | jq -e '.quorum_decision.status == "revision_required" and .created_revision.revision_number == 2 and .next_action == "revise"'
```

Expected `200`:

```json
true
```

### 17.20 POST coordinator launch second round

```bash
DESIGN_COORDINATOR_SECOND_LAUNCH_RESPONSE="$(curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SESSION_ID/coordinator/launch-round" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","workflow_version_bundle_id":"'"$DESIGN_COORDINATOR_WORKFLOW_BUNDLE_ID"'","reviewers":[{"reviewer_key":"reviewer-0","role_key":"reviewer-role-0","enabled":true},{"reviewer_key":"reviewer-1","role_key":"reviewer-role-1","enabled":true},{"reviewer_key":"reviewer-2","role_key":"reviewer-role-2","enabled":true},{"reviewer_key":"reviewer-3","role_key":"reviewer-role-3","enabled":true},{"reviewer_key":"reviewer-4","role_key":"reviewer-role-4","enabled":true}],"idempotency_key":"qa062-curl-launch-second"}')"
printf '%s\n' "$DESIGN_COORDINATOR_SECOND_LAUNCH_RESPONSE" | jq .
export DESIGN_COORDINATOR_SECOND_ROUND_ID="$(printf '%s\n' "$DESIGN_COORDINATOR_SECOND_LAUNCH_RESPONSE" | jq -r '.round.design_review_round_id')"
test "$DESIGN_COORDINATOR_SECOND_ROUND_ID" != "null"
```

Expected `201`:

```json
{"round":{"round_number":2}}
```

### 17.21 POST coordinator completion with manual resolution

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/rounds/$DESIGN_COORDINATOR_SECOND_ROUND_ID/coordinator/complete" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","safe_synthesis_summary":"QA062 curl council found a blocker.","idempotency_key":"qa062-curl-complete-manual","verdicts":[{"reviewer_key":"reviewer-0","verdict":"approved","score":5,"blocking_issue_count":1,"safe_feedback_summary":"Reviewer zero found a blocker.","output_digest":"qa062-m0"},{"reviewer_key":"reviewer-1","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer one approved.","output_digest":"qa062-m1"},{"reviewer_key":"reviewer-2","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer two approved.","output_digest":"qa062-m2"},{"reviewer_key":"reviewer-3","verdict":"approved","score":5,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer three approved.","output_digest":"qa062-m3"},{"reviewer_key":"reviewer-4","verdict":"changes_requested","score":3,"blocking_issue_count":0,"safe_feedback_summary":"Reviewer four requested changes.","output_digest":"qa062-m4"}]}' \
  | jq -e '.quorum_decision.status == "manual_resolution" and .session.status == "manual_resolution" and .next_action == "manual_decision"'
```

Expected `200`:

```json
true
```

### 17.22 POST /admin/design-reviews/sessions/{session_id}/coordinator/manual-decisions

```bash
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SESSION_ID/coordinator/manual-decisions" \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","round_id":"'"$DESIGN_COORDINATOR_SECOND_ROUND_ID"'","decision_type":"revise","safe_rationale":"QA062 curl manual decision requests a revision.","next_revision_summary":"QA062 curl manual revision summary.","idempotency_key":"qa062-curl-manual-revise"}' \
  | jq -e '.manual_decision.decision_type == "revise" and .created_revision.revision_number == 3 and .next_action == "launch_round"'
```

Expected `201`:

```json
true
```

### 17.23 Coordinator cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/design-reviews/sessions/$DESIGN_COORDINATOR_SESSION_ID/coordinator?tenant_id=$ACME_TENANT_ID"
```

Expected `403`:

```json
{"detail":"design review access denied"}
```

### 17.24 Seed QA063 design review workspace records

```bash
QA063_SEED_OUTPUT="$(uv run python scripts/qa/seed_design_review_workspace_qa063.py)"
printf '%s\n' "$QA063_SEED_OUTPUT"
export DESIGN_WORKSPACE_SESSION_ID="$(printf '%s\n' "$QA063_SEED_OUTPUT" | sed -n 's/^design_review_session_id=//p')"
export DESIGN_WORKSPACE_ROUND_ID="$(printf '%s\n' "$QA063_SEED_OUTPUT" | sed -n 's/^design_review_round_id=//p')"
export DESIGN_WORKSPACE_WORKFLOW_BUNDLE_ID="63636363-6363-6363-6363-636363636363"
test "$DESIGN_WORKSPACE_SESSION_ID" != ""
test "$DESIGN_WORKSPACE_ROUND_ID" != ""
curl -sS "$BASE_URL/health/live" >/dev/null
```

Expected `200`:

```json
{"handoff_state":"ready","quorum_status":"passed"}
```

### 17.25 GET /admin/app/design-reviews/bootstrap.json

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/design-reviews/bootstrap.json?tenant_id=$ACME_TENANT_ID&session_id=$DESIGN_WORKSPACE_SESSION_ID" \
  | jq -e '.selected_session.session.design_review_session_id == env.DESIGN_WORKSPACE_SESSION_ID and .selected_session.handoff.state.kind == "ready" and .selected_session.rounds[-1].quorum_decision.status == "passed" and (.selected_session.rounds[-1].verdicts | length) == 5 and .actions.create_session.href == "/admin/design-reviews/sessions"'
```

Expected `200`:

```json
true
```

### 17.26 GET /admin/app/design-reviews/bootstrap.json empty tenant

```bash
curl -sS -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/app/design-reviews/bootstrap.json?tenant_id=$GLOBEX_TENANT_ID" \
  | jq -e '.state.state == "empty" and (.sessions | length) == 0 and .selected_session == null'
```

Expected `200`:

```json
true
```

### 17.27 GET /admin/app/design-reviews

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/design-reviews?tenant_id=$ACME_TENANT_ID" \
  | grep -q 'id="root"'
```

Expected `200`:

```html
id="root"
```

### 17.28 Design review workspace cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" \
  "$BASE_URL/admin/app/design-reviews/bootstrap.json?tenant_id=$ACME_TENANT_ID&session_id=$DESIGN_WORKSPACE_SESSION_ID"
```

Expected `403`:

```json
{"detail":"cross_tenant_scope"}
```

### 17.29 POST /admin/design-reviews/templates/council/install

```bash
DESIGN_TEMPLATE_INSTALL_OUTPUT="$(curl -sS -H "$ACME_HEADER" -H 'Content-Type: application/json' \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","idempotency_key":"curl-qa064-install","safe_mode":"both"}' \
  "$BASE_URL/admin/design-reviews/templates/council/install")"
printf '%s\n' "$DESIGN_TEMPLATE_INSTALL_OUTPUT"
export DESIGN_TEMPLATE_DRAFT_ID="$(printf '%s\n' "$DESIGN_TEMPLATE_INSTALL_OUTPUT" | jq -r '.workflow_draft_id')"
test "$DESIGN_TEMPLATE_DRAFT_ID" != ""
printf '%s\n' "$DESIGN_TEMPLATE_INSTALL_OUTPUT" \
  | jq -e '.ready_to_publish == true and .required_evidence_status == "passing" and .publish_gate_status == "ready" and (.evidence_modes | index("deterministic")) != null and (.evidence_modes | index("model backed safe")) != null'
```

Expected `201`:

```json
true
```

### 17.30 POST /admin/design-reviews/templates/council/install replay

```bash
curl -sS -H "$ACME_HEADER" -H 'Content-Type: application/json' \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","idempotency_key":"curl-qa064-install","safe_mode":"both"}' \
  "$BASE_URL/admin/design-reviews/templates/council/install" \
  | jq -e '.replayed == true and .workflow_draft_id == env.DESIGN_TEMPLATE_DRAFT_ID'
```

Expected `200`:

```json
true
```

### 17.31 GET /admin/app/design-reviews/bootstrap.json template setup

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/design-reviews/bootstrap.json?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.template_setup.status == "ready" and .template_setup.workflow_draft_id == env.DESIGN_TEMPLATE_DRAFT_ID and .template_setup.ready_to_publish == true and .template_setup.install_action.href == "/admin/design-reviews/templates/council/install"'
```

Expected `200`:

```json
true
```

### 17.32 Design review template cross-tenant denial

```bash
curl -sS -i -H "$GLOBEX_HEADER" -H 'Content-Type: application/json' \
  -d '{"tenant_id":"'"$ACME_TENANT_ID"'","idempotency_key":"curl-qa064-denied"}' \
  "$BASE_URL/admin/design-reviews/templates/council/install"
```

Expected `403`:

```json
{"detail":"design review template access denied"}
```

## 18. React Admin, Local UI, And URL Surface Smoke

These smoke checks keep the URL walkthrough aligned with the current FastAPI
route inventory, including read-only React admin routes, local auth helper
routes, legacy redirect URLs, and SPA deep links. Canonical JSON APIs above
remain the source of truth for mutation bodies and domain behavior.

### 18.1 GET /admin and /admin/scope redirect URLs

```bash
curl -sS -i -H "$ACME_HEADER" "$BASE_URL/admin"
curl -sS -i -H "$ACME_HEADER" \
  "$BASE_URL/admin/scope?tenant_id=$ACME_TENANT_ID&next=/admin/app/workflows"
```

Expected `303`:

```json
{"detail":"redirect to React admin shell"}
```

### 18.2 React shell missing-auth scenario

```bash
curl -sS -i "$BASE_URL/admin/app/bootstrap.json"
```

Expected `401`:

```json
{"detail":"missing local principal header or cookie"}
```

### 18.3 React shell and migration URL scenarios

```bash
react_shell_urls=(
  "/admin/app?tenant_id=$ACME_TENANT_ID"
  "/admin/app/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/home.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/config.json"
  "/admin/app/manifest.json"
  "/admin/app/search.json?tenant_id=$ACME_TENANT_ID&q=workflow"
  "/admin/app/migration?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/shell.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/routes.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/decommission-inventory.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/live-data-inventory.json?tenant_id=$ACME_TENANT_ID&ci_mode=true&source_scan=false"
  "/admin/app/migration/transitional-labels.json?tenant_id=$ACME_TENANT_ID&ci_mode=true&source_scan=false"
  "/admin/app/migration/jinja-inventory.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/migration/rollback.json?tenant_id=$ACME_TENANT_ID"
)
for url in "${react_shell_urls[@]}"; do
  curl -sS -H "$ACME_HEADER" "$BASE_URL$url" >/dev/null
done
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/home.json?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.quick_actions[] | select(.action_id == "workflow_onboarding" and (.href | contains("/admin/app/workflows/onboarding")))'
```

Expected `200`:

```json
{"detail":"React shell and migration URLs returned successfully"}
```

### 18.4 React workflow URL scenarios

```bash
cat >/tmp/curl-react-workflow-create.json <<JSON
{
  "idempotency_key": "curl-react-workflow-create",
  "scope_type": "tenant",
  "tenant_id": "$ACME_TENANT_ID",
  "workflow_kind": "main_workflow",
  "slug": "curl-react-api-scenario",
  "display_name": "Curl React API Scenario",
  "description": "Created through the React workflow create action.",
  "document": {
    "workflow_key": "curl-react-api-scenario",
    "display_name": "Curl React API Scenario",
    "description": "Created through the React workflow create action.",
    "workflow_kind": "main_workflow",
    "entry_node_key": "start",
    "contracts": [
      {"contract_key": "input", "contract_kind": "workflow_input", "json_schema": {"type": "object"}},
      {"contract_key": "output", "contract_kind": "workflow_output", "json_schema": {"type": "object"}}
    ],
    "roles": [
      {"role_key": "creator", "display_name": "Creator", "purpose": "Validate React create API coverage", "input_contract_key": "input", "output_contract_key": "output", "graph_node_keys": ["start"]}
    ],
    "prompt_profile_references": [],
    "skill_installations": [],
    "nodes": [
      {"node_key": "start", "node_type": "role", "display_name": "Start", "role_key": "creator"},
      {"node_key": "done", "node_type": "terminal", "display_name": "Done"}
    ],
    "edges": [
      {"edge_key": "edge-start-done", "source_node_key": "start", "target_node_key": "done", "edge_type": "success"}
    ],
    "join_policies": [],
    "approval_gates": [],
    "subworkflow_refs": [],
    "test_requirements": [],
    "editor_annotations": {"section_notes": {"metadata": "Curl React create scenario"}, "graph_layout": {}, "collapsed_sections": []}
  }
}
JSON
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-create.json \
  | tee /tmp/curl-react-workflow-create-response.json \
  | jq -e '.status == "accepted" and (.audit_reference_id | startswith("workflow-draft:")) and (.next_action.href | contains("/admin/app/workflows/drafts/"))'
export REACT_CREATED_WORKFLOW_DRAFT_ID="$(jq -r '.audit_reference_id | split(":")[1]' /tmp/curl-react-workflow-create-response.json)"
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$REACT_CREATED_WORKFLOW_DRAFT_ID/detail.json?tenant_id=$ACME_TENANT_ID" \
  | jq -e '.draft.name == "Curl React API Scenario"'
react_workflow_urls=(
  "/admin/app/workflows?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/onboarding?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/new?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/registry.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/create.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/legacy-routes.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/builder.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/lookups.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID"
  "/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/detail.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/publish-gate.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/revisions"
  "/admin/app/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID"
  "/admin/app/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/detail.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/saved-filters/workflows?tenant_id=$ACME_TENANT_ID"
)
for url in "${react_workflow_urls[@]}"; do
  curl -sS -H "$ACME_HEADER" "$BASE_URL$url" >/dev/null
done
```

Expected `200`:

```json
{"detail":"React workflow URLs returned successfully"}
```

### 18.4a React workflow full document save scenarios

```bash
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/detail.json?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-react-workflow-detail.json
export REACT_WORKFLOW_REVISION="$(jq -r '.draft.revision' /tmp/curl-react-workflow-detail.json)"
cat >/tmp/curl-react-workflow-save.json <<JSON
{
  "revision": "$REACT_WORKFLOW_REVISION",
  "idempotency_key": "curl-react-workflow-save",
  "name": "Curl React Workflow Full Document",
  "description": "Saved through the React workflow document route.",
  "change_summary": "Curl React full document save",
  "client_context": {"active_section": "graph", "mutation_source": "curl_testing"},
  "selected_prompt_ref": "coordinator-prompt-profile",
  "selected_profile_ref": "coordinator-runtime-profile",
  "join_policy": "evidence-join",
  "force_stale": false,
  "document": {
    "workflow_key": "curl-triage-flow-copy",
    "display_name": "Curl React Workflow Full Document",
    "description": "Saved through the React workflow document route.",
    "workflow_kind": "main_workflow",
    "entry_node_key": "start",
    "contracts": [
      {"contract_key": "request", "contract_kind": "workflow_input", "json_schema": {"type": "object"}},
      {"contract_key": "finding", "contract_kind": "data_contract", "json_schema": {"type": "object"}},
      {"contract_key": "result", "contract_kind": "workflow_output", "json_schema": {"type": "object"}},
      {"contract_key": "approval-decision", "contract_kind": "approval_decision", "json_schema": {"type": "object"}}
    ],
    "roles": [
      {
        "role_key": "coordinator",
        "display_name": "Coordinator",
        "purpose": "Coordinate the workflow setup review",
        "responsibilities": ["Collect request context", "Prepare final response"],
        "profile_reference_key": "coordinator-prompt-profile",
        "prompt_reference_keys": ["coordinator-prompt-profile"],
        "input_contract_key": "request",
        "output_contract_key": "result",
        "graph_node_keys": ["start"]
      },
      {
        "role_key": "research",
        "display_name": "Research",
        "purpose": "Review workflow setup evidence",
        "responsibilities": ["Summarize durable references"],
        "input_contract_key": "request",
        "output_contract_key": "finding",
        "graph_node_keys": ["research"]
      },
      {
        "role_key": "review",
        "display_name": "Review",
        "purpose": "Check setup risks before approval",
        "responsibilities": ["Assess release readiness"],
        "input_contract_key": "request",
        "output_contract_key": "finding",
        "graph_node_keys": ["review"]
      }
    ],
    "prompt_profile_references": [
      {"reference_key": "coordinator-prompt-profile", "role_key": "coordinator", "agent_key": "coordinator", "agent_kind": "agent", "source_scope": "tenant", "readiness_status": "ready"}
    ],
    "skill_installations": [],
    "nodes": [
      {"node_key": "start", "node_type": "role", "display_name": "Coordinate", "role_key": "coordinator", "editor_position": {"x": 0, "y": 0}},
      {"node_key": "research", "node_type": "role", "display_name": "Research", "role_key": "research", "editor_position": {"x": 220, "y": -80}},
      {"node_key": "review", "node_type": "role", "display_name": "Review", "role_key": "review", "editor_position": {"x": 220, "y": 80}},
      {"node_key": "join", "node_type": "join", "display_name": "Join Evidence", "join_policy_key": "evidence-join", "editor_position": {"x": 460, "y": 0}},
      {"node_key": "approval", "node_type": "approval", "display_name": "Manager Approval", "approval_gate_key": "manager-approval", "editor_position": {"x": 660, "y": 0}},
      {"node_key": "done", "node_type": "terminal", "display_name": "Done"}
    ],
    "edges": [
      {"edge_key": "edge-start-research", "source_node_key": "start", "target_node_key": "research", "contract_key": "request", "edge_type": "success"},
      {"edge_key": "edge-start-review", "source_node_key": "start", "target_node_key": "review", "contract_key": "request", "edge_type": "success"},
      {"edge_key": "edge-research-join", "source_node_key": "research", "target_node_key": "join", "contract_key": "finding", "edge_type": "success"},
      {"edge_key": "edge-review-join", "source_node_key": "review", "target_node_key": "join", "contract_key": "finding", "edge_type": "success"},
      {"edge_key": "edge-join-approval", "source_node_key": "join", "target_node_key": "approval", "contract_key": "result", "edge_type": "success"},
      {"edge_key": "edge-approval-done", "source_node_key": "approval", "target_node_key": "done", "contract_key": "approval-decision", "edge_type": "success"}
    ],
    "join_policies": [
      {"join_policy_key": "evidence-join", "strategy": "quorum", "inbound_edge_keys": ["edge-research-join", "edge-review-join"], "required_branches": ["research", "review"], "quorum_count": 2, "failure_behavior": "block", "output_merge_contract_key": "result"}
    ],
    "approval_gates": [
      {"approval_gate_key": "manager-approval", "display_name": "Manager Approval", "approver_scope": "tenant_admin", "reason": "Review workflow setup changes", "decision_contract_key": "approval-decision", "resume_behavior": "continue_on_approval"}
    ],
    "subworkflow_refs": [],
    "test_requirements": [
      {"requirement_key": "agent-test-bench-pass", "suite_id": "$AGENT_SUITE_ID", "target_type": "workflow_draft", "freshness_policy": "latest_revision", "latest_result_id": "$AGENT_RUN_ID", "latest_result_status": "passed", "safe_summary": "Curl agent test run is passing."}
    ],
    "editor_annotations": {"section_notes": {"metadata": "Curl React full document save"}, "graph_layout": {}, "collapsed_sections": []}
  }
}
JSON
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/save?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-save.json \
  | tee /tmp/curl-react-workflow-save-response.json \
  | jq -e '.status == "accepted" and (.editor_state.document.roles | length) == 3 and (.editor_state.document.prompt_profile_references | length) == 1 and (.editor_state.document.join_policies | length) == 1 and .editor_state.document.test_requirements[0].suite_id == env.AGENT_SUITE_ID and .editor_state.document.editor_annotations.section_notes.metadata == "Curl React full document save"'
export REACT_WORKFLOW_SAVED_REVISION="$(jq -r '.revision' /tmp/curl-react-workflow-save-response.json)"
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/detail.json?tenant_id=$ACME_TENANT_ID" \
  | tee /tmp/curl-react-workflow-reloaded.json \
  | jq -e '.draft.revision == env.REACT_WORKFLOW_SAVED_REVISION and (.draft.document.roles | length) == 3 and .draft.document.join_policies[0].strategy == "quorum" and .draft.document.test_requirements[0].latest_result_status == "passed"'
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/save?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-save.json \
  | tee /tmp/curl-react-workflow-replay.json \
  | jq -e '.status == "idempotent_replay" and .idempotency.replayed == true'
jq '.description = "Different payload with reused idempotency key" | .document.description = "Different payload with reused idempotency key"' \
  /tmp/curl-react-workflow-save.json > /tmp/curl-react-workflow-idempotency-conflict.json
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/save?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-idempotency-conflict.json \
  | tee /tmp/curl-react-workflow-idempotency-conflict-response.json \
  | jq -e '.status == "validation_error" and .validation.findings[0].field_path == "idempotency_key"'
jq '.idempotency_key = "curl-react-workflow-stale" | .force_stale = true' \
  /tmp/curl-react-workflow-save.json > /tmp/curl-react-workflow-stale.json
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/save?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-stale.json \
  | tee /tmp/curl-react-workflow-stale-response.json \
  | jq -e '.status == "stale_conflict"'
jq '.revision = env.REACT_WORKFLOW_SAVED_REVISION | .idempotency_key = "curl-react-workflow-invalid" | .document.edges += [{"edge_key":"edge-missing-node","source_node_key":"start","target_node_key":"missing-node"}]' \
  /tmp/curl-react-workflow-save.json > /tmp/curl-react-workflow-invalid.json
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/workflows/drafts/$WORKFLOW_COPY_DRAFT_ID/save?tenant_id=$ACME_TENANT_ID" \
  --data @/tmp/curl-react-workflow-invalid.json \
  | tee /tmp/curl-react-workflow-invalid-response.json \
  | jq -e '.status == "validation_error" and .validation.findings[0].section == "graph"'
```

Expected `200`:

```json
true
```

### 18.5 React governance URL scenarios

```bash
react_governance_urls=(
  "/admin/app/governance?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/providers.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/providers/$PROVIDER_CONNECTION_ID"
  "/admin/app/governance/providers/$PROVIDER_CONNECTION_ID/edit"
  "/admin/app/governance/prompts.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/prompts/$PROMPT_LINEAGE_ID/edit"
  "/admin/app/governance/prompts/versions/$PROMPT_VERSION_ID"
  "/admin/app/governance/prompts/$PROMPT_LINEAGE_ID/history"
  "/admin/app/governance/prompts/$PROMPT_LINEAGE_ID/preview"
  "/admin/app/governance/profiles.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/profiles/$AGENT_PROFILE_ID/edit"
  "/admin/app/governance/profiles/versions/$AGENT_PROFILE_VERSION_ID"
  "/admin/app/governance/profiles/$AGENT_PROFILE_ID/history"
  "/admin/app/governance/profiles/resolve"
  "/admin/app/governance/routing"
  "/admin/app/governance/history"
  "/admin/app/governance/history.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/governance/provenance/$RUNTIME_RUN_ID"
  "/admin/app/governance/provenance/$RUNTIME_RUN_ID.json?tenant_id=$ACME_TENANT_ID"
)
for url in "${react_governance_urls[@]}"; do
  curl -sS -H "$PLATFORM_HEADER" "$BASE_URL$url" >/dev/null
done
curl -sS -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/governance/legacy-routes.json?tenant_id=$ACME_TENANT_ID" \
  >/dev/null
```

Expected `200`:

```json
{"detail":"React governance URLs returned successfully"}
```

### 18.6 React skills, test bench, memberships, channels, and usage URLs

```bash
react_tenant_workspace_urls=(
  "/admin/app/skills?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/legacy-routes.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/packages/calendar-assistant"
  "/admin/app/skills/packages/calendar-assistant/candidate"
  "/admin/app/skills/packages/calendar-assistant/versions/1.2.3"
  "/admin/app/skills/available-versions?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/discovery.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/installations?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/installations.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/installations/$SKILL_INSTALLATION_ID"
  "/admin/app/skills/installations/$SKILL_INSTALLATION_ID/credentials"
  "/admin/app/skills/diagnostics"
  "/admin/app/skills/diagnostics.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/skills/audit.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/suites?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/suites/$AGENT_SUITE_ID?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/runs.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/runs/$AGENT_RUN_ID.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/gates.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/test-bench/audit.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/memberships?tenant_id=$ACME_TENANT_ID"
  "/admin/app/memberships/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/memberships/access-history.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/memberships/audit.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/runs?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/runs?tenant_id=$ACME_TENANT_ID&workflow_id=curl-triage-flow"
  "/admin/app/channels/runs/$CHANNEL_RUN_ID?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/shell.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/telegram/deliveries.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/runs/$CHANNEL_RUN_ID/status.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/channels/briefing/preferences.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/usage?tenant_id=$ACME_TENANT_ID"
  "/admin/app/usage/bootstrap.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/usage/events.json?tenant_id=$ACME_TENANT_ID"
  "/admin/app/usage/exports/$USAGE_EXPORT_ID"
  "/admin/app/usage/exports/$USAGE_EXPORT_ID.json?tenant_id=$ACME_TENANT_ID"
)
for url in "${react_tenant_workspace_urls[@]}"; do
  curl -sS -H "$ACME_HEADER" "$BASE_URL$url" >/dev/null
done
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/test-bench/suites?tenant_id=$ACME_TENANT_ID" \
  -d '{"name":"Curl React Test Bench Guard","description":"React route mutation coverage.","target_type":"workflow_draft","target_id":"curl-triage-flow","target_revision":"draft-rev-1","default_safe_mode":"mock_model","pass_threshold":0.95,"required_for_publish":true,"idempotency_key":"react-suite-curl-001"}' \
  | tee /tmp/curl-react-test-bench-suite.json \
  | jq -e '.status == "accepted" and .suite.summary.suite_name == "Curl React Test Bench Guard"'
export REACT_AGENT_SUITE_ID="$(jq -r '.suite.summary.suite_id' /tmp/curl-react-test-bench-suite.json)"
export REACT_AGENT_SUITE_REVISION="$(jq -r '.suite.summary.suite_revision' /tmp/curl-react-test-bench-suite.json)"
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/test-bench/suites/$REACT_AGENT_SUITE_ID/cases?tenant_id=$ACME_TENANT_ID" \
  -d '{"name":"React route case","fixture_summary":"Fixture uses safe workflow setup summary.","expected_contract_summary":"Summary status is required.","assertions":[],"evaluator_reference_id":"react-curl-evaluator","idempotency_key":"react-case-curl-001"}' \
  | tee /tmp/curl-react-test-bench-case.json \
  | jq -e '.status == "accepted" and .case.case_revision != null'
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/test-bench/suites/$REACT_AGENT_SUITE_ID/runs?tenant_id=$ACME_TENANT_ID" \
  -d '{"target_revision":"draft-rev-1","safe_mode":"real_model_side_effects_disabled","run_reason":"Curl React mutation coverage","idempotency_key":"react-run-curl-001"}' \
  | tee /tmp/curl-react-test-bench-run.json \
  | jq -e '.status == "accepted" and .run.progress.status == "passed" and .run.publish_gate.gate_id != null'
export REACT_AGENT_GATE_ID="$(jq -r '.run.publish_gate.gate_id' /tmp/curl-react-test-bench-run.json)"
curl -sS -X POST -H "$ACME_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/test-bench/gates/$REACT_AGENT_GATE_ID/refresh?tenant_id=$ACME_TENANT_ID" \
  -d '{"target_revision":"draft-rev-1","idempotency_key":"react-gate-curl-001"}' \
  | tee /tmp/curl-react-test-bench-gate.json \
  | jq -e '.status == "accepted" and .gate.evidence_status == "passed" and .gate.target_revision == "draft-rev-1"'
curl -sS -i -H "$ACME_HEADER" \
  "$BASE_URL/admin/app/test-bench/artifacts/00000000-0000-0000-0000-000000000000.json?tenant_id=$ACME_TENANT_ID"
```

Expected `404`:

```json
{"detail":"not_found"}
```

### 18.7 React operations URL scenarios

```bash
react_operations_urls=(
  "/admin/app/operations"
  "/admin/app/operations.json"
  "/admin/app/operations.json?run_id=$RUNTIME_RUN_ID"
  "/admin/app/operations/runs/$RUNTIME_RUN_ID.json?tenant_id=$ACME_TENANT_ID"
)
for url in "${react_operations_urls[@]}"; do
  curl -sS -H "$PLATFORM_HEADER" "$BASE_URL$url" >/dev/null
done
curl -sS -X POST -H "$PLATFORM_HEADER" -H "$JSON_HEADER" \
  "$BASE_URL/admin/app/operations/export" \
  -d '{"range":"60m","included_sections":["summary","logs","run_debug","reliability","exports"]}' >/dev/null
```

Expected `200`:

```json
{"detail":"React operations URLs returned successfully"}
```

### 18.8 Legacy HTML redirect URL scenarios

```bash
platform_legacy_redirect_urls=(
  "/admin/workflows/ui?tenant_id=$ACME_TENANT_ID"
  "/admin/workflows/new?tenant_id=$ACME_TENANT_ID"
  "/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/editor"
  "/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/revisions/ui"
  "/admin/workflows/drafts/$WORKFLOW_DRAFT_ID/publish-gate/ui"
  "/admin/workflows/versions/$WORKFLOW_VERSION_BUNDLE_ID/detail"
  "/admin/model-providers"
  "/admin/model-providers/new"
  "/admin/model-providers/catalog"
  "/admin/model-providers/$PROVIDER_CONNECTION_ID"
  "/admin/model-providers/$PROVIDER_CONNECTION_ID/edit"
  "/admin/prompt-runtime/prompts?tenant_id=$ACME_TENANT_ID"
  "/admin/prompt-runtime/prompts/new?tenant_id=$ACME_TENANT_ID"
  "/admin/prompt-runtime/prompts/$PROMPT_LINEAGE_ID/edit"
  "/admin/prompt-runtime/prompts/versions/$PROMPT_VERSION_ID"
  "/admin/prompt-runtime/prompts/$PROMPT_LINEAGE_ID/history"
  "/admin/prompt-runtime/prompts/$PROMPT_LINEAGE_ID/preview"
  "/admin/prompt-runtime/profiles?tenant_id=$ACME_TENANT_ID"
  "/admin/prompt-runtime/profiles/new?tenant_id=$ACME_TENANT_ID"
  "/admin/prompt-runtime/profiles/$AGENT_PROFILE_ID/edit"
  "/admin/prompt-runtime/profiles/versions/$AGENT_PROFILE_VERSION_ID"
  "/admin/prompt-runtime/profiles/$AGENT_PROFILE_ID/history"
  "/admin/prompt-runtime/profiles/resolve"
  "/admin/config/ui?tenant_id=$ACME_TENANT_ID"
  "/admin/config/ui/history?tenant_id=$ACME_TENANT_ID"
  "/admin/config/ui/runs/$RUNTIME_RUN_ID/provenance?tenant_id=$ACME_TENANT_ID"
  "/admin/skill-registry/ui/packages"
  "/admin/skill-registry/ui/packages/new"
  "/admin/skill-registry/ui/packages/calendar-assistant"
  "/admin/skill-registry/ui/packages/calendar-assistant/candidate"
  "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3"
  "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3/grants"
  "/admin/skill-execution/ui/diagnostics?tenant_id=$ACME_TENANT_ID"
  "/admin/agent-tests/ui?tenant_id=$ACME_TENANT_ID"
  "/admin/agent-tests/ui/suites/new?tenant_id=$ACME_TENANT_ID"
  "/admin/agent-tests/ui/suites/$AGENT_SUITE_ID?tenant_id=$ACME_TENANT_ID"
  "/admin/agent-tests/ui/runs/$AGENT_RUN_ID?tenant_id=$ACME_TENANT_ID"
  "/admin/briefing-preferences?tenant_id=$ACME_TENANT_ID"
  "/admin/usage?tenant_id=$ACME_TENANT_ID"
  "/admin/usage/exports/$USAGE_EXPORT_ID"
  "/admin/memberships?tenant_id=$ACME_TENANT_ID"
  "/admin/telegram?tenant_id=$ACME_TENANT_ID"
  "/admin/operations"
  "/admin/reliability/ui/"
  "/admin/reliability/ui/breakers"
  "/admin/reliability/ui/dead-letters"
)
for url in "${platform_legacy_redirect_urls[@]}"; do
  curl -sS -i -H "$PLATFORM_HEADER" "$BASE_URL$url" >/dev/null
done

tenant_legacy_redirect_urls=(
  "/admin/skill-registry/ui/available-versions?tenant_id=$ACME_TENANT_ID"
  "/admin/skill-registry/ui/installations?tenant_id=$ACME_TENANT_ID"
  "/admin/skill-registry/ui/installations/$SKILL_INSTALLATION_ID"
  "/admin/skill-registry/ui/installations/$SKILL_INSTALLATION_ID/credentials"
  "/runs"
  "/runs/new?tenant_id=$ACME_TENANT_ID"
  "/runs/$CHANNEL_RUN_ID"
)
for url in "${tenant_legacy_redirect_urls[@]}"; do
  curl -sS -i -H "$ACME_HEADER" "$BASE_URL$url" >/dev/null
done
```

Expected `303`:

```json
{"detail":"legacy URL redirects returned successfully"}
```

## 19. Coverage Checklist

The walkthrough covers the JSON/API and URL-surface scenarios from specs 001
through 069:

- Operations foundation: `/health/live`, `/health/ready`, `/version`, `/dependencies`
- Auth and access: `/auth/me`, `/auth/tenant-context/{tenant_id}`, `/auth/local-login.json`, `/auth/local-login`, `/auth/local-logout`, `/admin/tenants/{tenant_id}/role-grants`, `/admin/role-grants`, `/admin/support-overrides`, `/admin/support-overrides/{support_override_request_id}/approve`
- Admin shell and saved filters: `/admin`, `/admin/scope`, `/admin/filters/{admin_area}.json`, `/admin/filters/{admin_area}`, `/admin/filters/{admin_area}/{filter_id}/restore`, and delete aliases for `/admin/filters/{admin_area}/{filter_id}`
- Workflow registry: all `/admin/workflows` JSON endpoints, including draft and published Agent Communication Graph JSON projections, plus React full document save, replay, stale conflict, and invalid graph validation coverage
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
- Design review domain foundation, coordinator, workspace bootstrap, and reusable template setup: all `/admin/design-reviews` JSON endpoints and `/admin/app/design-reviews/bootstrap.json`
- React admin shell and migration: `/admin/app`, `/admin/app/bootstrap.json`, `/admin/app/home.json`, `/admin/app/config.json`, `/admin/app/manifest.json`, `/admin/app/search.json`, and all `/admin/app/migration` JSON inventories, including live-data and transitional-label scans
- React admin workspaces: read URL scenarios for `/admin/app/workflows`, `/admin/app/governance`, `/admin/app/skills`, `/admin/app/test-bench`, `/admin/app/memberships`, `/admin/app/channels`, `/admin/app/usage`, `/admin/app/operations`, `/admin/app/design-reviews`, and SPA deep links under those workspaces
- Legacy and HTML URL aliases: redirect smoke coverage for workflow, governance, model-provider, prompt/profile, skill registry, skill execution, test bench, briefing, usage, memberships, Telegram, operations, reliability, and channel-run UI routes

React admin mutation facades under `/admin/app/...` are represented by the
canonical JSON mutations above plus the React URL smoke sections. Their request
body behavior is covered by the focused API, contract, and browser QA suites so
this walkthrough can stay deterministic and side-effect bounded.
