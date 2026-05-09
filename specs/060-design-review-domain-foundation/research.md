# Research: Design Review Domain Foundation

## Decision: Add A Dedicated Design Review Domain

**Rationale**: The scenario has first-class lifecycle concepts that are not
owned by workflow registry, runtime orchestration, or test bench alone:
sessions, revisions, rounds, assignments, verdicts, quorum decisions, manual
decisions, and handoffs. A dedicated admin domain keeps the scenario additive
while allowing later specs to integrate with runtime and model gateway.

**Alternatives considered**: Store everything as workflow run metadata; rejected
because design revisions, manual decisions, and handoffs need their own durable
tenant-scoped lifecycle and route contracts.

## Decision: Keep Spec 060 Backend-Only

**Rationale**: The roadmap sequences backend domain, model executor,
coordinator, Admin workspace, and templates across Specs 060-064. Landing the
domain first gives later specs stable contracts without introducing fake UI rows
or premature model calls.

**Alternatives considered**: Build UI and coordinator in the same spec; rejected
because it expands blast radius and risks hidden fixture behavior.

## Decision: Store Safe Metadata, References, And Digests Only

**Rationale**: Design packets and reviewer feedback can contain product-sensitive
content. PostgreSQL should hold transactional metadata, safe summaries,
artifact references, digests, and provenance. Raw artifact bodies remain in the
configured storage layer and are not returned by this spec's APIs.

**Alternatives considered**: Store structured reviewer payloads directly in
design-review tables; rejected because it increases redaction and retention
risk before model output contracts are finalized.

## Decision: Use Tenant-Scoped Idempotency Keys

**Rationale**: Create-session, evidence recording, manual decisions, and handoff
creation are retry-prone and must not duplicate durable records. Tenant-scoped
idempotency keys allow safe retries without cross-tenant collisions.

**Alternatives considered**: Rely on client-side retry avoidance; rejected
because process and network failures must be recoverable.

## Decision: Manual Decisions Are Append-Only Evidence

**Rationale**: Human approval is durable state. Manual decisions must record the
actor, decision type, safe rationale, accepted-risk marker, and idempotency key
without silently rewriting prior verdicts or quorum decisions.

**Alternatives considered**: Store only the latest manual decision on the
session; rejected because it would lose audit and replay context.

## Decision: Use `/admin/design-reviews` JSON Routes

**Rationale**: Spec 060 exposes backend JSON contracts before a browser
workspace exists. `/admin/design-reviews` follows existing admin API patterns
and leaves `/admin/app/design-reviews` available for Spec 063 UI routes.

**Alternatives considered**: Add `/admin/app/design-reviews.json` now; rejected
because the UI page envelope and browser interactions are intentionally deferred.

## Decision: Deterministic Local QA Only

**Rationale**: The foundation can be fully validated with local-principal auth,
seeded tenants, database rows, and service/repository/API tests. No real Auth0,
provider, Telegram, connector, credential, or outbound call is needed.

**Alternatives considered**: Probe real model providers to validate assignment
metadata; rejected because model-backed execution belongs to Spec 061.
