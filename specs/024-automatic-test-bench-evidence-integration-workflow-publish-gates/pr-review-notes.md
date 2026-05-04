# PR Review Notes: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Scope

- Adds repository-backed required-suite evidence summaries for workflow draft validation and publish gates.
- Adds latest-run lookup support for suite, tenant, target type, target id, and target version matching.
- Blocks validation and publication when required suites are missing, stale, failing, unavailable, archived, cross-tenant, platform-scoped, or targeted at another workflow revision.
- Ignores manual workflow document `latest_result_status` fields for publish readiness.
- Renders safe required-test evidence counts and item summaries in the admin publish gate UI.
- Pins safe required-test evidence snapshots into publish gate summaries and published version metadata.

## Security And Privacy

- Tenant-scoped suites and runs remain the only accepted evidence source for tenant workflow drafts.
- Cross-tenant suite ids fail closed and render safe unavailable diagnostics.
- Denied evidence does not disclose suite names, fixture values, transcripts, target names, or artifact references.
- Platform-scoped workflow drafts with required tenant test evidence fail closed until a safe platform target policy exists.
- Published evidence pins include safe ids, target metadata, status, and freshness fields only.

## Durability

- Evidence is derived from persisted Agent Test Suite and Agent Test Run records.
- Publish gates re-query required evidence during validation, gate evaluation, and final publication.
- Validation freshness now treats superseded or failing validation results as not publish-ready.
- Current target version is the active workflow draft revision id.

## Test Evidence

Review:

- `tests/unit/admin/test_publish_gate.py`
- `tests/unit/admin/test_workflow_builder_references.py`
- `tests/unit/admin/test_workflow_registry_service.py`
- `tests/integration/api/test_admin_workflow_ui.py`

Run:

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_publish_gate.py \
  tests/unit/admin/test_workflow_builder_references.py \
  tests/unit/admin/test_workflow_registry_service.py \
  tests/integration/api/test_admin_workflow_ui.py
```

## Residual Limits

- QA024 covers workflow draft required evidence first; published workflow and subworkflow target policies remain governed by the existing test bench target model.
- Browser QA validates the rendered publish gate evidence summary and login flow; deep suite creation remains documented in the manual QA guide.
- The implementation stores safe summaries and pins, not raw run transcripts or fixture bodies.
