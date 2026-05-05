# Feature Specification: React Admin Migration Hardening And Jinja Retirement

**Feature Branch**: `codex/037-react-admin-migration-hardening-and-jinja-retirement`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for React Admin Migration Hardening and Jinja Retirement. After the React domain specs reach parity, the platform needs a safe final migration that verifies every admin destination has an authorized React path, preserves direct links or redirects, retires duplicated legacy UI only where parity is proven, documents rollback behavior, validates performance and accessibility, and updates reviewer/operator guidance. The feature must be cautious, auditable, and reversible."

## Clarifications

### Session 2026-05-05

- Q: Which legacy Jinja routes can be retired immediately? → A: Only routes with parity matrix approval, dual-auth validation, redaction evidence, tenant-isolation evidence, accessibility evidence, and rollback instructions; read-only fallbacks remain for two releases by default. (autopilot)
- Q: How should old direct links behave after primary navigation moves to React? → A: Primary navigation targets React, while old direct links preserve route parameters, tenant scope, and query filters through authorized redirects, aliases, or retained fallback pages with migration notices. (autopilot)
- Q: What are the migration feature flag defaults? → A: React primary routing is enabled for QA037 validation, legacy deletion is disabled by default, and rollback must be possible by flag plus previous React asset version. (autopilot)
- Q: What visual, browser, and accessibility coverage is required? → A: Cover major Specs 026-036 admin journeys in Chromium local QA across desktop and mobile-sized viewports, with no critical WCAG-oriented keyboard, focus, label, landmark, contrast-sensitive state, or text-overlap defects. (autopilot)
- Q: What performance budgets should gate migration acceptance? → A: Route bootstrap should complete within 500 ms in deterministic local QA, primary admin journeys should become interactive within 2 seconds, and compressed React assets should stay within the documented budget or carry explicit mitigation notes. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify Admin Route Parity And Safe Navigation (Priority: P1)

Platform operators and tenant administrators need confidence that every primary admin destination has an authorized React path, direct links remain usable, and navigation changes do not bypass authentication, tenant scope, audit, or redaction controls.

**Why this priority**: Route parity and safe navigation are the minimum conditions for completing the React migration. Without this proof, retiring or redirecting legacy pages would risk broken operator workflows or protected-data exposure.

**Independent Test**: Review the migration parity matrix, open every primary admin destination as platform-admin and tenant-admin-acme, verify the React route or approved fallback, and confirm denied unauthenticated and cross-tenant access still fails closed.

**Acceptance Scenarios**:

1. **Given** the current admin destination inventory, **When** a platform administrator opens each primary admin journey, **Then** an authorized React path, documented fallback, or explicit non-migrated exception is present.
2. **Given** a tenant administrator opens tenant-scoped admin journeys, **When** they use React navigation or an old direct link, **Then** they remain limited to their tenant and cannot see platform-only or other-tenant data.
3. **Given** an unauthenticated browser requests a retired, redirected, or React primary admin route, **When** the route resolves, **Then** authentication is required before any protected page data is returned.
4. **Given** a route has not met parity criteria, **When** migration hardening is applied, **Then** the legacy route remains available as an authorized fallback with a clear migration status.

---

### User Story 2 - Retire Or Redirect Legacy UI Cautiously (Priority: P2)

Platform operators need duplicated legacy UI retired only where React parity is proven, while direct links, bookmarks, and operational runbooks continue to work through redirects, aliases, or deprecation notices.

**Why this priority**: The migration should reduce duplicated UI maintenance, but premature removal would make production support brittle. Retirement must be reversible and auditable.

**Independent Test**: Select a route that meets retirement criteria, open its legacy direct URL, verify it redirects or aliases to the React destination with safe status and audit evidence, then disable the migration flag and confirm rollback returns to the approved fallback.

**Acceptance Scenarios**:

1. **Given** a legacy admin route has approved parity evidence, **When** the direct legacy URL is opened, **Then** it redirects or aliases to the React route without losing scope, query filters, breadcrumbs, or safe status messaging.
2. **Given** a legacy route lacks full parity, **When** hardening is applied, **Then** the route stays available and documents why it remains a fallback.
3. **Given** rollback is requested, **When** the configured migration flag or asset version is reverted, **Then** operators can reach the previously approved fallback without a code emergency.
4. **Given** an administrator follows an old bookmark, **When** the route redirects, **Then** the system records migration-safe audit or trace evidence without logging private payloads.

