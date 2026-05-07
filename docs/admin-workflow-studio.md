# Admin Workflow Studio

The admin workflow studio is now implemented end to end for Spec `003`.
Admins can author drafts, persist immutable revisions, validate publish
readiness, publish immutable version bundles, inspect version detail, and grant
tenant access to platform-scoped published assets.

## Main Surfaces

- JSON API: `/admin/workflows`
- React browser registry: `/admin/app/workflows`
- React draft editor: `/admin/app/workflows/drafts/{workflow_draft_id}`
- React version detail: `/admin/app/workflows/versions/{workflow_version_bundle_id}`
- Local QA browser login: `/auth/local-login?redirect_to=/admin/app/workflows`

## Local QA Flow

1. Set `AUTH_MODE=local_principal`.
2. Seed the `acme` tenant row in Postgres before using `tenant-admin-acme`.
3. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --reload`.
4. Open [http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows).
5. Choose `tenant-admin-acme` or `platform-admin`.
6. Continue to the React registry UI without a header-extension workflow.

Why the tenant seed is required:

- local principal auth includes a concrete `tenant_id`
- access-decision audit rows reference `tenants.tenant_id`
- tenant-scoped requests fail early if that tenant row is missing

## Validation Rules

The validator now returns field-targeted blocking or advisory findings for:

- missing input or output contract references
- non-exact skill versions such as `latest`
- secret-like or delegated-credential-like refs in tool policy or runtime ref fields
- missing or inaccessible published subworkflow version refs
- join-policy shape mismatches, including invalid quorum settings
- approval-gate scope and decision-contract mismatches
- breaking contract changes against the latest published lineage version

## Publish And Sharing Behavior

- Publish requires the current draft revision and the latest non-superseded
  passing validation result.
- Publish writes a compiled JSON bundle artifact, records an immutable workflow
  version bundle row, stores the compiled digest, and pins the run-version
  blueprint metadata.
- Published source drafts become immutable.
- Platform-scoped published versions can be shared to tenant admins through
  durable sharing grants without mutating the bundle.

## Recovery Notes

- `409 validation result is stale or failed publish readiness`: re-run
  validation on the latest draft revision and publish again.
- `503 compiled bundle artifact persistence failed`: verify
  `FILESYSTEM_STORAGE_ROOT` or the configured storage provider, then retry
  publish. No version bundle is committed when artifact persistence fails.
- `403 only platform-scoped versions can be shared`: sharing grants are limited
  to platform-scoped published assets.

## Evidence

Validation date: `2026-04-23`

- Full repo check: `./scripts/check.sh`
- Result: `153 passed`
- Coverage: `90.53%`
- Targeted workflow-registry slice:
  `uv run pytest --no-cov tests/unit/admin/test_admin_service.py tests/unit/admin/test_validation.py tests/unit/admin/test_workflow_registry_service.py tests/unit/api/test_admin_workflow_routes.py tests/unit/api/test_admin_workflow_ui_routes.py tests/integration/admin/test_publish_compilation.py tests/integration/api/test_admin_workflows_api.py tests/integration/api/test_admin_workflow_ui.py tests/contract/test_workflow_registry_contract.py`

Measured local timings were captured on `2026-04-23` with `FastAPI TestClient`
against a temporary SQLite database and filesystem artifact storage:

- registry list: `7.36 ms`
- draft detail: `7.23 ms`
- draft save: `10.50 ms`
- validation: `8.90 ms`
- publish: `13.76 ms`
- version detail: `6.01 ms`

Validation-message clarity review:

- blocked `latest` skill versions point directly to `roles[].skill_bindings[].skill_version`
- quorum failures point directly to `join_policies[].quorum_count`
- named-role approval failures point directly to
  `approval_gates[].approver_role_code`
- missing published subworkflow refs point directly to
  `subworkflow_refs[].workflow_version_ref`

UI verification evidence:

- workflow registry, editor, and version-detail browser behavior is covered by
  integration tests and React migration evidence
- browser-friendly local QA login is covered by
  `tests/integration/api/test_local_browser_login.py`
- no separate manual browser-only spot-check was rerun after the final test pass

Security review outcomes:

- platform workflows still require `platform_admin`
- tenant admins cannot publish or browse platform assets without visibility
- sharing grants require `platform_admin`
- validation and publish paths reject secret-like and delegated-credential-like
  refs in authored workflow metadata
