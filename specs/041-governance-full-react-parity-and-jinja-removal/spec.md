# Feature Specification: Governance Full React Parity And Jinja Removal

**Feature Branch**: `codex/041-governance-full-react-parity-and-jinja-removal`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Governance Full React Parity and Jinja Removal. Spec 031 added a React governance workspace, but full removal requires React parity for model-skill config, model provider list/detail/edit/catalog and test results, prompt list/detail/edit/history/preview, agent profile list/detail/edit/history/resolve, routing previews, policy history, run provenance, credential reference diagnostics, provider probes, and direct-call guardrail evidence. Old governance Jinja routes must redirect or retire only after parity is proven."

## Clarifications

### Session 2026-05-06

- Q: How should missing provider, prompt, and profile create/edit browser flows be represented after Jinja deletion? → A: Add React routes, panels, or modals backed by backend-owned contracts for every provider, prompt, and profile create/edit flow before deleting the matching template. (autopilot)
- Q: Who owns provider, prompt, profile, credential, probe, routing, and guardrail mutation decisions? → A: Existing backend services remain authoritative; React renders only authorized actions and mutation results returned by those services. (autopilot)
- Q: Which governance actions stay platform-admin only? → A: Provider create/edit/catalog sync/probe/test, credential-reference mutation, and direct-call guardrail mutation remain platform-admin only; tenant admins get read-only authorized readiness and provenance views. (autopilot)
- Q: How should old governance URLs preserve direct-link behavior? → A: Redirect old provider, prompt, profile, and model-skill config browser URLs to stable React governance paths when safe ids and tenant scope can be preserved; otherwise return a non-Jinja safe problem or documented gone response. (autopilot)
- Q: How should local/CI validation treat provider probes, prompt previews, profile resolution, routing previews, and provenance? → A: Use deterministic mocked-safe actions and fixtures only; no live provider, Auth0, Telegram, credential, connector, external tool, or direct SDK call is allowed. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Govern Providers Through React Only (Priority: P1)

Platform administrators need the full model provider browser journey to work through React, including provider list, create/edit, detail, catalog readiness, credential reference diagnostics, explicit probe/test results, direct-call guardrail evidence, and safe denied states. Tenant administrators need read-only provider catalog readiness for their authorized tenant scope without platform-only mutation controls.

**Why this priority**: Provider configuration and health are the most sensitive governance surface. It touches credential references, provider probes, direct-call guardrails, tenant grants, and model routing safety.

**Independent Test**: Sign in as a platform-admin local principal and an Auth0-shaped platform principal, open provider governance React views and old provider browser URLs, run deterministic mocked probe and credential-reference actions, then sign in as a tenant admin and prove mutation controls are unavailable and cross-tenant/provider labels do not leak.

**Acceptance Scenarios**:

1. **Given** a platform administrator opens provider governance, **When** they list, create, edit, inspect catalog readiness, run an explicit mocked probe, and review test results, **Then** every browser-visible journey is React-backed and every decision is served by backend-owned JSON contracts.
2. **Given** provider credentials are missing, invalid, or unauthorized, **When** diagnostics or probe evidence is requested, **Then** the UI shows safe readiness, failure category, breaker, and remediation summaries without resolved credential values, authorization headers, provider request bodies, provider response bodies, or stack traces.
3. **Given** a tenant administrator opens provider governance, **When** platform-only provider create/edit/probe/credential controls would otherwise appear, **Then** the backend denies or omits those controls and only authorized tenant catalog readiness is visible.
4. **Given** old provider routes are opened, **When** parity exists for the route and parameters, **Then** the browser redirects to a React governance path preserving safe tenant/id/query intent or returns a non-Jinja safe problem response.

---

### User Story 2 - Manage Prompts And Profiles Through React Only (Priority: P2)

