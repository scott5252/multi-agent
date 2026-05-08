# PR Notes: Live-Only UI Decommission Gate

## Reviewer Focus

- Verify production admin UI routes are classified as live data, computed
  metadata, empty, denied, unavailable, redirect-only, or out of scope.
- Confirm fixed QA markers and fixture-like IDs are blocking only in
  production-reachable source, built assets, and route responses.
- Confirm tests, frontend test data, QA seed helpers, validation manifests, and
  historical specs remain allowed only through explicit policy.
- Confirm route probes cover both fresh empty-state and seeded live-data QA
  behavior with platform and tenant-shaped principals.

## Generated Contract Notes

- `frontend/admin/src/api/generated/reactAdminApi.ts` already contains the
  migration hardening and live-data inventory schemas.
- Spec 058 may regenerate this file if backend schema fields or route query
  options change.

## Documentation Impact

- Feature-level QA docs are required for QA058.
- Shared `README.md` and `docs/quickstart.md` only need updates if Spec 058
  introduces a reusable command beyond the spec validation manifest.
- Reviewed shared `README.md` and `docs/quickstart.md`; no shared update is
  required because QA058 adds only spec-scoped gate commands and artifacts.

## Rollback Notes

- Rollback should narrow a false positive or restore a deleted surface only
  under review.
- Do not reintroduce a production demo-data flag or backend-generated fixture
  rows as rollback.
