# Data Model: Live Data Inventory And Mock Guardrails

No new PostgreSQL tables or Alembic migration are required. The feature uses computed Pydantic contracts and QA artifact files.

## LiveDataInventoryDashboard

- `page_id`: stable page identifier for migration evidence.
- `generated_at`: UTC timestamp of the scan projection.
- `summary`: `LiveDataScanSummary`.
- `findings`: tuple of `LiveDataInventoryFinding`.
- `allowlist`: tuple of `LiveDataAllowlistEntry`.
- `route_targets`: tuple of `LiveDataRouteTarget`.
- `evidence`: tuple of `LiveDataInventoryEvidence`.
- `states`: tuple of safe state summaries for denied/unavailable/empty cases.

Validation rules:

- All strings pass migration hardening safe-text validation.
- Finding and allowlist counts must match the summary.
- Prohibited unmapped findings are not allowed in CI mode.

## LiveDataInventoryFinding

- `finding_id`: stable identifier.
- `severity`: `blocking`, `warning`, or `info`.
- `status`: `mapped_legacy`, `allowed_computed_metadata`, `new_regression`, or `test_only`.
- `marker_kind`: taxonomy value such as `qa_marker`, `fake_audit_reference`, `fake_artifact_reference`, `fake_run_id`, `fake_link_token`, `fixture_collection`, `fake_mutation_success`, `hardcoded_domain_entity`, or `test_fixture_import`.
- `source_path`: repository-relative source path or asset path.
- `route_path`: route reached by the finding when known.
- `owner_spec`: source React/Jinja migration spec that introduced the surface when known.
- `replacement_spec`: planned cleanup spec from 049 through 058.
- `durable_source`: expected repository, service, or computed metadata source.
- `reachability`: `production_response`, `production_source`, `generated_contract`, `built_asset`, `computed_metadata`, or `test_only`.
- `safe_excerpt`: short redaction-safe excerpt or marker summary.

Validation rules:

- `source_path` must be repository-relative and must not include local absolute paths.
- `safe_excerpt` must not include raw secrets, prompts, completions, private messages, raw payloads, stack traces, or full external identifiers.
- `new_regression` findings are blocking in CI mode.

## LiveDataAllowlistEntry

- `allowlist_id`: stable identifier.
- `scope`: route, source path, generated contract, or built asset scope.
- `marker_kind`: marker taxonomy covered by the allowlist.
- `reason`: computed metadata reason.
- `derivation_source`: code/config/route/asset/scanner source.
- `owner`: migration or platform area owner.
- `expires_with_spec`: replacement or decommission spec when temporary.

Validation rules:

- Allowlist entries cannot target broad repository roots.
- Each entry must name a derivation source and reason.

## LiveDataRouteTarget

- `target_id`: stable route target identifier.
- `method`: HTTP method.
- `path`: production `/admin/app` JSON endpoint.
- `principal`: local-principal role used by route scans.
- `tenant_scope`: platform, tenant, auditor, or mixed.
- `empty_state_required`: whether an empty QA database scan is mandatory.
- `seeded_state_required`: whether a seeded QA database scan is mandatory.
- `computed_metadata_only`: whether domain seeded data is not expected.
- `replacement_spec`: cleanup spec that owns live-data migration if deterministic data is found.

Validation rules:

- Targets must avoid unsafe mutations unless a safe idempotent mutation is explicitly part of a later spec.
- Tenant targets must include tenant query parameters in QA scans.

## LiveDataScanSummary

- `total_findings`
- `blocking_findings`
- `mapped_legacy_findings`
- `allowed_computed_metadata`
- `test_only_markers`
- `route_targets`
- `empty_state_scans`
- `seeded_state_scans`
- `ci_status`: pass, warning, or fail.
- `next_step`

Validation rules:

- `ci_status` is fail when a new unallowlisted production finding exists.
- Empty and seeded scan counts cannot exceed target counts.

## LiveDataInventoryEvidence

- `evidence_id`
- `evidence_type`: scanner, route_response_scan, contract_test, backend_route_test, frontend_test, playwright, qa_doc, reviewer_note, or curl_test.
- `reference`
- `status`

Validation rules:

- References must be redaction-safe and repository-relative or artifact-root relative.