Authorized administrators need prompt list/detail/edit/history/preview and agent runtime profile list/detail/edit/history/resolve experiences to be React-backed, including safe prompt previews, fixture-backed render tests, version history, grants, model/provider/profile pins, and profile resolution links.

**Why this priority**: Prompt and profile changes shape runtime behavior. Browser parity must retain redaction, version pinning, and grants before prompt and profile templates are removed.

**Independent Test**: Open prompt and profile React views, request deterministic safe previews and profile resolution previews, exercise safe save/preview actions, follow old prompt/profile direct links, and verify unsafe prompt/completion text is blocked or summarized before React rendering.

**Acceptance Scenarios**:

1. **Given** an authorized prompt lineage, **When** an admin opens list, detail, edit, history, and preview views, **Then** React shows safe version summaries, grants, render readiness, fixture-backed preview outcomes, and mutation states from backend-owned contracts.
2. **Given** unsafe prompt or completion content would be included in a preview, **When** the preview is requested, **Then** the backend blocks or summarizes it before React rendering and records safe redaction evidence.
3. **Given** an authorized runtime profile, **When** an admin opens list, detail, edit, history, and resolve views, **Then** React shows model/provider/prompt/skill bindings, grant summaries, resolver status, and read-only resolution output.
4. **Given** a prompt/profile direct link is unauthorized or cross-tenant, **When** it is requested through React JSON or old browser compatibility routes, **Then** the system fails closed without revealing protected labels, version metadata, raw prompt text, or policy history.

---

### User Story 3 - Review Routing, Policy, Model-Skill Config, And Provenance Through React Only (Priority: P3)

Governance reviewers need model-skill config history, routing previews, policy history, run provenance, credential reference diagnostics, and direct-call guardrail evidence to be available through React and to replace old model-skill config Jinja pages safely.

**Why this priority**: Governance deletion is not complete until reviewers can explain routing and provenance without falling back to Jinja, raw JSON, live providers, or unsafe direct calls.

**Independent Test**: Run deterministic read-only routing preview, open model-skill config history and run provenance React views, request old model-skill config routes, and verify every output is redacted, tenant-scoped, audit-safe, and does not invoke live providers or tools.

**Acceptance Scenarios**:

1. **Given** routing preview inputs for a tenant-scoped workflow, **When** the admin evaluates routing, **Then** React shows backend-owned model/skill decision summaries, fallback or deny status, policy reasons, and direct-call guardrail evidence without external side effects.
2. **Given** policy or model-skill configuration history exists, **When** the reviewer filters by domain, actor, tenant, status, or time window, **Then** React shows bounded safe summaries and audit references.
3. **Given** a run provenance fixture, **When** the reviewer opens provenance, **Then** React links provider, model, prompt, profile, routing, credential reference, usage, and audit evidence through safe identifiers and summaries.
4. **Given** old model-skill config routes are opened, **When** route parity is proven, **Then** the browser redirects to React or returns a documented non-Jinja compatibility response with no protected existence leak.

### Edge Cases

