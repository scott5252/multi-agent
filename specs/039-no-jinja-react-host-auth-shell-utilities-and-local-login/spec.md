# Feature Specification: No-Jinja React Host, Auth, Shell Utilities, And Local Login

**Feature Branch**: `codex/039-no-jinja-react-host-auth-shell-utilities-and-local-login`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for replacing the remaining Jinja app host, auth/local-login page, admin shell utility pages, saved-filter pages, shell fallback pages, and unavailable/error pages with React or non-Jinja static responses. The feature must remove server-side Jinja rendering from the admin entry path while preserving Auth0 and local-principal behavior, active scope, navigation, command/search, saved filters, denied states, safe redirects, CSRF or action-token behavior, and rollback guidance."

## Clarifications

### Session 2026-05-06

- Q: How should FastAPI serve the React app host without TemplateResponse? → A: Serve the built Vite index or a minimal Python-generated HTML response with safe asset manifest handling, CSP/cache headers, and no Jinja template rendering. (autopilot)
- Q: Should local-login become a React route or plain compatibility page? → A: Use a React/local-auth route backed by server-owned JSON contracts for local-principal selection, action tokens, session creation, audit, and redirects; disabled modes return a non-Jinja safe problem. (autopilot)
- Q: How are Auth0 redirects preserved? → A: Keep Auth0 decisions server-owned, allow only safe admin return URLs, preserve authorized requested destinations, and fail closed on unsafe or cross-tenant redirect intent. (autopilot)
- Q: Where should saved-filter and shell utilities move? → A: Move saved-filter management, scope switching, breadcrumbs, command/search, denied, unavailable, and mutation result presentation into React or non-Jinja compatibility responses using backend-owned contracts. (autopilot)
- Q: What happens to old `/admin` and shell utility URLs? → A: Redirect `/admin` and redirectable shell URLs to `/admin/app` or the closest React route while preserving tenant, route, filter, and saved-filter intent; otherwise return a documented non-Jinja retirement/problem response. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter Admin Through A Non-Jinja React Host (Priority: P1)

Administrators need every admin entry URL to reach the React application without server-side Jinja rendering while preserving authentication, active tenant scope, navigation, breadcrumbs, command/search, unavailable states, and safe direct-link behavior.

**Why this priority**: The admin entry path is the root of the Jinja retirement sequence. Removing the app host and shell fallback templates safely proves that React is the authoritative admin browser surface before domain-specific templates are retired.

**Independent Test**: Request `/admin`, `/admin/app`, representative `/admin/app/*` direct links, and shell utility URLs as Auth0-shaped and local-principal users; verify responses are React/static, redirect, or non-Jinja compatibility responses with no TemplateResponse rendering.

**Acceptance Scenarios**:

1. **Given** an authenticated platform admin opens `/admin/app`, **When** the admin host responds, **Then** the user receives the React shell with authorized navigation, active scope, saved-filter affordances, breadcrumbs, and command/search without server-side Jinja rendering.
2. **Given** an authenticated tenant admin opens `/admin` or an old admin shell utility URL with query filters, **When** the route is handled, **Then** the response safely redirects to the equivalent React route while preserving tenant scope and safe query intent.
3. **Given** an unauthenticated user opens an admin browser URL, **When** authentication is required, **Then** Auth0 production redirect behavior and local-principal login behavior remain server-owned and do not reveal tenant data.

---

### User Story 2 - Complete Local Login Without Jinja (Priority: P2)

Local QA reviewers and developers need the local-principal login experience to move off `auth/local_login.html` while still exercising the same backend authentication, role, tenant, CSRF/action-token, and audit behavior used by the existing test mode.

**Why this priority**: Every later Playwright validation depends on deterministic local login. Jinja removal cannot proceed if the test authentication path still relies on a template or bypasses server-owned decisions.

**Independent Test**: Run local-principal browser flows for platform admin, tenant admin, and user principals; verify login, denied login, logout, and post-login redirects through backend JSON contracts or non-Jinja responses.

**Acceptance Scenarios**:

