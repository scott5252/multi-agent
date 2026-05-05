# Research: React Admin Data Contracts And Form Patterns

## Decision 1: Use A Generic Admin Page Envelope

**Decision**: Add a reusable `AdminPageEnvelope` for React admin pages, with typed page metadata, scope, state descriptors, actions, filters, pagination, sorting, evidence, and a generic data payload.

**Rationale**: Future admin pages need consistent loading, empty, denied, partial-data, and action surfaces. A generic envelope lets each domain provide safe data without re-solving the same shell and page metadata shape.

**Alternatives considered**:

- Domain-specific response wrappers for every page. Rejected because future specs would duplicate pagination, action, error, and evidence fields.
- Browser-composed envelopes. Rejected because the browser must not infer authorized scope or actions.

## Decision 2: Use Safe Problem Details

**Decision**: Use RFC-style problem details with safe reason categories, status, title, detail, field errors, retry hints, and audit reference ids.

**Rationale**: React can render clear validation and recovery messages without seeing raw exceptions, stack traces, provider responses, prompts, memory, tool payloads, or private messages.

**Alternatives considered**:

- Return raw FastAPI validation responses. Rejected because they may expose implementation detail and do not map cleanly to shared admin toasts.
- Use plain strings. Rejected because field validation and recovery metadata would be ambiguous.

## Decision 3: Keep Mutations Backend-Owned

**Decision**: Define mutation result contracts for accepted, validation-error, stale-conflict, replayed, confirmation-required, dependency-unavailable, and unexpected-error outcomes, but keep action acceptance in backend services.

**Rationale**: React needs consistent feedback and dirty-state handling, but domain rules, action tokens, revision tokens, idempotency, audit persistence, and side-effect decisions belong on the backend.

**Alternatives considered**:

- Implement client-side domain validation. Rejected because it duplicates policy and can diverge from backend guardrails.
- Skip mutation examples until domain pages migrate. Rejected because future pages need a proven form pattern first.

## Decision 4: Use Backend-Owned Filter Profiles

**Decision**: Define allowed filter criteria, operators, values, chips, saved-filter summaries, sortable fields, and bounded pagination in backend contracts.

**Rationale**: Filters and sorting are a frequent source of tenant leaks if the browser can invent criteria or raw identifiers.

**Alternatives considered**:

- Browser-only filter metadata. Rejected because it cannot prove tenant scope and authorization.
- Free-form query strings. Rejected because non-technical admins need guided options and safe chips.

## Decision 5: Use Safe Export Snapshots

**Decision**: Return export status snapshots with safe progress labels, artifact reference ids, expiry metadata, and audit references.

**Rationale**: Real exports can be large and sensitive. React should show progress and safe download references, not raw local paths or exported content.

**Alternatives considered**:

- Inline export content in React JSON. Rejected because it risks raw data exposure and oversized responses.
- Real domain exports in Spec 028. Rejected because this feature should remain a reusable pattern and avoid major domain migration.

## Decision 6: Add A Harmless Patterns Sample Page

**Decision**: Implement `/admin/app/patterns` as a minimal sample page that demonstrates envelopes, filters, table state, details, validation, stale conflict, replay, confirmation, export status, and safe toasts.

**Rationale**: Future specs need an executable example and Playwright needs a harmless browser flow.

**Alternatives considered**:

- Document-only pattern. Rejected because generated types and frontend behavior need executable coverage.
- Migrate a real domain page now. Rejected because Spec 028 should not change domain workflows.
