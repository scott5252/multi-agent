# Research: Usage React Live Data

## Decisions

### Source Of Truth

**Decision**: Use `UsageAnalyticsService.summarize_usage()` and
`UsageRepository` over persisted usage tables as the React source of truth.

**Rationale**: The existing service already enforces usage access scope,
filtering, event normalization, rollup computation from live events, and export
creation. Reusing it avoids a second fixture-like analytics path.

**Alternatives Considered**:

- Keep deterministic React usage events and label them as samples. Rejected
  because production React routes must not render fixed domain data.
- Build analytics entirely in the frontend. Rejected because tenant scoping,
  redaction, confidence semantics, and export mutation decisions belong to the
  backend.

### Rollups And Trend Points

**Decision**: Compute dashboard totals, rollups, and trend points from live
usage events on read for the requested scope and range; treat persisted rollup
rows as optional acceleration only when implementation can prove matching scope
and filters.

**Rationale**: The clarification answers make events the correctness source and
prevent missing persisted rollup rows from producing false empty dashboards.

**Alternatives Considered**:

- Require precomputed rollups before rendering. Rejected because a fresh but
  valid usage database can contain events before a rollup job runs.

### Export Persistence

**Decision**: Route React export creation through
`UsageAnalyticsService.create_csv_export()` with the active usage access scope,
filters, principal, and configured storage provider; expose artifact references
only from completed persisted export metadata.

**Rationale**: Existing export service creates request rows, scopes data, writes
CSV bytes through storage, records row count/checksum/size, and marks failed or
denied states.

**Alternatives Considered**:

- Return a fixed artifact id or browser-only success state. Rejected because the
  spec requires durable, auditable evidence.

### Missing Pricing And Confidence

**Decision**: Map usage and cost statuses into React confidence states:
confirmed, estimated, partial, and unavailable. Missing or unavailable pricing
must show explicit unavailable/missing copy and zero or absent cost values
without inventing amounts.

**Rationale**: The existing usage event model stores usage status, cost status,
estimated cost micros, and pricing references. The UI can explain confidence
without exposing sensitive payloads.

**Alternatives Considered**:

- Hide rows with missing pricing. Rejected because operators need to see
  incomplete evidence and reconciliation work.

### Attribution

**Decision**: Render safe labels from usage event fields and sanitized
`safe_attribution` metadata first. Add authorized live metadata lookup only when
it remains bounded and redaction-safe.

**Rationale**: Usage events already carry provider, model, workflow, prompt,
profile, run, step, agent, and trace references. Safe event fields preserve
explainability without needing raw runtime payloads.

**Alternatives Considered**:

- Join every referenced runtime/provider/skill table on every dashboard load.
  Rejected for scope and performance risk; richer lookup can be added behind
  bounded helpers when needed.

### Empty And Denied States

**Decision**: Return truthful empty states when scoped live queries have no
events or exports, and fail closed for cross-tenant filter/export attempts.

**Rationale**: Empty and denied states are first-class outcomes in the existing
React common-state pattern and are required to prevent misleading qa035-style
demo rows.

**Alternatives Considered**:

- Seed default examples for empty tenants. Rejected because production routes
  must not invent usage.

### QA Strategy

**Decision**: qa056 will seed Acme usage, pricing, reconciliation, export, and
safe attribution rows inside the default last-30-days range, leave Globex empty,
exercise a local-principal browser export action, and verify persistence through
API/database evidence.

**Rationale**: This proves both live seeded and empty behavior and demonstrates
that the UI mutation writes durable backend state.
