# Research: Skill Lifecycle React Live Data

## Decision: Reuse Existing Skill Registry Records As The Source Of Truth

Use persisted skill package, package version, tenant grant, installation, and audit records for production route projections.

**Rationale**: Specs 014, 014-v2, 021, and 032 already established the package lifecycle, tenant installation, credential readiness, and connector governance domains. Spec 052 is a live-data migration, so replacing fixed QA032 builders with repository/service projections is lower risk than inventing a parallel lifecycle model.

**Alternatives considered**: Keep fixed QA032 projections and mark them as examples; rejected because production routes would still invent domain rows. Move fixtures into frontend test data; rejected because the browser would still not prove live backend state.

## Decision: Render Safe Summaries And Artifact References Only

Skill manifests, validation output, connector diagnostics, smoke-test records, and SkillExecutionGateway evidence must reach React as safe summaries, fingerprints, artifact references, status values, timestamps, and audit ids.

**Rationale**: The project constitution requires secret hygiene and controlled tool access. Manifest bodies, connector request/response payloads, tool outputs, and validation transcripts can contain sensitive operational details.

**Alternatives considered**: Truncate raw content client-side; rejected because unsafe data would already cross the backend boundary. Store raw details in React state but hide them; rejected for the same reason.

## Decision: Empty, Denied, Blocked, Stale, And Unavailable Are First-Class Outcomes

Every panel and mutation must distinguish live records from empty scopes, denied scopes, blocked lifecycle state, stale revision conflicts, and unavailable evidence.

**Rationale**: The old deterministic builder made every panel appear populated. Live systems often have no package, no install, no credential, or no diagnostic result yet. Treating these states explicitly prevents fake readiness.

**Alternatives considered**: Return empty arrays only; rejected because QA reviewers need to understand whether the route is empty, denied, blocked, or missing safe evidence.

## Decision: Local QA Uses Mocked-Safe Diagnostics

Playwright and Spec QA may create persisted smoke-test or connector diagnostic evidence, but execution must be mocked-safe or local allowlisted unless an explicit artifact approves a live probe.

**Rationale**: Local validation must prove backend persistence and authorization without real connector, provider, credential, or outbound calls.

**Alternatives considered**: Call real connector adapters in QA; rejected because it risks secret use and network side effects.

## Decision: Playwright Must Persist One Lifecycle Action

The QA052 Playwright flow should perform one safe visible action, then post-UI validation should query an API first and a redaction-safe database check when needed.

**Rationale**: A loaded page does not prove mutations are durable. A safe action such as credential reference metadata save, smoke-test refresh, candidate validation, grant update, or install action can prove service-backed mutation behavior.

**Alternatives considered**: Validate only through backend route tests; rejected because the roadmap requires browser-first UI exercise. Use a non-mutating preview only; rejected because skill lifecycle has safe mutation surfaces.

## Decision: Scanner Guardrails Track QA032 Markers

The live-data inventory scanner should fail when former QA032 package/install/credential/diagnostic/audit markers appear in production route builders or React runtime paths.

**Rationale**: The migration must prevent fixed rows from returning later while still allowing historical specs and test fixtures.

**Alternatives considered**: Search only source files manually; rejected because the autopilot requires repeatable guardrails.
