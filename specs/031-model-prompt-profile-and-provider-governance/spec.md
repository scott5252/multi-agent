# Feature Specification: Model, Prompt, Profile, And Provider Governance

**Feature Branch**: `codex/031-model-prompt-profile-and-provider-governance`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "React-based model, prompt, profile, and provider governance. Non-technical admins need a coherent experience for configuring model providers, testing safe connections, reviewing provider health, managing prompt versions, previewing safe prompt renders, configuring agent runtime profiles, previewing model/skill routing decisions, reviewing policy history, configuring credential secret references, understanding live credential resolution diagnostics, and understanding run provenance."

## Clarifications

### Session 2026-05-05

- Q: How should the React governance domains be grouped for non-technical administrators? A: Organize the route around Setup, Prompts, Profiles, Routing, Providers, and Provenance, with backend-owned section metadata and authorized links. (autopilot)
- Q: Who can mutate provider configuration and credential references? A: Provider creation, update, sync, tests/probes, credential-reference changes, and direct-call guardrail changes are platform-admin only. (autopilot)
- Q: What can tenant administrators see? A: Tenant admins see only authorized provider catalog readiness, prompt grants, profile grants, routing previews, policy history, and run provenance for their active tenant scope. (autopilot)
- Q: How should prompt previews work? A: Prompt previews use existing deterministic fixture safety and return blocked or summarized results before React rendering whenever raw prompt or completion text is unsafe. (autopilot)
- Q: How should provider probe refresh work? A: Probes are explicit user-triggered actions; health status may show last known safe diagnostics but no unbounded background polling is introduced. (autopilot)
- Q: How should routing previews behave? A: Routing previews are read-only policy evaluations and never invoke live providers, credential stores, external tools, Telegram, or direct SDK calls in local/CI validation. (autopilot)
- Q: How should local OpenAI-compatible no-auth behavior be represented? A: It is shown only when covered by the existing explicit allowlist; non-allowlisted no-auth behavior is degraded or denied with safe diagnostics. (autopilot)
- Q: How should direct SDK guardrail evidence be handled? A: React displays backend-produced guardrail evidence summaries only and preserves ModelGateway-only execution requirements. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Govern Provider Setup And Health (Priority: P1)

Platform administrators can configure model provider catalog entries, select credential secret references, run explicit safe connection probes, review provider health and live credential resolution diagnostics, and understand direct-call guardrail evidence without seeing raw credential values or provider tokens. Tenant administrators can review only authorized provider readiness and catalog grants.

**Why this priority**: Provider configuration and health are prerequisites for safe model execution, prompt previews, routing decisions, and runtime provenance.

**Independent Test**: Sign in with local principal as a platform admin, open `/admin/app/governance`, configure a deterministic provider reference, run an explicit mocked probe, verify safe health and credential diagnostics, then sign in as a tenant admin and verify provider mutation controls are unavailable and only authorized catalog entries are visible.

**Acceptance Scenarios**:

1. **Given** a platform administrator, **When** they open the governance setup and providers views, **Then** provider catalog entries, credential reference status, health, probe history, and direct-call guardrail evidence are displayed through safe summaries only.
2. **Given** a provider credential reference is missing, invalid, or unreadable, **When** the admin reviews diagnostics or runs a probe, **Then** the route fails closed or returns a safe unavailable state with no resolved credential value, token, authorization header, stack trace, or provider payload.
3. **Given** a tenant administrator, **When** they open the same React governance route, **Then** provider mutation controls are hidden or disabled by backend authorization and only tenant-authorized provider catalog readiness is visible.
4. **Given** Auth0-shaped principal overrides and local-principal mode, **When** protected governance contracts or actions are requested, **Then** both modes enforce equivalent authorization, tenant scope, audit, and redaction behavior.

---

### User Story 2 - Manage Prompts And Runtime Profiles Safely (Priority: P2)

Platform and authorized tenant administrators can review prompt lineages, draft and published prompt versions, safe diffs, fixture-backed render previews, runtime profile versions, model/provider/profile pins, skill routing requirements, and profile resolution previews without exposing unsafe raw prompts or completions.

**Why this priority**: Prompt and profile governance directly affects runtime behavior and must be understandable to non-technical administrators while preserving existing prompt safety controls.

**Independent Test**: Open a deterministic prompt/profile fixture, review prompt history, save a safe draft summary, run a fixture-backed preview, inspect profile configuration and resolution output, and verify unsafe prompt content and completions are summarized or blocked.

**Acceptance Scenarios**:

1. **Given** an authorized prompt lineage, **When** an admin opens prompt governance, **Then** they see draft/published status, version history, safe change summaries, grants, render-test readiness, and fixture-backed preview controls.
2. **Given** a prompt preview fixture contains unsafe text, **When** preview is requested, **Then** the backend returns a blocked or summarized preview with safe finding categories and no raw unsafe prompt or completion text.
3. **Given** a runtime profile version, **When** an admin reviews configuration, **Then** model/provider pins, prompt bindings, skill requirements, resolver status, and tenant grants appear as safe summaries with authorized links.
4. **Given** a tenant admin lacks a prompt or profile grant, **When** they attempt to request the detail contract, **Then** the route fails closed and does not reveal labels, version metadata, or policy history from another tenant.

