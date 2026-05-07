# Data Model: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## Skill Lifecycle Dashboard Envelope

- `active_scope`: backend-authorized scope label, tenant id, and scope type.
- `sections`: ordered publish, discover, installations, credentials, readiness, binding, diagnostics, and audit navigation metadata.
- `setup_summary`: bounded safety and readiness summary text.
- `platform_publication`: package publication workspace for platform admins only.
- `tenant_discovery`: available package versions authorized for the active tenant.
- `installations`: tenant-scoped installation summaries.
- `skill_execution_diagnostics`: safe diagnostic summaries and explicit refresh actions.
- `binding_preview`: backend-owned eligibility preview.
- `audit_timeline`: bounded safe audit records.
- `legacy_routes`: old skill route mappings and retirement evidence.
- Validation: no section, action, or link may be emitted unless authorized for the active principal.

## Skill Package Summary

- `package_slug`: safe package slug.
- `display_name`: safe label.
- `description`: safe summary.
- `lifecycle_state`: draft, candidate, published, quarantined, withdrawn, unavailable.
- `latest_version`: latest safe version summary.
- `candidate`: optional safe candidate metadata.
- `tenant_grants`: bounded tenant availability summaries for platform admins.
- `actions`: authorized create, candidate, validate, publish, grant, quarantine, and withdraw action metadata.
- Validation: platform-only package mutation actions are never emitted to tenant-only principals.

## Manifest Candidate

- `candidate_id`: safe candidate id.
- `package_slug`: package slug.
- `source`: upload or paste; upload wins when both are present.
- `candidate_revision`: stale conflict token.
- `safe_summary`: manifest-derived safe package metadata.
- `manifest_digest`: non-reversible digest.
- `artifact_reference`: optional artifact reference for reviewer-safe evidence.
- `validation_findings`: safe finding list.
- `publish_blockers`: bounded blocker summaries.
- `audit_reference`: safe audit id.
- Validation: raw manifest text is never returned after submit.

## Skill Package Version Detail

- `package_version_id`: stable safe id.
- `package_slug`: safe package slug.
- `semantic_version`: exact version.
- `manifest_digest`: non-reversible digest.
- `artifact_digest`: non-reversible artifact digest.
- `lifecycle_state`: published, superseded, quarantined, withdrawn, runtime_blocked.
- `readiness`: validation, smoke, credential, compatibility, policy, and grant status.
- `tenant_grants`: authorized tenant grant summaries.
- `audit_references`: bounded audit ids.
- Validation: version detail never contains raw manifests, artifact bytes, credentials, or connector payloads.

## Tenant Grant Summary

- `tenant_id`: authorized tenant id.
- `tenant_label`: safe tenant label only when authorized.
- `grant_enabled`: boolean availability state.
- `revision`: stale conflict token.
- `policy_summary`: safe availability and runtime blocking summary.
- `audit_reference`: safe audit id.
- Validation: cross-tenant grant visibility fails closed.

## Tenant Skill Installation

- `installation_id`: stable safe id.
- `tenant_id`: owning tenant id.
- `package_slug`: safe package slug.
- `semantic_version`: exact installed version.
- `installation_revision`: stale conflict token.
- `credential_references`: safe credential reference summaries.
- `readiness_state`: ready, blocked, degraded, unavailable, stale.
- `smoke_tests`: bounded smoke-test history.
- `connector_readiness`: safe connector readiness summaries.
- `binding_eligibility`: allowed, denied, missing requirements, unavailable.
- `audit_timeline`: bounded safe audit records.
- Validation: tenant principals can see only their tenant's installations.

## Credential Reference Option

- `reference_id`: safe reference id.
- `label`: safe display label.
- `credential_kind`: secret reference or delegated credential.
- `fingerprint`: non-reversible fingerprint when available.
- `status`: ready, missing, invalid, denied, unavailable.
- `remediation`: safe next step.
- Validation: never includes resolved values, authorization headers, provider tokens, connection strings, or local paths.

## Smoke Test Record

- `record_id`: safe id.
- `status`: queued, running, passed, failed, skipped, timed_out, blocked.
- `connector`: safe connector label.
- `started_at` / `completed_at`: bounded timestamps when available.
- `artifact_reference`: optional artifact reference.
- `safe_summary`: redacted result summary.
- `audit_reference`: safe audit id.
- Validation: raw transcripts and connector request/response payloads are not rendered.

## Skill Execution Diagnostic Result

- `diagnostic_id`: safe id.
- `tenant_scope`: authorized tenant/platform summary.
- `tool_name`: allowlisted tool label.
- `policy_decision`: allowed, denied, blocked, unavailable.
- `credential_status`: safe credential readiness.
- `outbound_status`: safe outbound policy status.
- `side_effect_status`: read-only or blocked summary.
- `safe_output_summary`: normalized safe result summary.
- `audit_reference`: safe audit id.
- Validation: diagnostics are explicit mocked-safe actions in local/CI.

## Legacy Skill Route Mapping

- `legacy_path`: old browser path pattern.
- `react_path`: stable React destination when safe.
- `preserved_params`: safe path/query keys.
- `compatibility_status`: redirected, converted, gone, retained_with_blocker, outside_scope.
- `authorization_behavior`: authenticate first, deny safe, unavailable safe, or redirect safe.
- `evidence`: route tests, scanner output, docs, QA, and reviewer notes.

## Skill Retirement Evidence Record

- `surface`: template, route, helper, static asset, docs link, or form action.
- `owner`: skill_registry, skill_execution, shared shell, or later-spec domain.
- `outcome`: deleted, redirected, converted, retained_with_blocker, outside_scope.
- `evidence_paths`: route test, scanner, docs, QA, Playwright, or PR notes.
- `rollback`: restoration scope and guardrail.
