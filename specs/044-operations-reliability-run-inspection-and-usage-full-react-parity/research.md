# Research: Operations, Reliability, Run Inspection, And Usage Full React Parity

## Decision 1: Old Operations Console Routes Redirect To React

**Decision**: Convert `/admin/operations` browser rendering to an authenticated
redirect to `/admin/app/operations`, preserving safe `tenant_id`, filters, and
saved-filter intent.

**Rationale**: Spec 029 already provides the React operations workbench, and
the remaining template is a browser shell, not the source of operational
truth.

**Alternatives Considered**: Keep the template until Spec 047. Rejected because
Spec 044 specifically owns operations Jinja removal and React parity evidence.

## Decision 2: Reliability Browser Routes Map Into React Operations

**Decision**: Convert `/admin/reliability/ui/`,
`/admin/reliability/ui/breakers`, and `/admin/reliability/ui/dead-letters` to
React operations redirects with `panel=reliability`, `panel=breakers`, or
`panel=dead-letters` style query context.

**Rationale**: Reliability controls are part of operations triage and are
already represented in the React workbench envelope.

**Alternatives Considered**: Build a separate React reliability route. Rejected
as unnecessary unless a later product spec requires it.

## Decision 3: Run Inspection Routes Map To React Run Debug

**Decision**: Convert `/admin/runs`, `/admin/runs/{run_id}`,
`/admin/runs/{run_id}/replay`, and lineage-style browser URLs to React
operations run-debug routes or query-state panels.

**Rationale**: Run inspection carries sensitive runtime evidence. React must
consume safe summaries from backend contracts and never render raw prompts,
completions, memory, tool payloads, or stack traces.

**Alternatives Considered**: Retain old run templates as read-only fallbacks.
Rejected because deletion-grade parity requires old browser URLs to prove safe
redirect behavior.

## Decision 4: Usage Dashboard And Export Detail Routes Map To React Usage

**Decision**: Convert `/admin/usage` and `/admin/usage/exports/{export_id}` to
React usage routes, preserving safe filters, tenant id, and export id.

**Rationale**: Spec 035 already added React usage dashboards and export detail.
The old templates are redundant after route coverage and export metadata tests
pass.

**Alternatives Considered**: Inline CSV/export rows into React for detail. Rejected
because export detail must stay metadata-only and artifact-reference based.

## Decision 5: Safe Problems For Unmappable Or Unauthorized Links

**Decision**: Invalid UUIDs, unsafe query parameters, unauthorized ids, and
unmappable old browser URLs return non-Jinja safe problem responses or safe
denials.

**Rationale**: Redirects must not reveal whether an incident, run, export,
dead-letter, breaker, or tenant-private label exists.

**Alternatives Considered**: Redirect all failures to a generic React page.
Rejected because unauthenticated or invalid route data can leak intent and
confuse audit review.
