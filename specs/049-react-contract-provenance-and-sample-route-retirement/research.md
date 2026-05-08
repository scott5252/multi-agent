# Research: React Contract Provenance And Sample Route Retirement

## Decision: Use Shared Backend-Owned Provenance Metadata

**Rationale**: Existing React admin contracts are generated from Pydantic schemas and consumed by React. Adding shared provenance and empty-state models to the backend schema layer keeps data source semantics outside browser-only logic and gives later domain specs a reusable contract.

**Alternatives considered**:

- Per-page ad hoc metadata: rejected because later specs would implement inconsistent empty-state and source semantics.
- Frontend-only classification: rejected because it would move trust and data-source decisions into the browser.

## Decision: Retire Production Patterns Route Instead Of Replacing It With Frontend Fixtures

**Rationale**: `/admin/app/patterns` returns intentionally fake records, fake revisions, fake audit references, fake artifact references, and sample mutation outcomes. The production route should be absent, denied, or development-gated so it cannot satisfy production validation with sample data.

**Alternatives considered**:

- Leave the route but hide navigation: rejected because direct links and generated contracts would still expose sample data.
- Convert sample data to a backend repository: rejected because the route exists only as a shared component demonstration, not a durable product feature.

## Decision: Keep Test Fixtures In Test-Only Paths

**Rationale**: Shared component tests still need deterministic table/form fixtures. Test fixtures under `tests/`, `frontend/admin/src/test`, and component test files are allowed by the live-data policy and should not be deleted just because they contain historical QA markers.

**Alternatives considered**:

- Delete all pattern fixtures: rejected because it would weaken shared component coverage.
- Move fixtures into production components with a flag: rejected because production bundles must not import fixture data.

## Decision: Generate Action Defaults From Backend Metadata Or Client Runtime Helpers

**Rationale**: Current production components contain fixed `qa0xx` revision and idempotency strings. Revision values should come from backend action metadata when they represent server state; idempotency keys may be generated at action time by a shared client helper when the backend only needs replay protection and the value is not a domain identifier.

**Alternatives considered**:

- Keep deterministic QA strings until later domain specs: rejected because Spec 049 specifically sets the shared production rule and scanner guardrail.
- Require backend routes to return every idempotency key: rejected because idempotency keys are per-attempt client request metadata in several flows and can safely be browser-generated when redaction-safe.

## Decision: Validate Empty And Seeded States On Bootstrap/Migration Surfaces

**Rationale**: This spec establishes contract conventions and route retirement rather than replacing every domain builder. The strongest bounded validation is to exercise admin bootstrap/navigation, migration live-data inventory, and retired sample route behavior in empty and seeded QA databases.

**Alternatives considered**:

- Validate every domain route now: rejected as scope for Specs 050 through 057.
- Validate only source scanners: rejected because the browser and route behavior must also prove sample data is not reachable.