- A provider connection id, catalog entry, prompt lineage id, prompt version id, profile id, profile version id, route history id, or run id in an old URL no longer exists.
- A provider probe is requested by a tenant admin or an unauthenticated user.
- A credential reference exists but the secret resolver reports unavailable, unauthorized, malformed, or policy-denied status.
- A local OpenAI-compatible no-auth provider is configured outside the explicit allowlist.
- A prompt preview includes unsafe raw prompt text, raw completion text, memory content, private channel content, or connector payloads.
- A profile resolution preview would require a live provider, live credential store, Telegram call, connector call, or direct SDK call.
- Policy history contains stale versions, deleted grants, conflicting revision tokens, failed audit writes, or large diff payloads.
- Run provenance references artifacts or usage records from another tenant.
- Old route query parameters include unsafe redirects, secret-like values, raw prompt fragments, provider tokens, or oversized filters.
- A governance template or helper is still imported by a later non-governance route.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide React-backed browser parity for model provider list, create/edit, detail, catalog readiness, test results, credential diagnostics, explicit probes, direct-call guardrail evidence, and denied/unavailable states.
- **FR-002**: The system MUST provide React-backed browser parity for prompt list, detail, edit, history, safe preview, fixture render readiness, grants, mutation states, and denied/unavailable states.
- **FR-003**: The system MUST provide React-backed browser parity for agent runtime profile list, detail, edit, history, resolve preview, grants, routing summaries, mutation states, and denied/unavailable states.
- **FR-004**: The system MUST provide React-backed browser parity for model-skill config, routing preview, policy/config history, run provenance, credential reference diagnostics, direct-call guardrail evidence, and denied/unavailable states.
- **FR-005**: Existing provider, prompt, runtime profile, routing, model gateway, credential resolution, audit, redaction, usage, and provenance services MUST remain authoritative for browser decisions.
- **FR-006**: React governance contracts MUST be backend-owned and generated from server schemas where browser contracts are needed.
- **FR-007**: Old governance browser URLs MUST redirect to equivalent React governance routes when route parameters, tenant scope, filters, ids, anchors, and safe breadcrumbs can be preserved unambiguously and authorization allows it.
- **FR-008**: Old governance browser URLs that cannot safely redirect MUST return documented non-Jinja compatibility, gone, denied, or unavailable responses without exposing protected resource existence.
- **FR-009**: Provider creation, provider mutation, catalog sync, explicit probes/tests, credential-reference mutation, and direct-call guardrail mutation MUST remain platform-admin only.
- **FR-010**: Tenant admins MUST see only authorized provider catalog readiness, prompt grants, profile grants, routing previews, policy history, and provenance for their active tenant scope.
- **FR-011**: Provider probes MUST be explicit user-triggered mocked-safe actions in local and CI validation and MUST NOT introduce unbounded background polling.
- **FR-012**: Routing and profile resolution previews MUST be read-only policy evaluations and MUST NOT call live model providers, external tools, Telegram, credential stores, connector gateways, or direct SDK clients in local/CI validation.
- **FR-013**: Prompt previews MUST block or summarize unsafe prompt/completion content before React rendering.
- **FR-014**: Direct-call guardrail evidence MUST preserve ModelGateway-only execution requirements and MUST NOT enable browser-side provider execution.
- **FR-015**: Legacy provider, prompt, profile, and model-skill config form posts MUST be converted to backend JSON or redirect compatibility handlers before their templates are deleted.
- **FR-016**: The implementation MUST prove that governance-owned legacy browser routes no longer render Jinja TemplateResponse after governance templates are deleted or converted.
- **FR-017**: The implementation MUST delete only governance-owned templates, browser handlers, helpers, and static assets whose parity evidence is complete for Spec 041.
- **FR-018**: Shared Jinja infrastructure, non-governance templates, global template providers, Jinja dependencies, and later-spec domains MUST remain until their roadmap owners complete deletion-grade parity.
- **FR-019**: Reviewer notes MUST record deleted, redirected, converted, retained, and blocked governance inventory items with evidence references and rollback guidance.
- **FR-020**: React UI, redirects, compatibility responses, exports, screenshots, QA docs, logs, and reviewer notes MUST NOT expose raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, raw run payloads, private channel messages, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-021**: Auth0-shaped backend tests MUST cover authenticated, unauthenticated, unauthorized, platform-only, tenant-scoped, cross-tenant, direct-link, redirect, denied, and redaction behavior.
- **FR-022**: Local-principal Playwright flows MUST cover platform-admin and tenant-admin governance journeys in the React UI.
- **FR-023**: QA artifacts MUST document deterministic seed data, route coverage, direct-link redirects, denied/unavailable states, redaction checks, governance template deletion evidence, scanner results, and rollback steps.

### Key Entities *(include if feature involves data)*