---

### User Story 3 - Preview Routing, History, And Run Provenance (Priority: P3)

Administrators can run read-only routing previews for model and skill decisions, inspect policy/configuration history, trace run provenance back to provider/prompt/profile versions, and understand recovery actions for failed routing, credential resolution, or health checks.

**Why this priority**: Governance decisions need explainable evidence before admins can safely diagnose production behavior or approve future changes.

**Independent Test**: Run a deterministic read-only routing preview, filter policy history, inspect run provenance for a fixture run, and verify every output is redacted, tenant-scoped, audit-safe, and consistent with ModelGateway-only execution.

**Acceptance Scenarios**:

1. **Given** routing preview inputs for a tenant workflow, **When** an admin evaluates routing, **Then** the backend returns read-only model/skill decision summaries, policy reasons, fallback status, and safe remediation hints without invoking live providers or tools.
2. **Given** policy or configuration history exists, **When** an admin filters by domain, actor, tenant, status, or time window, **Then** the page shows safe diff/history summaries and bounded results.
3. **Given** a run provenance fixture, **When** an admin opens provenance, **Then** they can identify provider, model, prompt, profile, routing, and credential-reference evidence without seeing raw prompts, completions, provider payloads, or resolved secrets.
4. **Given** cross-tenant routing, history, or provenance access is attempted, **When** the backend cannot prove authorization, tenant scope, or audit persistence, **Then** it fails closed with a safe problem response.

### Edge Cases

- A credential secret reference exists but points to an unavailable, unauthorized, or malformed credential.
- A provider probe returns degraded, failed, timeout, or breaker-open diagnostics.
- A local OpenAI-compatible provider is configured for no-auth behavior outside the explicit allowlist.
- A prompt render preview contains unsafe raw prompt text, raw completion text, private channel content, memory content, or connector payloads.
- A tenant admin attempts platform-only provider creation, update, sync, test, or credential-reference mutation.
- A tenant requests catalog, prompt, profile, policy, routing, or provenance data from another tenant.
- Policy history contains stale versions, deleted grants, failed audit writes, or conflicting revision tokens.
- Routing preview inputs request live provider, live credential, Telegram, external connector, or direct SDK calls in local/CI validation.
- Provider and gateway diagnostics include stack traces, local file paths, authorization headers, request bodies, response bodies, or provider tokens.
- JavaScript is unavailable; existing Jinja/admin API fallback routes remain available during migration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a protected additive React governance route at `/admin/app/governance` while preserving existing Jinja/model, prompt, profile, provider, and configuration routes as fallbacks until migration hardening retires them.
- **FR-002**: System MUST expose backend-owned JSON contracts for governance bootstrap, provider lists/details/forms/probes/catalog, credential reference selection, live credential resolution status, prompt lists/details/edit/preview/history, profile lists/details/edit/resolve, routing preview, policy history, run provenance, safe mutation results, and denied states.
- **FR-003**: System MUST generate TypeScript contracts from backend schemas and React MUST consume generated contracts rather than hand-maintained browser models for protected governance data.
- **FR-004**: System MUST support local-principal and Auth0-shaped principal validation for React governance routes and protected actions.
- **FR-005**: System MUST fail closed when authorization, tenant scope, credential policy, direct-call guardrails, provider routing policy, or audit persistence cannot be proven.
- **FR-006**: System MUST group governance workflows so non-technical admins can navigate setup overview, prompts, profiles, routing, providers, and provenance without relying on raw IDs, JSON, or implementation jargon as the primary interface.
- **FR-007**: System MUST restrict provider creation, provider mutation, provider sync, provider probe/test actions, credential reference changes, and direct-call guardrail changes to platform administrators.
- **FR-008**: System MUST allow tenant administrators to view only authorized provider catalog entries, prompt grants, profile grants, routing previews, policy history, and run provenance for their active tenant scope.
- **FR-009**: System MUST use explicit user-triggered provider probes and MUST avoid unbounded background probe polling.
- **FR-010**: System MUST make routing previews read-only policy evaluations that do not call live model providers, external tools, Telegram, credential stores, or direct SDK clients in local/CI validation.
- **FR-011**: System MUST render provider health, credential readiness, live resolution diagnostics, breaker status, local allowlist status, and direct-call guardrail evidence as safe summaries.
- **FR-012**: System MUST provide prompt version history, safe diff summaries, authorized safe draft edit/save controls, render-test readiness, and fixture-backed safe preview behavior.
- **FR-013**: System MUST block or summarize unsafe prompt previews before React rendering and MUST never render unsafe raw prompts or raw completions.
- **FR-014**: System MUST provide runtime profile version history, editable safe profile fields where authorized, model/provider/prompt/skill binding summaries, and profile resolution preview.
- **FR-015**: System MUST provide policy/configuration history and run provenance views with bounded filters, safe diff categories, actor summaries, audit references, and authorized cross-links.
- **FR-016**: System MUST show loading, empty, denied, partial, stale, conflict, credential unavailable, provider degraded, probe failed, routing failed, audit unavailable, and mutation confirmation states.
- **FR-017**: System MUST redact raw secrets, resolved credential values, secret provider payloads, provider tokens, authorization headers, raw prompts, raw completions, provider request/response bodies, private channel messages, memory contents, connector payloads, stack traces, local paths, and unauthorized tenant labels before rendering, logging, exporting, or storing QA artifacts.
- **FR-018**: System MUST preserve ModelGateway-only execution requirements and expose direct SDK guardrail evidence without enabling browser-side provider execution.
- **FR-019**: System MUST cross-link to existing workflow registry, prompt library, runtime profile, provider catalog, skill registry, operations, usage, audit/debugging, and provenance destinations only when URLs are authorized for the active principal.
- **FR-020**: System MUST produce QA documents, Playwright screenshots, backend tests, frontend tests, generated contract checks, and full Spec QA evidence before advancing to the next spec.