---

### User Story 3 - Validate Performance, Accessibility, Visual Stability, And Guidance (Priority: P3)

Reviewers and operators need measurable performance, accessibility, visual-regression, redaction, tenant-isolation, and documentation evidence before the final migration is accepted.

**Why this priority**: React parity is not just route coverage. The final migration must be usable, understandable, responsive, accessible, and documented well enough for support staff to recover quickly.

**Independent Test**: Run the final admin journey suite, accessibility checks, bundle/performance checks, visual screenshots, redaction scans, tenant-isolation sweep, QA docs, and rollback runbook review, then confirm all evidence paths are recorded.

**Acceptance Scenarios**:

1. **Given** the final migration is ready for review, **When** the admin journey suite runs, **Then** screenshots and route checks cover all major React-admin journeys from Specs 026 through 036.
2. **Given** the React shell and migrated workspaces are opened on supported viewports, **When** accessibility and visual checks run, **Then** no critical keyboard, landmark, contrast, text-overlap, or blank-screen issues remain.
3. **Given** generated contract and bundle checks run, **When** the validation completes, **Then** type contracts are current and bundle/performance budgets are within documented thresholds or have explicit mitigation notes.
4. **Given** reviewers inspect QA evidence, **When** they run the redaction and tenant-isolation sweeps, **Then** no raw secrets, private data, local paths, or unauthorized tenant labels appear in JSON evidence, screenshots, docs, or exports.

### Edge Cases

- A legacy route has a React equivalent but old bookmarks include query filters, tenant ids, or saved-filter state.
- A route appears in navigation but is intentionally kept as Jinja fallback for two-release soak time.
- A platform-only React destination is requested by a tenant administrator.
- A tenant-scoped redirect is requested without a tenant id.
- React assets fail to load after deployment.
- Generated React contract output is stale compared with backend schemas.
- A route passes happy-path browser validation but fails keyboard-only navigation.
- A screenshot captures a hidden field, old flash message, unsafe token label, or unauthorized tenant label.
- Bundle size or route bootstrap time exceeds the documented budget.
- An operator needs to roll back only the admin UI while keeping backend domain services active.
- A browser opens an old route during rollback while a newer React asset manifest is cached.
- A direct route cannot be retired because it serves a non-React workflow not yet represented in the parity matrix.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain a complete admin destination parity matrix covering primary routes, direct links, protected JSON endpoints, role scope, tenant scope, fallback status, retirement status, and validation evidence.
- **FR-002**: The system MUST classify each legacy admin route as React primary, redirect/alias to React, retained fallback, or explicitly out of scope with a documented reason.
- **FR-003**: The system MUST keep legacy direct links usable through authorized redirects, aliases, or retained fallbacks unless retirement criteria are fully met.
- **FR-004**: The system MUST preserve query filters, tenant scope, route parameters, saved-filter intent, and safe breadcrumbs when redirecting or aliasing old admin routes.
- **FR-005**: The system MUST require authentication and authorization for every React route, redirect route, retained fallback, and protected admin JSON endpoint.
- **FR-006**: The system MUST fail closed when route parity, tenant scope, role authorization, audit persistence, or redaction safety cannot be proven.
- **FR-007**: The system MUST provide rollback behavior based on documented migration flags and asset-version procedures.
- **FR-008**: The system MUST document which legacy templates, static assets, and route handlers are retired, retained, or intentionally untouched.
- **FR-009**: The system MUST retire or disable duplicated legacy UI only for routes that have approved parity evidence, dual-auth validation, redaction evidence, tenant-isolation evidence, and rollback instructions.
- **FR-010**: The system MUST avoid deleting any legacy UI needed for support, fallback, direct-link compatibility, or unproven admin journeys.
- **FR-011**: The system MUST validate the React admin shell and migrated workspaces under both Auth0-backed production-style principals and `AUTH_MODE=local_principal`.
- **FR-012**: The system MUST include local-principal browser validation for primary admin journeys and backend route tests for Auth0-shaped principal behavior.
- **FR-013**: The system MUST provide visual screenshot evidence for major admin journeys from Specs 026 through 036.
- **FR-014**: The system MUST validate keyboard navigation, focus management, landmarks, labels, contrast-sensitive states, and text non-overlap across supported desktop and mobile viewports.
- **FR-015**: The system MUST validate documented performance budgets for route bootstrap time, React asset size, major admin journey responsiveness, and bounded table or diagnostic rendering.
- **FR-016**: The system MUST validate generated frontend contracts are current with backend-owned schemas.
- **FR-017**: The system MUST run a migration-wide redaction sweep over JSON evidence, screenshots, exports, docs, and reviewer artifacts.
- **FR-018**: The system MUST run a tenant-isolation sweep proving platform-only data, tenant-scoped data, and user-scoped data remain separated across redirects and React routes.
- **FR-019**: The system MUST update reviewer, operator, rollback, README, quickstart, and QA guidance for the final admin migration state.
- **FR-020**: The system MUST record migration decisions and validation outcomes in auditable PR notes or reviewer notes.
- **FR-021**: The system MUST preserve existing backend domain behavior and data contracts while changing only route ownership, navigation, rendering, fallback, documentation, and proven-obsolete UI assets.
- **FR-022**: The system MUST not expose raw secrets, credential values, provider authorization headers, raw prompts, raw completions, raw memory content, raw run payloads, raw tool payloads, private channel messages, raw package payloads, raw test transcripts, private briefing preference values, full Telegram identifiers, link tokens after creation, local filesystem paths, stack traces, or unauthorized tenant labels in any migration evidence or UI.

