# Research: Governance React Live Data

## Decision: Project Governance From Existing Repositories

Use existing provider, prompt, runtime profile, model-skill configuration, gateway, usage/provenance, and audit repositories/services instead of building a new governance store.

**Rationale**: The current fixed `admin/governance.py` builder mirrors concepts that already have durable ownership elsewhere. Reusing those owners keeps authorization, revision state, readiness, policy history, and audit behavior consistent with the rest of the platform.

**Alternatives considered**:

- Keep the QA031 builder and swap fixture values at runtime. Rejected because production would still own deterministic rows.
- Add a separate governance projection table. Rejected because it would duplicate durable state and drift from provider/prompt/profile owners.

## Decision: Empty And Unavailable States Are First-Class

Governance panels must render empty or unavailable states when no live data exists, when diagnostics have not run, or when evidence is not safely renderable.

**Rationale**: Fresh QA and production tenants may legitimately have no providers, prompts, profiles, routes, diagnostics, or provenance. Truthful absence is the desired behavior.

**Alternatives considered**:

- Seed production-like default rows automatically. Rejected because it recreates mock data under another name.
- Hide empty panels. Rejected because users need to understand which governance evidence is missing.

## Decision: Render Safe Summaries Only

Prompt previews, render tests, credential references, provider diagnostics, gateway attempts, and run provenance must render safe summaries, labels, fingerprints, timestamps, statuses, and references only.

**Rationale**: The governance area is security-sensitive; raw prompts, completions, credentials, provider payloads, private channel messages, and run payloads are explicitly prohibited in UI and QA artifacts.

**Alternatives considered**:

- Render raw prompt templates to make governance more inspectable. Rejected because it violates the redaction and prompt safety policy.
- Store sanitized copies in frontend fixtures. Rejected because production contracts must stay backend-owned.

## Decision: Keep Probe And Credential Actions Platform-Only

Provider probes and credential-reference actions remain available only to authorized platform administrators. Local QA uses mocked or local allowlisted diagnostics and never performs real provider, credential-store, or outbound calls.

**Rationale**: Probe and credential behavior touches external systems and secrets. Existing policy already separates local safe diagnostics from production resolution.

**Alternatives considered**:

- Allow tenant admins to run probes for their own providers. Deferred because it changes authorization scope beyond mock-data removal.
- Disable probes entirely. Rejected because live governance needs safe health/readiness evidence.

## Decision: Use Prompt Or Profile Draft Save For Playwright Persistence

The Playwright flow should perform one safe user-visible governance mutation that persists through existing prompt or profile services, then verify that saved state through API or redaction-safe database evidence.

**Rationale**: Prompt/profile draft save is safer than live provider probing, avoids external side effects, and proves that React governance actions are not fake success responses.

**Alternatives considered**:

- Use provider credential-reference save. Rejected for Playwright because it touches secret-reference semantics and is platform-only.
- Use routing preview only. Rejected as the sole action because preview can be read-only and does not necessarily prove persistence.

## Decision: Scanner Guardrails Target Production Governance Markers

Update live-data scanner mappings to classify `src/multi_agent_platform/admin/governance.py`, governance route handlers, frontend governance fixtures, generated contracts, and built assets so QA031 markers are allowed only in test-only fixtures or historical specs.

**Rationale**: Spec 048 introduced the worklist and scanner; Spec 051 must close the governance surface and prevent future regressions.

**Alternatives considered**:

- Remove all QA031 strings from the repository. Rejected because historical specs and test fixtures can legitimately retain them.
