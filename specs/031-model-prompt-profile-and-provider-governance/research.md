# Research: Model, Prompt, Profile, And Provider Governance

## Decision 1: Backend-Owned Governance Aggregation

**Decision**: Build a backend governance aggregator that composes existing provider catalog, prompt library, runtime profile, model-skill routing, secret resolver, gateway provenance, audit, and redaction behavior into React-specific safe contracts.

**Rationale**: Specs 007, 011, 012, 021, and 025 already define the authoritative domain rules. React should improve workflow clarity, not duplicate authorization, tenant scope, credential policy, prompt safety, or ModelGateway routing rules in the browser.

**Alternatives Considered**:

- Browser-side composition from many raw domain endpoints: rejected because it risks leaking raw IDs, labels, prompts, provider details, or unauthorized tenant data.
- New persistence model for governance: rejected because existing provider/prompt/profile/routing/audit models remain authoritative.

## Decision 2: Platform-Only Provider And Credential Mutations

**Decision**: Provider creation, update, sync, probe/test actions, credential-reference changes, and direct-call guardrail changes are platform-admin only.

**Rationale**: Provider configuration controls production model access and credential selection. Tenant administrators can safely review authorized catalog readiness, but mutations must stay behind platform authorization and audit.

**Alternatives Considered**:

- Tenant-admin provider mutation for tenant-specific overrides: rejected for this spec because tenant/provider ownership and credential lifecycle ambiguity would trigger a stop condition.
- Client-side hiding without backend enforcement: rejected because backend authorization must own the boundary.

## Decision 3: Explicit Provider Probes

**Decision**: Provider probes are explicit user-triggered actions. The page may show last-known health, but it does not introduce background polling.

**Rationale**: Probes can touch credentials, provider adapters, retry/breaker policy, and audit. Explicit actions are easier to reason about, test, and audit, and they avoid unbounded local/CI work.

**Alternatives Considered**:

- Continuous health polling: rejected due to load, noisy audit, and ambiguous credential access.
- Probe on every page load: rejected because users should understand when a connection test happens.

## Decision 4: Fixture-Safe Prompt Preview

**Decision**: Prompt previews use deterministic fixtures and existing safety/redaction behavior. Unsafe prompt or completion text is blocked or summarized before React rendering.

**Rationale**: Prompt previews are valuable for non-technical admins, but raw prompts/completions can contain sensitive user, channel, memory, or tool content. Backend safety must decide what can be displayed.

**Alternatives Considered**:

- Render raw prompt diffs by default: rejected because raw prompt exposure is explicitly disallowed when unsafe.
- Call a live model for preview: rejected for local/CI and outside the approved scope.

## Decision 5: Read-Only Routing And Profile Previews

**Decision**: Profile resolution and model/skill routing previews are read-only backend policy evaluations with safe decision summaries.

**Rationale**: Previewing policy outcomes helps admins diagnose routing without triggering runtime side effects. ModelGateway-only requirements and direct SDK guardrails remain backend owned.

**Alternatives Considered**:

- Browser-side routing prediction: rejected due to policy drift.
- Live dry-run provider execution: rejected because it would call external systems and blur preview vs execution semantics.

## Decision 6: Provenance Uses Safe Evidence Links

**Decision**: Run provenance shows safe identifiers, labels, audit references, and authorized links for provider, model, prompt, profile, routing, credential reference, and usage evidence.

**Rationale**: Admins need to trace decisions, but raw runtime payloads, prompts, completions, credential values, provider payloads, and unauthorized tenant labels must stay out of UI contracts and screenshots.

**Alternatives Considered**:

- Embed raw trace payloads in React for debugging: rejected due to privacy and prompt/credential risks.
- Hide provenance entirely: rejected because run diagnosis and policy review are core user stories.

## Decision 7: Bounded Domain Tabs Instead Of One Giant Table

**Decision**: Organize the route around Setup, Prompts, Profiles, Routing, Providers, and Provenance sections, each with bounded lists, clear status badges, guided actions, empty states, and safe recovery hints.

**Rationale**: Non-technical administrators need a coherent path through related but distinct governance domains. Tabs/sections keep the interface scannable and avoid exposing raw domain jargon as the primary organizing model.

**Alternatives Considered**:

- One dense combined governance table: rejected because it hides workflows and makes recovery steps unclear.
- Separate unrelated routes for each domain: rejected for this spec because the roadmap asks for a coherent governance experience.