1. **Given** local-principal auth mode is enabled, **When** a reviewer selects a platform-admin principal and submits login, **Then** the backend grants the expected session, records safe audit evidence, and redirects to the requested React route.
2. **Given** a user selects a tenant-scoped principal, **When** login completes, **Then** the React shell shows only authorized tenant scope and navigation destinations.
3. **Given** an invalid local-principal request or missing action token, **When** login is submitted, **Then** the response fails closed with a redaction-safe non-Jinja problem state.

---

### User Story 3 - Manage Shell Utilities And Saved Filters In React (Priority: P3)

Admins need saved-filter management, scope switching, unavailable/denied pages, flash or mutation results, and shell utility pages to be available from React or non-Jinja compatibility responses after the shell templates are removed.

**Why this priority**: Shell utility pages are shared dependencies for every migrated admin workspace. They must preserve existing repeated workflows and error handling before legacy templates can be deleted.

**Independent Test**: Exercise saved-filter list/create/update/delete flows, scope switching, unavailable route behavior, denied route behavior, and mutation-result messaging in React with backend route tests and browser QA.

**Acceptance Scenarios**:

1. **Given** an authenticated admin has saved filters, **When** they open the React saved-filter management surface, **Then** they can view, create, update, and delete filters through backend-owned contracts without Jinja.
2. **Given** a user lacks access to a requested shell destination, **When** they open the old URL or React route, **Then** the response shows a safe denied state without exposing unauthorized tenant labels or resource existence.
3. **Given** a backend dependency is unavailable, **When** the admin shell cannot load a required bootstrap contract, **Then** the browser receives a non-Jinja unavailable response or React fallback that contains only safe diagnostic text and a rollback path.

### Edge Cases

- The built React asset manifest is missing, stale, or unavailable during local development.
- A legacy `/admin` or shell utility URL includes route parameters, filters, saved-filter identifiers, or a next URL.
- Auth0 production mode needs to preserve an intended admin return URL without accepting unsafe open redirects.
- Local-principal auth mode is disabled in a production-shaped environment.
- A saved-filter mutation is submitted with an expired or missing CSRF/action token.
- A tenant-scoped user requests platform-only shell utilities or platform-only saved filters.
- A denied or unavailable state must not reveal whether a tenant, saved filter, workflow, provider, skill, prompt, run, or membership exists.
- A legacy static asset is still referenced by React-compatible code or docs.
- Browser refreshes on deep React routes must return the React host without TemplateResponse.
- Rollback guidance is needed if the React host assets fail after the templates are removed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST serve the admin React application host without server-side Jinja rendering for `/admin/app` and deep React admin routes.
- **FR-002**: The system MUST redirect `/admin` and old admin shell utility URLs to authorized React destinations or return documented non-Jinja compatibility responses when a redirect cannot preserve behavior safely.
- **FR-003**: Redirects from legacy admin shell URLs MUST preserve tenant id, route parameters, query filters, saved-filter intent, safe breadcrumbs, and requested return destination when doing so is unambiguous and authorized.
- **FR-004**: The system MUST preserve Auth0 production authentication behavior, including safe return URLs, denied states, logout behavior, and fail-closed handling.
- **FR-005**: The system MUST provide a non-Jinja local-principal login flow for local and CI QA that uses backend-owned contracts for principal selection, action tokens, session creation, authorization, audit, and redirect decisions.
- **FR-006**: Local-principal login MUST support platform-admin, tenant-admin-acme, and user principals needed by browser QA without requiring real Auth0, provider, Telegram, credential, or connector calls.
- **FR-007**: Saved-filter listing, creation, update, deletion, and navigation entry points MUST be available through React or backend JSON contracts after the shell saved-filter templates are removed.
- **FR-008**: Scope selector, navigation, breadcrumbs, command/search, mutation result, flash-message equivalent, denied, and unavailable shell states MUST be available through React or non-Jinja compatibility responses.
- **FR-009**: Backend contracts MUST own authorization, tenant scope, validation, CSRF/action-token validation, redaction, and audit decisions for all auth and shell utility behavior.
- **FR-010**: React UI, redirects, non-Jinja responses, screenshots, QA docs, logs, and exports MUST NOT expose raw secrets, credential values, provider authorization headers, private channel messages, raw prompts or completions, memory contents, raw run payloads, raw tool payloads, raw test transcripts, full Telegram identifiers, link tokens after creation, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-011**: The system MUST test Auth0-shaped principal behavior through backend route tests and local-principal behavior through Playwright browser flows.
- **FR-012**: The system MUST prove that admin entry routes, local-login routes, shell utility routes, unavailable routes, and saved-filter routes no longer return TemplateResponse or depend on Jinja templates.
- **FR-013**: The implementation MUST delete or retire only the shell/auth templates and Jinja-only static assets whose deletion-grade parity is proven by Spec 039 evidence.
- **FR-014**: The implementation MUST retain API and JSON routes used by React and MUST NOT remove the global Jinja dependency or shared template infrastructure before Spec 047.
- **FR-015**: The migration dashboard or reviewer evidence MUST record which Spec 039 inventory items were deleted, redirected, converted, retained, or blocked, with evidence references and rollback guidance.
- **FR-016**: QA artifacts MUST document local setup, deterministic seed data, Auth0-shaped backend tests, local-principal browser flows, denied/unauthorized checks, redaction checks, direct-link redirects, saved-filter checks, and rollback steps.

