# Research: Test Bench React Live Data

## Decision: Use Existing Agent Test Services And Repository As Source Of Truth

**Decision**: Build React test bench projections from `AgentTestRepository`, `AgentTestBenchService`, persisted agent test suite/case/assertion/run/run-step/publication requirement records, safe artifact metadata, and audit records.

**Rationale**: These services already enforce tenant ownership, stale revision handling, safe execution modes, idempotent run launch, publication evidence, and redaction for fixture summaries. Reusing them avoids creating a second source of truth and gives React the same state that the public test bench API and publish gates use.

**Alternatives considered**:

- Keep fixed QA033/QA043 builders and add labels: rejected because production routes would still invent suites, runs, gates, and artifacts.
- Query models directly inside FastAPI route handlers: rejected because route handlers would grow policy, redaction, and projection logic that belongs in service/repository helpers.
- Move projection decisions to React: rejected because authorization, tenant scoping, redaction, and mutation outcomes must remain backend-owned.

## Decision: Return Explicit Provenance And Empty-State Metadata

**Decision**: Extend test bench response envelopes with provenance and empty-state metadata that identifies live repository-backed data, selected scope, source record counts, and truthful empty/unavailable/denied reasons.

**Rationale**: Reviewers need to distinguish an empty database from a stale fixture route. Explicit metadata also gives scanner and contract tests a stable way to verify that the route is live-backed without relying only on visible row names.

**Alternatives considered**:

- Infer live behavior from zero rows: rejected because empty fixed arrays and empty live results are visually indistinguishable.
- Add frontend-only banners: rejected because provenance must be part of the backend contract and route tests.

## Decision: Use Mocked-Safe Run Launch For QA Mutations

**Decision**: Playwright should perform a safe user-visible action that persists backend state, preferably launching a seeded suite with a mocked-safe mode or saving suite/case metadata through `AgentTestBenchService`.

**Rationale**: A run launch exercises the most important test bench path: suite lookup, active case validation, idempotency, sandbox execution, run persistence, run-step projection, artifact summary projection, and refreshed UI state. The sandbox blocks real provider/tool/credential/outbound side effects.

**Alternatives considered**:

- Refresh publish-gate evidence only: acceptable fallback, but it may not create new run evidence and is less representative of the test bench workspace.
- Create a new suite only: useful but does not prove run progress, artifacts, or publish-gate evidence.
- Real dependency probe: rejected for local QA because it requires explicit approval and could perform external side effects.

## Decision: Summarize Artifacts And Traces Before React

**Decision**: React receives artifact labels, kinds, hashes, sizes, retention states, access outcomes, safe summaries, and audit references only. Run steps expose safe transcript excerpts or redaction summaries, not raw prompts, completions, payloads, stack traces, storage URIs, or artifact contents.

**Rationale**: Test bench records can be close to raw workflow inputs and model outputs. Keeping only safe summaries aligns with the existing schema validators and constitution requirements for secret hygiene and tiered storage.

**Alternatives considered**:

- Link raw artifact paths for local QA: rejected because local filesystem paths are prohibited in React and QA evidence.
- Render redacted transcripts inline by default: rejected because even redacted transcripts can be too large and should be summarized with artifact references.

## Decision: Publish-Gate Evidence Must Be Current-Revision And Repository-Backed

**Decision**: Publish-gate panels derive required suites and latest qualifying runs from `AgentTestPublicationRequirement` records and latest persisted runs for the target type, target id, and current target revision. Stale or missing evidence is explicit.

**Rationale**: The live-data migration must remove synthetic pass/fail gates. Release readiness depends on current-revision evidence and should fail closed when no qualifying run exists.

**Alternatives considered**:

- Reuse static gates from the fixed builder: rejected because they can show passing evidence for nonexistent or stale runs.
- Treat any passing run as qualifying: rejected because evidence must match target scope and revision where a revision is required.

## Decision: Scanner Guardrails Target Production Surfaces Only

**Decision**: Update live-data scanner mappings and tests so QA033/QA043 test bench markers are forbidden in production test bench builders/routes/build assets, while still allowed in test-only fixtures, historical specs, and QA seed scripts.

**Rationale**: The roadmap explicitly allows test fixtures and historical docs to retain deterministic markers. The risk is production UI routes and projection services returning fixed demo data.

**Alternatives considered**:

- Ban QA033/QA043 globally: rejected because it would create false positives in test-only and historical artifacts.
- Rely on manual review only: rejected because scanner guardrails are the shared protection against regression across remaining specs.
