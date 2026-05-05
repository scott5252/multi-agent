# Research: React Usage And Cost Analytics

## Usage Source Of Truth

**Decision**: Reuse `UsageAnalyticsService`, `UsageRepository`, existing usage
models, pricing versions, reconciliation records, export requests, and
`store_usage_csv_export` for all persisted usage behavior.

**Rationale**: Spec 016 already defines normalized token/cost semantics,
tenant filtering, safe CSV export metadata, pricing calculations, and
availability statuses. The React feature should improve administrator
experience without creating parallel accounting rules.

**Alternatives considered**: Querying usage tables directly from the React
router would duplicate tenant filters and export behavior. Creating new
rollup tables for this spec would widen scope and require migrations that are
not needed for the bounded dashboard.

## React Projection Layer

**Decision**: Add a backend-owned `admin.usage.react_usage` projection layer
that converts usage summaries and events into cards, trend points, rollup rows,
filter metadata, drilldown rows, export summaries, and safe state messages.

**Rationale**: The browser should not own confidence calculations, tenant
visibility, grouping eligibility, cost formatting, or redaction. A projection
layer lets the existing usage service remain authoritative while giving React
the shape needed for non-technical admin workflows.

**Alternatives considered**: Returning the existing Spec 016 API response
directly would leave the browser to infer too much domain meaning. Adding
business logic in React would make Auth0/local-principal and tenant behavior
harder to validate.

## Grouping And Attribution

**Decision**: Support backend-owned React grouping dimensions for day, tenant,
provider, model, workflow, agent, sub-agent, prompt, execution mode,
principal, graph node, gateway operation, physical attempt, and governed tool
where authorized. Existing `UsageFilters.group_by` remains the persisted
filter source, and extra React-only attribution labels are projected from safe
event metadata when available.

**Rationale**: Current Spec 016 grouping covers core usage dimensions. Specs
020, 021, and 025 add graph/runtime, governed tool, gateway operation, and
physical-attempt evidence mostly as safe metadata. React needs to present
those as user-facing dimensions without exposing raw run payloads.

**Alternatives considered**: Extending the base `UsageGroupBy` literal before
React requirements are proven risks coupling older usage APIs to UI-only
attribution. Rendering unsupported dimensions as raw IDs would violate the
redaction requirements.

## Time Range And Trend Rendering

**Decision**: Default to the last 7 days with daily buckets, bounded trend
points, and backend-formatted values. Render the chart as an accessible
React/SVG component using existing dependencies rather than adding a charting
library.

**Rationale**: The dashboard trend is a compact operational visualization, not
a general analytics workbench. A small SVG component keeps bundle churn low
and is easy to test with deterministic fixture data.

**Alternatives considered**: Adding Recharts or another chart library would
increase dependency and bundle surface for one bounded chart. A table-only
trend would be less usable for non-technical administrators.

## Filter Metadata

**Decision**: Filters and options are returned from the backend with selected
defaults, allowed values, disabled reasons, and scope labels.

**Rationale**: Tenant and platform visibility must fail closed, and
administrators should not see options they cannot safely use. Backend-owned
metadata also makes Playwright validation deterministic.

**Alternatives considered**: Client-side filter discovery from result rows
would hide empty-but-valid states and could accidentally expose unauthorized
tenant/provider labels.

## Export Flow

**Decision**: React export creation posts the active safe filter snapshot,
returns status, row count, safe artifact reference, requester/scope summary,
and audit reference, then supports a detail endpoint for delayed artifacts.

**Rationale**: Export is the only mutation in scope. Persisted export records
and artifact metadata satisfy auditability without exposing CSV contents in
the browser or QA evidence.

**Alternatives considered**: Immediate browser-side CSV generation would
bypass existing storage and audit controls. Showing raw artifact paths would
leak local filesystem or storage internals.

## Authorization And QA

**Decision**: Protect all React usage routes through the existing admin policy
surface, test Auth0-shaped principals with backend route tests, and test
local-principal browser flows with Playwright.

**Rationale**: The roadmap requires dual-auth validation for every React
admin feature, and usage/cost data is tenant-sensitive operational evidence.

**Alternatives considered**: Local-principal-only tests would miss production
claim mapping. Auth0-only mocks would make local QA brittle.