### Key Entities *(include if feature involves data)*

- **React Admin Host Response**: A non-Jinja browser response that serves the admin React app, asset references, bootstrap hints, cache headers, and safe unavailable fallback behavior.
- **Local Login Contract**: Backend-owned data and actions that present selectable local principals, issue or validate action tokens, create test sessions, and return safe redirect decisions.
- **Shell Redirect Plan**: A mapping from an old admin shell or utility URL to a React destination, alias, or non-Jinja compatibility response with preservation and authorization rules.
- **Saved Filter Interaction**: Tenant-scoped saved-filter data and mutation results exposed through React-compatible backend contracts.
- **Retirement Evidence Record**: Reviewer-facing evidence that an inventoried template, route, or static asset was safely deleted, converted, retained, or blocked in Spec 039.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Spec 039 shell/auth inventory items are classified after implementation as deleted, redirected, converted to non-Jinja, retained with blocker, or outside active scope with evidence references.
- **SC-002**: 0 admin entry, local-login, saved-filter, shell utility, unavailable, or denied browser routes in Spec 039 return TemplateResponse in backend route tests.
- **SC-003**: Auth0-shaped backend tests cover allowed, unauthenticated, unauthorized, cross-tenant, safe return URL, and logout cases for changed admin/auth routes.
- **SC-004**: Local-principal Playwright flows prove platform-admin, tenant-admin-acme, and user login paths can reach authorized React destinations and capture redaction-safe evidence.
- **SC-005**: Saved-filter React flows cover list, create, update, delete, redirect preservation, validation failure, and denied states without Jinja templates.
- **SC-006**: Browser refreshes on `/admin/app` and representative deep React routes load the React host within existing local QA performance budgets and without template imports.
- **SC-007**: Redaction sweeps over QA docs, screenshots, route responses, and reviewer notes find 0 raw secrets, credential values, raw private payloads, local filesystem paths, stack traces, or unauthorized tenant labels.
- **SC-008**: QA docs and reviewer notes let a reviewer reproduce the no-Jinja host, local-login, shell redirect, and saved-filter evidence within 15 minutes.

## Assumptions

- Static Vite-built HTML or a minimal Python-generated HTML string is acceptable because the removal target is server-side Jinja rendering.
- Existing React shell, navigation, scope, command/search, saved-filter, and migration-hardening patterns from Specs 026 through 038 remain the preferred UX and contract baseline.
- Local-principal authentication remains limited to explicit local/CI configuration and must be impossible to enable accidentally in production.
- Spec 039 owns shell/auth host templates and shell utility redirects, while domain-specific admin templates are retired by Specs 040 through 046.
- Spec 039 does not remove `jinja2`, global template providers, or shared template infrastructure; Spec 047 owns final dependency and infrastructure decommissioning.
- Real Auth0, provider, Telegram, credential, connector, and external tool calls remain out of scope for validation; deterministic mocks and local principals are required.