### Key Entities

- **GovernanceDashboard**: Authorized route envelope, active scope, section definitions, status summaries, routes, feature flags, and safe callouts for setup, prompts, profiles, routing, providers, and provenance.
- **ProviderGovernanceSummary**: Provider catalog entry, version, mode, tenant availability, health, breaker state, probe readiness, direct-call guardrail summary, local allowlist status, and authorized actions.
- **ProviderCredentialReference**: Safe credential reference metadata, source type, readiness, fingerprint, last resolution status, policy reason, and remediation hint without resolved values.
- **ProviderProbeDiagnostic**: Explicit probe result with status, latency bucket, failure category, retry/breaker evidence, audit reference, and redacted attempt details.
- **PromptLibrarySummary**: Prompt lineage, draft/published versions, grants, render-test readiness, safe change summary, policy status, and authorized actions.
- **SafePromptPreview**: Fixture-backed render result with blocked/summarized status, redaction findings, safe variables, preview artifact references, and no raw unsafe prompt or completion content.
- **RuntimeProfileGovernanceSummary**: Profile lineage/version, model/provider/prompt/skill bindings, grants, resolver readiness, policy state, and authorized edit actions.
- **ProfileResolutionPreview**: Read-only resolution output with selected profile version, model route, prompt route, provider route, skill route, fallback reason, and remediation hints.
- **RoutingPreviewResult**: Read-only model/skill routing decision summary, policy reasons, fallback/deny status, direct-call guardrail evidence, and audit reference.
- **PolicyHistoryRecord**: Bounded safe history item with domain, actor summary, tenant scope, timestamp, change category, policy outcome, audit reference, and safe diff summary.
- **RunProvenanceSummary**: Run-level provenance tying workflow, provider, model, prompt, profile, routing, credential reference, usage, and audit evidence through safe identifiers and summaries.
- **GovernanceMutationResult**: Provider, prompt, profile, probe, preview, resolve, and routing action response with status, toast, revision token, warnings, audit reference, and safe redirect links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A platform admin can configure a deterministic provider credential reference, run an explicit mocked probe, and review health/credential diagnostics without raw secret or provider payload exposure.
- **SC-002**: A tenant admin can review only authorized provider catalog readiness, prompt grants, profile grants, routing previews, and provenance for their tenant and cannot mutate provider configuration.
- **SC-003**: A prompt admin can inspect deterministic prompt version history and run a fixture-backed preview where unsafe prompt/completion content is blocked or summarized before rendering.
- **SC-004**: A profile admin can inspect and safely edit deterministic runtime profile settings, then run a read-only profile resolution preview.
- **SC-005**: A governance reviewer can run deterministic read-only routing preview, policy history filtering, and run provenance inspection without live providers, external tools, direct SDK calls, or cross-tenant leakage.
- **SC-006**: Local-principal and Auth0-shaped route tests cover authorized, denied, platform-only mutation, tenant-scoped, and cross-tenant behavior.
- **SC-007**: Playwright validation captures denied, platform governance, tenant governance, provider probe, prompt preview, profile/routing, and provenance evidence without unsafe text.
- **SC-008**: Full Spec QA passes with Ruff, format, mypy, coverage at or above 90 percent, generated TypeScript drift checks, frontend typecheck/tests/build, QA docs, and Playwright validation.

## Assumptions

- Existing model provider services, prompt services, runtime profile services, model-skill configuration resolver, ModelGateway provenance, ProviderSecretResolver, audit/redaction helpers, and local-principal test mode remain authoritative.
- The React governance experience is additive; existing Jinja/admin API governance routes remain available during migration.
- Local QA uses deterministic mocks and fixtures and does not require real Auth0, model provider, Telegram, credential, or connector calls.
- Prompt and provenance screens prioritize safe summaries, history, previews, and authorized links over raw JSON or raw domain payloads.
