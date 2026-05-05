# Research: React Agent And Workflow Test Bench

## Decision: Reuse Existing Test Bench Services As The Authority

**Rationale**: Spec 015 already defines tenant-scoped suites, cases, assertions, runs, artifacts, audit records, and publish-gate evidence. React should not reimplement test execution or policy logic in the browser.

**Alternatives considered**: Creating a new React-only suite model was rejected because it would duplicate authorization, redaction, and publish-gate rules.

## Decision: Backend-Owned Guided Forms

**Rationale**: Suite and case authoring needs target choices, assertion comparator choices, safe execution modes, evaluator options, thresholds, and revision tokens. Backend metadata keeps non-technical forms understandable while preserving policy and tenant scope.

**Alternatives considered**: Hand-coded browser option lists were rejected because they can drift from backend policy and expose unavailable targets.

## Decision: Mock Model And Mock Tools Are The Default Local Mode

**Rationale**: Local and CI validation must avoid live providers, Telegram, credentials, and connector side effects. Mock defaults let QA verify run launch, progress, diagnostics, artifacts, and gate evidence deterministically.

**Alternatives considered**: Defaulting to side-effect-disabled real gateway mode was rejected because it can still require provider readiness and credential policy not guaranteed in local QA.

## Decision: Real Dependency Probes Require Explicit Approval Evidence

**Rationale**: Probe requests can cross external boundaries. Approval state, policy reason, actor summary, and audit reference must be durable before any real probe path is offered.

**Alternatives considered**: Hiding probes entirely was rejected because production admins need to understand approved readiness paths; allowing probes by environment flag was rejected because it is too easy to misconfigure.

## Decision: Redacted Trace Summaries Only

**Rationale**: Raw prompts, completions, transcripts, memory, and connector payloads can contain secrets or private data. The React route renders step labels, safe excerpts, failure categories, usage, latency, and references only.

**Alternatives considered**: Inline transcript expansion was rejected because screenshot and browser source evidence must be shareable without cleanup.

## Decision: Artifact References Instead Of Payloads

**Rationale**: PostgreSQL remains transactional metadata storage; object/filesystem storage holds large payloads. React shows checksum, size, content class, retention state, redaction class, and authorized link state.

**Alternatives considered**: Embedding artifact JSON previews was rejected because artifact payloads can be oversized or sensitive.

## Decision: Backend-Owned Progress Snapshots

**Rationale**: Test run progress must survive refresh and resume. React can poll or follow existing SSE-compatible links, but status, terminal state, and completed steps are backend-owned.

**Alternatives considered**: Client timers or optimistic terminal states were rejected because they can misrepresent durable run state.

## Decision: Target Revision Binding For Runs And Gates

**Rationale**: Publish-gate evidence is useful only when it matches the current prompt/profile/workflow/subworkflow/published workflow revision. Gate contracts must show current, stale, missing, failing, running, and passing states explicitly.

**Alternatives considered**: Accepting the latest passing run by suite alone was rejected because it allows stale or manually copied evidence to bypass publish gates.

## Decision: React Routes Remain Additive

**Rationale**: Existing Jinja test bench routes remain the fallback until Spec 037 proves migration parity. React can provide a richer route without weakening established workflows.

**Alternatives considered**: Replacing Jinja routes immediately was rejected because retirement criteria are deferred to hardening.
