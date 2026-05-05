# Feature Specification: React Admin UI Foundation

**Feature Branch**: `codex/026-react-admin-ui-foundation`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Create a feature specification for introducing the React admin UI foundation. The goal is to add the build, runtime, routing, authentication/session bridge, static serving, development workflow, generated type contracts, testing tooling, and migration guardrails needed for future React admin pages. This spec must not migrate domain pages yet. It must let engineers and reviewers open a minimal authenticated React admin app from the existing FastAPI service, verify active principal and tenant/platform scope, confirm navigation shell metadata can be fetched safely, and fall back to existing Jinja pages until domain parity exists. Prioritize non-technical administrator safety, no auth bypass, no tenant leakage, and a small reversible implementation. Acceptance criteria must require the foundation to work under both Auth0-backed auth and AUTH_MODE=local_principal."

## Clarifications

### Session 2026-05-04

- Q: What initial mount path should host the React admin foundation? -> A: `/admin/app` initially, with built assets under `/admin/static/react` (autopilot).
- Q: How should legacy admin fallbacks behave during the foundation phase? -> A: Existing Jinja admin routes remain direct, authorized, and linked as fallbacks until later parity specs retire them (autopilot).
- Q: How should session and action protection be handled? -> A: Reuse existing backend-authenticated admin requests, avoid browser-stored provider credentials, and issue server-owned CSRF/action tokens for protected React actions (autopilot).
- Q: How should browser-facing types be maintained? -> A: Generate or verify TypeScript contracts from backend schemas and fail validation on contract drift (autopilot).
- Q: Which frontend runtime and package defaults should planning use? -> A: Vite SPA mode, npm scripts/lockfile, and Node.js `>=20.19.0 <26` unless a stricter local toolchain is selected later (autopilot).
- Q: How should rollout be controlled? -> A: Keep the foundation additive and gate future domain React routes behind explicit backend-controlled feature flags (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open Authenticated React Admin Entry (Priority: P1)

An authorized platform or tenant administrator can open the new React admin entry from the existing admin service and immediately see a minimal shell that confirms their signed-in identity, active scope, and safe links back to existing admin pages.

**Why this priority**: The foundation has no value unless reviewers can prove the new entry point is authenticated, scoped, and reversible before domain pages move.

**Independent Test**: Can be tested by signing in as an authorized principal, opening the new admin app entry, and verifying the page shows only safe principal, tenant/platform scope, version, and fallback navigation information.

**Acceptance Scenarios**:

1. **Given** an authorized Auth0-backed administrator with an active tenant scope, **When** they open the React admin entry, **Then** the app loads through the existing admin service and displays their safe principal summary, active tenant/platform scope, and non-domain fallback links.
2. **Given** an authorized local-principal administrator in `AUTH_MODE=local_principal`, **When** they open the React admin entry during QA, **Then** the same authenticated shell and scope summary are available without any production auth shortcut.
3. **Given** a principal without admin access, **When** they request the React admin entry or bootstrap data, **Then** the request fails closed using existing authorization behavior and does not disclose cross-tenant metadata.

---

### User Story 2 - Fetch Safe Bootstrap And Navigation Metadata (Priority: P2)

An engineer or reviewer can verify that the browser receives only explicit, redaction-safe bootstrap metadata owned by the backend, including session state, scope choices, feature flags, app version, and authorized navigation destinations.

**Why this priority**: Future React screens must consume backend-owned contracts instead of copying authorization or domain rules into the browser.

**Independent Test**: Can be tested by requesting the bootstrap and navigation metadata as authorized and unauthorized principals and comparing the returned safe fields, tenant filters, and denied responses.

**Acceptance Scenarios**:

1. **Given** an authorized principal with platform access, **When** the React app requests bootstrap metadata, **Then** it receives only safe identity, platform/tenant scope, feature flag, version, and navigation records permitted for that principal.
2. **Given** an authorized tenant-scoped principal, **When** the React app requests navigation metadata, **Then** platform-only destinations are omitted and tenant-scoped destinations preserve the selected tenant context.
3. **Given** a missing, expired, or malformed session, **When** bootstrap metadata is requested, **Then** the response is a safe denied or unauthenticated result without raw stack traces, raw claims, secrets, prompts, memory content, provider payloads, or private channel data.

---

### User Story 3 - Use Reversible Migration Guardrails (Priority: P3)

Administrators and reviewers can continue using existing Jinja admin pages while the React foundation is present, and domain React routes remain disabled unless a later feature explicitly enables them.

**Why this priority**: The migration must be additive so the current admin workflows remain stable until later specs prove parity.

**Independent Test**: Can be tested by opening existing Jinja routes after the React foundation is enabled, checking fallback links from the React shell, and verifying attempted future domain React routes do not replace current pages.

**Acceptance Scenarios**:

1. **Given** the React foundation is enabled, **When** a user opens an existing Jinja admin route, **Then** the current route remains available and authorized as before.
2. **Given** a future domain React route has no completed migration flag, **When** a user attempts to open it, **Then** the system presents a safe fallback or not-found state and points to the existing authorized Jinja destination where appropriate.
3. **Given** the React build or manifest is unavailable in a non-development environment, **When** an administrator opens the entry, **Then** the service fails safely with a reviewer-actionable message and does not expose filesystem paths, stack traces, or raw configuration.

### Edge Cases

- The active tenant scope is missing, inactive, or no longer granted to the principal.
- A principal has multiple tenant memberships plus platform roles, and navigation visibility must reflect the selected scope.
- Browser requests ask for another tenant's navigation, bootstrap, assets, or scope metadata.
- Static asset manifest entries are missing, stale, or malformed.
- Development asset serving is unavailable while the backend service remains healthy.
- Generated contracts drift from backend response schemas.
- Feature flags are disabled, unknown, or inconsistent between bootstrap metadata and route handling.
- Existing Jinja admin routes must continue to work during React app errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a minimal authenticated React admin entry point mounted separately from existing domain admin routes.
- **FR-002**: The React admin entry point MUST be reachable from the existing FastAPI admin service without migrating any domain page in this spec.
- **FR-003**: The system MUST preserve existing Jinja admin routes and authorized direct access as fallbacks until later migration parity work explicitly retires them.
- **FR-004**: The system MUST expose a backend-owned bootstrap contract containing only redaction-safe principal, active scope, available scopes, navigation, feature flag, version, and health metadata needed by the minimal React shell.
- **FR-005**: The bootstrap contract MUST be generated or otherwise verifiably synchronized with backend response schemas so browser types do not become hand-maintained sources of truth.
- **FR-006**: Bootstrap, navigation, shell, and asset-manifest requests MUST use existing authentication, authorization, tenant-scope, and audit rules and MUST fail closed when those checks cannot be proven.
- **FR-007**: The feature MUST work under Auth0-backed authentication and under explicit `AUTH_MODE=local_principal` test mode, with both modes proving principal resolution, scope handling, denied access, and protected route behavior.
- **FR-008**: The React foundation MUST include an explicit migration guardrail that keeps future domain routes behind backend-controlled feature flags until their owning specs are implemented.
- **FR-009**: The React shell MUST provide safe fallback links to existing authorized Jinja destinations and MUST avoid exposing raw IDs, raw claims, raw prompts, raw completions, raw memory content, private channel messages, raw provider responses, raw credential values, raw tool payloads, raw test transcripts, or raw stack traces.
- **FR-010**: The system MUST define local development and production asset behavior so development can use a local frontend workflow while production serves built assets through the backend-controlled admin service under `/admin/static/react`.
- **FR-011**: The foundation MUST include automated unit, contract, backend route, and browser smoke validation covering the minimal shell, bootstrap metadata, navigation visibility, denied access, static assets, and fallback behavior.
- **FR-012**: The feature MUST produce QA documentation, a manual UI walkthrough, reviewer notes, and quickstart updates that explain how to validate both authentication modes without real provider, Telegram, credential, connector, or external tool calls.
- **FR-013**: Protected React actions MUST use server-owned CSRF/action tokens or equivalent backend-issued action protection and MUST NOT store provider credentials or raw identity tokens in browser-managed application state.

### Key Entities

- **React Admin Entry**: The separate admin app entry surface that hosts the minimal authenticated shell and future React routes.
- **Admin Bootstrap Metadata**: Redaction-safe session, principal, active scope, available scope, navigation, feature flag, version, and health data returned to the browser.
- **Admin Scope Summary**: The selected tenant or platform context plus permitted scope choices that the principal may use.
- **Navigation Destination**: A backend-authorized route record used to render React shell links and fallbacks without leaking unauthorized pages.
- **Migration Guardrail**: Backend-controlled enablement state that determines whether future React domain routes are visible, routable, or redirected to Jinja fallbacks.
- **Asset Manifest Summary**: Safe metadata describing built React assets and versions without exposing local filesystem paths or raw configuration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of authorized Auth0-backed and local-principal smoke flows can open the React admin entry, view safe principal and scope metadata, and return to an existing Jinja admin page.
- **SC-002**: 100% of unauthorized or cross-tenant bootstrap, navigation, and shell requests fail closed without exposing restricted tenant data, raw claims, secrets, private content, or stack traces.
- **SC-003**: Generated or synchronized browser-facing types match the backend bootstrap contract in automated validation before the feature is considered complete.
- **SC-004**: Existing Jinja admin route tests and smoke checks continue to pass with the React foundation enabled.
- **SC-005**: Browser smoke validation captures evidence for the minimal React shell in local-principal mode, including authenticated load, safe scope display, fallback navigation, and a denied-access case.
- **SC-006**: Relevant changed backend and frontend code meets the repository's 90 percent coverage expectation or documents an approved waiver in reviewer notes.

## Assumptions

- The initial React entry is mounted at `/admin/app`, while current Jinja routes remain directly accessible at their existing paths.
- Production authentication remains Auth0-backed, and local-principal mode remains explicit for development and deterministic QA.
- The backend remains authoritative for principal, scope, navigation, feature flag, and contract data.
- Vite SPA development assets are used only for local development, and built assets are served by FastAPI under `/admin/static/react` in production-like runs.
- The frontend package workflow uses npm and a checked lockfile for Spec 026 because the repository has no existing Node package manager lockfile.
- The frontend Node.js policy targets Vite-compatible runtimes `>=20.19.0 <26`; local newer Node versions must be pinned or documented before validation if tooling rejects them.
- Future domain pages are out of scope for Spec 026 and will be enabled only by later specs in the React UI roadmap.
- No real Auth0, Telegram, model provider, credential, connector, or external tool calls are required for this feature's local and CI validation.