### Key Entities

- **Admin Destination Inventory**: The authoritative list of admin routes, JSON endpoints, direct links, navigation entries, protected surfaces, roles, tenant-scope behavior, fallback status, and owner notes.
- **Parity Matrix Entry**: A route-level decision that records React destination, legacy destination, redirect behavior, fallback status, retirement eligibility, validation evidence, and rollback note.
- **Migration Route Decision**: The chosen behavior for a legacy route, such as redirect, alias, retained fallback, deprecation notice, or no-op.
- **Rollback Plan**: The operator-facing procedure for reverting route ownership, React asset version, feature flags, and direct-link behavior.
- **Validation Evidence Set**: The grouped screenshots, curl outputs, accessibility checks, performance measurements, contract checks, redaction scans, tenant-isolation scans, and reviewer notes used to approve migration status.
- **Legacy Asset Decision**: The record that explains whether a template, static file, or small script is retired, retained for fallback, or retained because another journey still depends on it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of primary admin destinations have a parity matrix entry with React path, fallback decision, authorization scope, and validation evidence.
- **SC-002**: 100% of retired or redirected legacy routes preserve authentication, tenant scope, important query state, and direct-link usability.
- **SC-003**: 0 legacy routes are deleted or disabled without approved parity evidence and rollback documentation.
- **SC-004**: Platform admin, tenant admin, and tenant user journeys complete in the final browser suite without critical navigation, authorization, or blank-screen failures.
- **SC-005**: Accessibility checks report no critical keyboard, label, landmark, focus, contrast-sensitive state, or text-overlap defects across the covered admin journeys.
- **SC-006**: Route bootstrap and bundle evidence meet documented budgets, or every exception has an explicit mitigation and approval note.
- **SC-007**: Redaction scans across QA evidence, screenshots, docs, exports, and reviewer artifacts find 0 unsafe secret, private payload, local path, or unauthorized tenant markers.
- **SC-008**: Tenant-isolation checks prove Acme tenant principals cannot access Globex or platform-only data across React paths, redirects, and retained fallbacks.
- **SC-009**: Rollback instructions allow an operator to identify the flag, asset version, and fallback route behavior in under 10 minutes.
- **SC-010**: Reviewer documentation lets a new reviewer reproduce the final migration QA flow without private credentials or live external services.

## Assumptions

- Specs 026 through 036 remain available as the parity source for migrated React admin domains.
- Direct deletion is the exception; redirect, alias, retained fallback, or deprecation notice is preferred until evidence proves safe retirement.
- Local QA continues to use deterministic local-principal users, Acme and Globex tenants, fake secret references, and mock-safe external boundaries.
- Production authentication remains Auth0-backed; local-principal mode remains explicit for local and CI validation.
- Rollback can be handled through existing configuration, feature flags, route selection, and React asset version control without reverting backend domain data.
- Existing backend services, authorization policies, tenant guards, audit helpers, redaction helpers, and domain contracts remain authoritative.