- **Governance Provider Entry**: Provider connection or catalog item, mode, tenant availability, health, credential readiness, probe status, direct-call guardrail summary, and authorized actions.
- **Governance Credential Diagnostic**: Safe credential reference metadata, readiness, fingerprint, resolver status, policy reason, and remediation hint without resolved values.
- **Governance Prompt Entry**: Prompt lineage/version state, grants, safe diff summary, render readiness, preview state, and authorized actions.
- **Safe Prompt Preview Result**: Fixture-backed preview status, blocked or summarized content indicators, redaction findings, safe variables, audit reference, and artifact references.
- **Governance Runtime Profile Entry**: Profile lineage/version state, model/provider/prompt/skill bindings, grants, resolver readiness, policy state, and authorized actions.
- **Profile Resolution Preview**: Read-only selected profile, model route, prompt route, provider route, skill route, fallback or deny reason, and remediation hints.
- **Governance Routing Preview**: Read-only model/skill decision summary, policy reasons, fallback/deny status, direct-call guardrail evidence, and audit reference.
- **Governance History Record**: Bounded safe policy/config/model-skill history item with domain, actor, tenant scope, timestamp, change category, outcome, audit reference, and safe diff summary.
- **Governance Run Provenance**: Run-level evidence tying workflow, provider, model, prompt, profile, routing, credential reference, usage, and audit records through safe identifiers.
- **Governance Legacy Route Mapping**: Old browser path, route parameters, React destination or compatibility response, preserved query keys, authorization behavior, and deletion evidence.
- **Governance Retirement Evidence Record**: Reviewer-facing record of governance templates, handlers, helpers, direct links, and static assets that were deleted, redirected, converted, retained, or blocked.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of governance inventory items from Spec 038 and current source carry a Spec 041 outcome of deleted, redirected, converted to non-Jinja, retained with blocker, or outside active scope with evidence references.
- **SC-002**: 0 governance-owned browser routes covered by Spec 041 return Jinja TemplateResponse in backend route tests after implementation.
- **SC-003**: A platform admin can reach provider list/create/edit/detail/catalog/test-result/probe/credential diagnostics through React and old links redirect or retire safely.
- **SC-004**: A tenant admin can reach authorized governance read-only views and cannot mutate provider or credential state.
- **SC-005**: Prompt preview and profile resolution tests show unsafe raw prompt/completion/provider/tool/credential payloads are blocked or summarized before rendering.
- **SC-006**: Routing preview, policy history, model-skill config history, and run provenance are available through React with no live provider/tool/credential side effects in local/CI validation.
- **SC-007**: Auth0-shaped backend tests cover authorized, denied, unauthenticated, platform-only, tenant-scoped, cross-tenant, old-route redirect, and redaction behavior.
- **SC-008**: Local-principal Playwright evidence proves platform-admin and tenant-admin users can complete representative React governance journeys and old route recovery.
- **SC-009**: Scanner/import checks show no remaining governance-owned template file is rendered by governance browser routes, and any retained shared template/helper has a documented blocker.
- **SC-010**: QA docs and reviewer notes let a reviewer reproduce governance React parity and Jinja removal evidence within 15 minutes.

## Assumptions

- Spec 031 React governance behavior and backend contracts are the baseline for governance React parity.
- Existing model provider, prompt, runtime profile, routing, gateway, credential resolver, audit, redaction, and provenance services remain authoritative.
- Static Vite-built React assets and Python-generated non-Jinja compatibility responses are allowed; server-side Jinja rendering is the removal target.
- Spec 041 owns model provider, prompt, agent profile, and model-skill config browser surfaces only. Skill registry, test bench, operations, channel/membership, user-facing run UI, and global Jinja infrastructure are owned by later specs.
- Local QA uses deterministic local principals and mocked-safe dependencies. Real Auth0, provider, Telegram, credential, connector, and external tool calls remain out of scope for validation.
