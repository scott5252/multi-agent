# Data Model: Live-Only UI Decommission Gate

## Route Live-Data Classification

Represents the final policy category for one production admin UI route.

**Fields**:

- `target_id`: Stable route target identifier.
- `method`: Supported request method.
- `path`: Admin UI route or JSON path.
- `principal`: Required platform or tenant principal shape.
- `tenant_scope`: Platform, tenant, mixed, or redirect-only scope.
- `classification`: Live data, computed metadata, truthful empty, denied,
  unavailable, redirect-only, or out of scope.
- `replacement_spec`: Spec that owns the live-data replacement, when relevant.
- `seed_requirement`: Setup required for seeded validation, or `none`.
- `empty_state_required`: Whether the route must be validated in a fresh QA
  database.
- `seeded_state_required`: Whether the route must be validated with persisted
  representative data.

**Validation Rules**:

- Production admin UI targets must live under `/admin/app`.
- Routes with seeded validation must name a seed requirement or an existing
  persisted source.
- Computed metadata classifications must name the derivation source.

## Live-Only Gate Finding

Represents a scanner, built-asset, import, or response-probe finding.

**Fields**:

- `finding_id`: Stable identifier for report and tests.
- `severity`: Blocking, warning, or info.
- `status`: New regression, mapped legacy, allowed computed metadata, or
  test-only.
- `marker_kind`: QA marker, fake audit reference, fake artifact reference, fake
  run ID, fake link token, fixture collection, fake mutation success,
  hardcoded domain entity, or test fixture import.
- `source_path`: Repository-relative source, asset, route, or report path.
- `route_path`: Affected route when known.
- `owner_spec`: Spec that introduced or owns the surface.
- `replacement_spec`: Spec expected to remove or justify the marker.
- `durable_source`: Live source, computed source, or test-only boundary.
- `reachability`: Production source, production response, generated contract,
  built asset, computed metadata, or test-only.
- `safe_excerpt`: Redaction-safe evidence snippet.

**Validation Rules**:

- New regressions are always blocking.
- Source paths and evidence references must be repository-relative.
- Safe excerpts must not contain raw secrets, payloads, local paths, stack
  traces, or unauthorized tenant labels.

## Route Response Probe

Represents one authenticated API/browser-adjacent route validation request.

**Fields**:

- `probe_id`: Stable probe identifier.
- `state`: Empty QA database or seeded QA database.
- `principal`: Platform or tenant-shaped principal used by the probe.
- `request`: Method, path, query, and safe body summary.
- `expected_status`: Allowed HTTP or application status.
- `assertions`: Live-only, empty-state, redaction, tenant-isolation, and
  provenance checks.
- `evidence_reference`: Relative QA artifact or test reference.

**Validation Rules**:

- Probes must fail closed when authorization is missing or ambiguous.
- Tenant probes must not include other-tenant labels in response evidence.
- Empty-state probes must assert no invented domain rows.

## Seed Requirement

Represents data needed for a route to prove live seeded behavior.

**Fields**:

- `surface`: Admin UI surface or route family.
- `required_records`: Persisted records or service state required.
- `setup_source`: QA seed script, repository call, public/admin API, or
  documented computed source.
- `empty_state`: Expected state when the records are absent.
- `verification`: API or database check that proves the data was read.

**Validation Rules**:

- Seed requirements must avoid real provider, Telegram, credential, connector,
  or outbound calls unless explicitly mocked or approved.
- Seeded data must be tenant-scoped where the route is tenant-scoped.

## Decommission Decision

Represents the disposition of an obsolete mock/demo surface.

**Fields**:

- `surface_id`: Stable surface identifier.
- `source_path`: Repository-relative source path or asset group.
- `decision`: Deleted, disconnected, retained test-only, allowed computed
  metadata, or blocked.
- `production_imports_remaining`: Count or boolean summary.
- `policy_rationale`: Why the decision satisfies live-only policy.
- `rollback_reference`: Reviewer-facing rollback note.

**Validation Rules**:

- Deleted/disconnected decisions require no production import references.
- Retained test-only decisions require a test/QA/docs/historical boundary.

## Rollback Record

Represents safe reviewer guidance for a decommission decision.

**Fields**:

- `rollback_id`: Stable rollback identifier.
- `surface_id`: Related decommission surface.
- `trigger`: False positive, missing seed, compatibility break, or route
  regression.
- `steps`: Safe recovery steps.
- `verification_steps`: Commands or checks after rollback.
- `owner`: Review owner or domain surface.

**Validation Rules**:

- Rollback steps must not reintroduce production fixture data without an
  explicit review decision.
- Verification steps must include scanner and route response validation.
