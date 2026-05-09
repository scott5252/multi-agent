# Research: Custom Workflow Test Evidence And Publish Setup

## Decision: Reuse Test Bench As Evidence Source Of Truth

Use existing Agent Tests/Test Bench suites, cases, runs, artifact references, publication requirements, and publish-gate summary behavior. Add workflow-context adapters only where the workflow setup UI needs to create or bind records without copied internal ids.

**Rationale**: The Test Bench already owns tenant-scoped suites, cases, deterministic run launch, safe artifact summaries, and publish evidence. Reusing it avoids duplicate evidence semantics and keeps publish trust in one backend domain.

**Alternatives considered**:

- A separate workflow setup evidence table: rejected because it would create a second publish trust path and require extra reconciliation.
- Browser-only evidence state: rejected because publish readiness must remain backend-owned and durable.

## Decision: Evidence Freshness Is Draft-Revision Specific

Treat evidence as current only when the required suite, cases, and latest passing deterministic run target the same workflow draft revision that will be published.

**Rationale**: Workflow documents can change roles, graph topology, prompts, profiles, contracts, and test requirements. Older evidence cannot prove the current draft is safe.

**Alternatives considered**:

- Workflow lineage-level evidence: rejected because it would let old runs satisfy changed drafts.
- Manual reviewer override in Spec 072: rejected because approval semantics are out of scope and would need durable approval state.

## Decision: Deterministic Safe Mode For QA And Default Launch

Default contextual run launch to deterministic safe execution using local mocks and deny live provider/external tool modes unless backend policy identifies an approved live probe.

**Rationale**: Local and CI validation must avoid real providers, credentials, tools, side effects, and outbound calls. Existing Test Bench safe-mode controls provide the right trust boundary.

**Alternatives considered**:

- Live provider mode in QA: rejected because it introduces external side effects and secret handling.
- Client-side mode filtering only: rejected because unsupported execution mode denial must be enforced by backend contracts.

## Decision: Safe Evidence Summaries Only

Expose only status, counts, suite/case labels, assertion summaries, diagnostics, target revision, and opaque artifact references. Never expose raw transcripts, raw prompt/completion text, tool/provider payloads, credentials, private payloads, stack traces, or local filesystem paths.

**Rationale**: Evidence exists to support publish decisions and operator repair, not to leak protected runtime or test payloads.

**Alternatives considered**:

- Inline transcript display behind a disclosure: rejected for workflow setup because screenshots and QA artifacts must stay safe.
- Local artifact paths: rejected because object-storage references and audit-safe ids are the allowed boundary.

## Decision: Workflow Registry Owns The Guided Context, Test Bench Owns Records

The workflow builder should render a contextual evidence panel with create/select/run/refresh actions, while cross-links open Agent Tests with the active tenant and workflow context preserved.

**Rationale**: Users need to complete setup without copying ids, but Agent Tests should remain the detailed authoring and diagnostics workspace.

**Alternatives considered**:

- Move all Test Bench authoring into Workflow Registry: rejected as too broad for Spec 072 and duplicative of existing Agent Tests UI.
- Force users to open Agent Tests manually and copy ids: rejected by the feature goal.

## Decision: Curl Coverage Depends On Route Surface

Update `curl_testing.md` only if implementation adds or behaviorally changes Test Bench, workflow setup, evidence, or publish route families.

**Rationale**: The roadmap requires curl coverage for new/changed APIs, but pure UI reuse of existing routes should not add redundant curl commands.

**Alternatives considered**:

- Always add duplicate curl commands: rejected because it adds maintenance burden without new route coverage.
