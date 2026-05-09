# Feature Specification: Design Review Domain Foundation

**Feature Branch**: `codex/060-design-review-domain-foundation`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Add a first-class Design Review domain for the multi-agent platform. The feature must let tenant admins create and inspect durable design review sessions for the Design Reviewer Council scenario. A session starts from a safe design request summary, tracks immutable design revisions, review rounds, reviewer assignments, reviewer verdicts, quorum decisions, manual decisions, and final development handoff references. Records must be tenant-scoped, authorization-aware, redaction-safe, and auditable. Do not execute live model calls in this spec. Do not add the Admin React workspace yet. The API must expose backend-owned JSON contracts for session creation, session detail, round detail, revision metadata, quorum decision metadata, and handoff metadata. Empty and denied states must be truthful."

## Clarifications

### Session 2026-05-08

- Q: What is the boundary between Spec 060 and later scenario specs? -> A: Spec 060 owns durable backend records, JSON contracts, services, repositories, migration, and tests only; model-backed execution, coordinator auto-launch, Admin workspace UI, and reusable template publishing remain deferred to Specs 061-064 (autopilot).
- Q: How should retries be deduplicated for session and evidence writes? -> A: Store tenant-scoped idempotency keys for create-session, round/evidence recording, manual decisions, and handoff creation so retries return or conflict against existing durable records instead of duplicating evidence (autopilot).
- Q: What may be stored for design packets, reviewer feedback, and handoffs? -> A: Persist safe summaries, structured safe metadata, artifact references, digests, usage/provenance, and policy references only; raw prompts, completions, artifacts, provider payloads, secrets, memory contents, private messages, and raw external tool payloads remain out of records and responses (autopilot).
- Q: How should manual decisions behave in this foundation spec? -> A: Manual decisions are append-only auditable records with explicit decision type and safe rationale; they do not silently override blocking reviewer issues and later coordinator specs must interpret them through policy (autopilot).
- Q: Which API surface should be added before the Admin workspace exists? -> A: Add backend-owned admin JSON route families under the existing authenticated admin/API pattern for create, list, detail, revision, round, decision, manual-decision, and handoff metadata; browser UI rendering remains a later spec (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Durable Design Review Sessions (Priority: P1)

A tenant administrator starts a Design Reviewer Council session by submitting a
safe request summary and receives a durable session with the first immutable
revision ready for later review-round orchestration.

**Why this priority**: The rest of the scenario depends on an authoritative,
tenant-scoped session and revision record that survives process, worker, and
request retries.

**Independent Test**: Create a session through the backend contract as an
authorized tenant administrator, then verify the returned session, first
revision, provenance, idempotency behavior, and persisted database state without
triggering model execution or UI workspace behavior.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator and a safe design request summary, **When** they create a design review session, **Then** the system persists a tenant-scoped session, revision 1, request summary, owner principal, quorum policy, workflow bundle reference if supplied, and safe timestamps.
2. **Given** the same tenant, principal, and idempotency key, **When** session creation is retried, **Then** the system returns the existing session rather than creating duplicate sessions or revisions.
3. **Given** an unauthenticated, unauthorized, or cross-tenant caller, **When** they attempt to create a session, **Then** the system fails closed and does not persist or expose another tenant's design review data.

---

### User Story 2 - Inspect Session, Revision, And Round Evidence (Priority: P2)

Authorized platform and tenant operators inspect design review sessions and see
live durable metadata for revisions, rounds, reviewer assignments, verdicts,
quorum decisions, manual decisions, and handoff references without raw prompt,
completion, payload, secret, or private content exposure.

**Why this priority**: Operators need trustworthy backend-owned evidence before
the later coordinator, model executor, and Admin workspace can build on the
domain.

**Independent Test**: Seed or create a session with revision and round evidence,
then fetch list, detail, revision, and round contracts as authorized and
cross-tenant principals to verify safe summaries, artifact references,
truthful empty states, and denied behavior.

**Acceptance Scenarios**:

1. **Given** a tenant with design review sessions, **When** an authorized tenant administrator lists and opens a session, **Then** the response includes only that tenant's safe session, revision, round, decision, manual decision, and handoff metadata.
2. **Given** a session with no rounds or handoff yet, **When** detail is requested, **Then** the response returns a truthful pending or empty state instead of synthesized reviewer rows, quorum outcomes, or handoff data.
3. **Given** a platform administrator, **When** they inspect tenant-scoped design review evidence with explicit tenant context, **Then** the response preserves tenant scoping and safe summaries while omitting raw protected content.

---

### User Story 3 - Record Immutable Review Evidence (Priority: P3)

Internal services can record reviewer assignments, verdicts, quorum decisions,
manual decisions, and final handoff references as immutable or append-only
evidence that later coordinator and Admin features can trust.

**Why this priority**: The production scenario needs durable evidence records
before it can safely add model-backed execution or iterative coordination.

**Independent Test**: Use service and repository tests to record assignments,
verdicts, quorum decisions, manual decisions, and handoff references, then
verify immutability, artifact-reference handling, digest storage, audit-safe
summaries, and duplicate prevention.

**Acceptance Scenarios**:

1. **Given** a design review round, **When** assignments and verdicts are recorded, **Then** each evidence record stores reviewer keys, role keys, prompt/profile references, verdict summaries, scores, issue counts, artifact references, digests, and timestamps without raw protected payloads.
2. **Given** recorded verdicts and a quorum policy, **When** a quorum decision is recorded, **Then** the system stores approval counts, blocking issue counts, next action, policy version, and safe rationale as immutable decision evidence.
3. **Given** a manual decision or approved handoff, **When** it is recorded, **Then** the system appends audit-safe decision or handoff metadata without silently overriding blocking reviewer issues.

### Edge Cases

- Session creation retried with the same idempotency key must not create duplicate sessions, revisions, rounds, manual decisions, or handoffs.
- A caller without the active tenant membership must receive denied or not-found behavior without learning whether another tenant's session exists.
- Empty session, round, verdict, decision, manual decision, and handoff collections must be truthful empty states, not seeded examples.
- Artifact references may be absent while later specs are still wiring storage, but raw artifact bodies, prompts, completions, memory contents, secrets, provider payloads, and external tool payloads must never appear in design review records or route responses.
- Evidence records that represent reviewer outputs, quorum decisions, manual decisions, and handoffs must be append-only or immutable after creation.
- The backend must not launch workflow runs, call model providers, or render an Admin workspace in this spec.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose backend-owned JSON contracts for creating, listing, and retrieving tenant-scoped design review sessions.
- **FR-002**: The system MUST create session records with tenant, owner principal, status, safe request summary, active revision number, quorum policy key, optional workflow bundle reference, idempotency key, and timestamps.
- **FR-003**: The system MUST create revision 1 with immutable safe summary, author role key, optional artifact reference, payload digest, previous revision reference, revision number, and timestamps when a session is created.
- **FR-004**: The system MUST expose session detail with safe revision, round, assignment, verdict, quorum decision, manual decision, and handoff metadata, while representing absent records as truthful empty or pending states.
- **FR-005**: The system MUST expose dedicated backend JSON contracts for revision metadata, round metadata, quorum decision metadata, manual decision metadata, and handoff metadata.
- **FR-006**: The system MUST provide service and repository operations for recording review rounds, reviewer assignments, reviewer verdicts, quorum decisions, manual decisions, and development handoffs without executing live model calls.
- **FR-007**: Reviewer assignments MUST store reviewer key, role key, enabled flag, and prompt/profile/provider reference metadata without requiring live prompt rendering or model execution.
- **FR-008**: Reviewer verdicts MUST store verdict, score, blocking issue count, safe feedback summary, artifact reference, output digest, and usage/provenance metadata without raw prompt or completion content.
- **FR-009**: Quorum decisions MUST store status, approval count, blocking issue count, next action, policy version, safe rationale, and link to the relevant round.
- **FR-010**: Manual decisions MUST be append-only, auditable records with decision type, actor principal, safe rationale, risk acceptance marker where applicable, and idempotency protection.
- **FR-011**: Development handoffs MUST store approved revision reference, safe summary, artifact reference, output digest, and status without raw handoff payloads.
- **FR-012**: All design review records and API responses MUST enforce tenant isolation and fail closed for unauthorized or cross-tenant access.
- **FR-013**: All persisted fields, responses, logs, QA artifacts, and reviewer notes MUST avoid raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, private channel payloads, unauthorized payloads, and raw external tool payloads.
- **FR-014**: The system MUST emit audit-safe events for session creation, evidence recording, manual decisions, handoff recording, denied access attempts where existing patterns support it, and idempotent retry recovery.
- **FR-015**: The feature MUST add migration, unit, repository, contract, integration, documentation, QA, Playwright, and curl regression evidence for the new domain contracts.

### Key Entities

- **Design Review Session**: A tenant-scoped workflow scenario container with owner, status, safe request summary, active revision pointer, quorum policy, optional workflow bundle reference, and idempotency metadata.
- **Design Revision**: An immutable design packet metadata record with revision number, author role, safe summary, artifact reference, digest, and lineage to the previous revision.
- **Design Review Round**: A record linking one session revision to one future runtime workflow run, reviewer counts, quorum target, status, and safe timing metadata.
- **Reviewer Assignment**: A reviewer role assignment for a round, including reviewer key, role key, enabled flag, and prompt/profile/provider reference metadata.
- **Reviewer Verdict**: Immutable reviewer evidence with verdict, score, blocking issue count, safe feedback summary, artifact reference, digest, and provenance metadata.
- **Quorum Decision**: Immutable aggregate decision metadata for a round, including approval counts, blockers, next action, policy version, and safe rationale.
- **Manual Decision**: Append-only operator decision metadata used to revise, retry, approve exception, or cancel without treating chat state or transient UI state as authority.
- **Development Handoff**: Final approved handoff metadata with approved revision, safe summary, artifact reference, digest, and status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized tenant administrator can create a design review session and retrieve its first revision through backend JSON contracts in a deterministic local QA environment.
- **SC-002**: Repeating session creation with the same idempotency key returns the existing durable session and creates zero duplicate sessions or revisions.
- **SC-003**: Cross-tenant and unauthorized access tests prove another tenant's design review sessions, revisions, rounds, decisions, manual decisions, and handoffs are not listed, retrieved, inferred, or mutated.
- **SC-004**: Service and repository tests prove reviewer verdict, quorum decision, manual decision, and handoff evidence is immutable or append-only and stores only safe summaries, digests, provenance, and artifact references.
- **SC-005**: Contract and integration tests cover every new design review route family, including empty, denied, success, idempotent retry, and validation-error states.
- **SC-006**: QA guides, Playwright smoke evidence, curl regression commands, and reviewer notes demonstrate the backend domain without raw prompts, completions, secrets, provider payloads, private messages, memory contents, raw artifacts, or fake UI records.

## Assumptions

- Spec 060 owns durable backend domain foundations only; model-backed role execution, coordinator auto-launch, iterative review loops, Admin workspace UI, and reusable templates are deferred to Specs 061 through 064.
- Local QA uses local-principal authentication, deterministic data setup, and no real provider, Auth0, Telegram, connector, or outbound calls.
- The initial API may accept safe summaries and artifact reference metadata from trusted internal callers or test fixtures; raw artifact bodies remain outside PostgreSQL.
- Existing tenant, authorization, audit, storage, workflow registry, runtime, prompt/profile, and test-bench patterns remain authoritative and are extended additively.
- No commit, staging, push, or pull request is required during the scenario enhancement run.

## Testing Instructions

- Add unit coverage for domain validation, redaction-safe DTO conversion, idempotency, and evidence immutability.
- Add repository coverage for tenant filters, uniqueness constraints, idempotency keys, append-only evidence, and relationship loading.
- Add integration/API coverage for create/list/detail/revision/round/decision/manual-decision/handoff route families with local-principal platform admin, tenant admin, denied, and cross-tenant principals.
- Add docs/QA coverage for `qa060.md`, `qa060_ui.md`, `.env.qa060`, `qa060_user_guide.md`, `pr_notes.md`, Playwright validation, and curl regression.

## PR Review Guidance

- Confirm no source, response, log, screenshot, or QA artifact contains raw prompts, completions, secrets, provider payloads, memory contents, private channel payloads, unauthorized payloads, or raw external tool payloads.
- Confirm all design review tables, repositories, services, schemas, routes, tests, and curl commands enforce explicit tenant scope and fail closed on cross-tenant access.
- Confirm the implementation does not add live model execution, coordinator auto-launch, cyclic graph execution, or a new Admin workspace.

## Documentation Impact

- Add Spec 060 plan, research, data model, contracts, quickstart, tasks, QA guide, UI walkthrough, manual QA user guide, and reviewer notes.
- Update `curl_testing.md` for new design review JSON route families.
- Update `AGENTS.md` Spec Kit plan pointer during planning only through the normal Spec Kit plan flow.
