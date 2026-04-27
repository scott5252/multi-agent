# Feature Specification: Admin Console Shell

**Feature Branch**: `010-admin-console-shell`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: User description: "Add a shared admin console shell for the multi-agent platform. The shell must provide platform and tenant admin navigation, tenant scope display, authorization-aware menu items, common page layout, shared error and empty states, safe flash messages, breadcrumbs, saved filters where useful, and links to existing workflow, model-skill, run inspection, and reliability pages. It must remain server-rendered with Jinja templates and small JavaScript files under the existing web_admin structure. The shell must not replace existing routes; it must wrap and organize them. Require platform-admin and tenant-admin behavior to be explicit, denied navigation to fail closed, access decisions to be audited, at least 90 percent coverage for submitted code, docs, PR review notes, testing instructions, and README updates."

## Clarifications

### Session 2026-04-27

- Q: What audit record granularity should the admin shell use for navigation visibility and access decisions? → A: Per-request/scope evaluation with item-level navigation outcomes, plus separate records for direct destination access, scope selection, and filter restoration.
- Q: How should the shell carry active tenant scope across links, forms, and bookmarked admin pages? → A: Use a validated `tenant_id` query parameter on shell links and forms; platform scope omits `tenant_id`.
- Q: How should useful saved filters be stored and restored for the admin shell? → A: Persist saved filters server-side, scoped by user, admin area, and platform or tenant scope, after validating each criterion.
- Q: Which existing admin pages must the first shell delivery wrap? → A: Wrap all existing server-rendered `web_admin` UI pages for workflows, model-skill, run inspection, and reliability; original UI routes remain direct and authorized.
- Q: What should happen when an admin access decision is computed but audit persistence is unavailable? → A: Fail closed: show a safe unavailable state, block the destination or action, and emit operational log/metric evidence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate By Admin Scope (Priority: P1)

As a platform administrator or tenant administrator, I need the admin console to show my current scope, available destinations, and permitted actions so that I can navigate the platform without guessing which tenant or authority level I am using.

**Why this priority**: Correct scope and authorization-aware navigation are the foundation of a shared admin shell. Without them, administrators may act in the wrong tenant, see unavailable links, or rely on unclear access behavior.

**Independent Test**: Can be fully tested by signing in as a platform administrator, a tenant administrator for one tenant, a tenant administrator for multiple tenants, and an unauthorized user, then confirming each user sees the correct scope display, navigation, and fail-closed access behavior.

**Acceptance Scenarios**:

1. **Given** a platform administrator has global administrative authority, **When** they open the admin console, **Then** the shell identifies platform scope and shows platform-level destinations and tenant-scoped destinations that the user is authorized to enter.
2. **Given** a tenant administrator has authority for one tenant, **When** they open the admin console, **Then** the shell identifies that tenant as the active scope and shows only destinations and actions available within that tenant.
3. **Given** a tenant administrator has authority for multiple tenants, **When** they switch active tenant scope, **Then** the scope display, navigation, breadcrumbs, saved filters, and page links update to the selected tenant without carrying over unauthorized tenant data.
4. **Given** a user lacks authority for a destination, **When** the shell evaluates navigation, **Then** the destination is unavailable in navigation and any direct request fails closed without exposing protected details.
5. **Given** access decisions allow, deny, or cannot safely determine access for admin destinations, **When** navigation visibility is evaluated, **Then** one audit record per request and active scope captures item-level navigation outcomes with actor, role context, scope, destination, outcome, reason category, and time.
6. **Given** an admin access decision is computed but required audit evidence cannot be persisted, **When** the shell would otherwise render a protected destination or perform an admin action, **Then** the shell fails closed with a safe unavailable state, blocks the destination or action, and emits operational log and metric evidence.

---

### User Story 2 - Use A Consistent Console Layout (Priority: P2)

As an administrator moving between workflow, model-skill, run inspection, and reliability pages, I need a consistent page frame with navigation, breadcrumbs, content area, and status messaging so that every admin surface feels like part of one console.

**Why this priority**: Existing admin pages already solve important tasks, but administrators need a coherent way to find them, understand where they are, and recover from errors without each page inventing its own surrounding experience.

**Independent Test**: Can be fully tested by visiting all existing server-rendered `web_admin` UI pages for workflow, model-skill, run inspection, and reliability through the shell and by direct route, then confirming the same underlying page purpose remains available with a shared frame and no route replacement.

**Acceptance Scenarios**:

1. **Given** existing workflow administration pages are available, **When** an authorized administrator opens the shell, **Then** workflow navigation links take the administrator to those existing pages without replacing their routes.
2. **Given** existing model-skill configuration, history, and run-provenance pages are available, **When** an authorized administrator opens the shell, **Then** model-skill navigation links take the administrator to those existing pages without replacing their routes.
3. **Given** existing run inspection, run detail, and replay pages are available, **When** an authorized administrator opens the shell, **Then** run inspection navigation links take the administrator to those existing pages without replacing their routes.
4. **Given** existing reliability control, breaker, and dead-letter pages are available, **When** an authorized administrator opens the shell, **Then** reliability navigation links take the administrator to those existing pages without replacing their routes.
5. **Given** an administrator lands on an admin page through a previously bookmarked route, **When** the route is still valid, **Then** the existing route remains usable and is organized by the shared shell where authorization permits.
6. **Given** a shell link, form submission, or bookmarked admin page carries an active tenant scope, **When** the request is handled, **Then** the shell validates the `tenant_id` query parameter against the administrator's authority before rendering or performing tenant-scoped actions; platform-scope requests omit `tenant_id`.
7. **Given** an existing server-rendered `web_admin` UI page belongs to workflow, model-skill, run inspection, or reliability administration, **When** an authorized administrator opens that page by shell navigation or its original route, **Then** the page renders inside the shared shell while preserving the original route identity and page purpose.

---

### User Story 3 - Recover From Empty, Error, And Flash States Safely (Priority: P3)

As an administrator, I need empty states, error states, and flash messages that are consistent, actionable, and safe so that I understand what happened without seeing sensitive or unauthorized information.

**Why this priority**: Admin consoles frequently show partial data, denied access, missing resources, and action confirmations. Those states must help authorized users while preserving tenant isolation and sensitive-data protections.

**Independent Test**: Can be fully tested by triggering empty lists, missing resources, denied destinations, action success messages, validation failures, and unexpected errors across shell-wrapped pages, then confirming the visible messages are useful and safe.

**Acceptance Scenarios**:

1. **Given** an authorized page has no records to show, **When** the administrator opens it, **Then** the shell displays an empty state that names the page purpose and offers a permitted next action when one exists.
2. **Given** a requested resource is missing or outside the active scope, **When** the administrator opens the page, **Then** the shell shows a safe not-found or unavailable state without revealing whether protected resources exist elsewhere.
3. **Given** an administrator is denied access to a destination or action, **When** the denial occurs, **Then** the shell shows a safe access-denied state, fails closed, and records an audit decision.
4. **Given** an admin action succeeds, fails validation, or cannot be completed, **When** a flash message is shown, **Then** the message uses safe summaries and does not reveal raw secrets, credentials, protected prompt content, unauthorized memory content, or cross-tenant details.
5. **Given** a shared state cannot be rendered completely, **When** an administrator views the page, **Then** the shell clearly distinguishes empty, denied, partial, unavailable, and unexpected-error states.

---

### User Story 4 - Resume Useful Filtered Views (Priority: P4)

As an administrator who repeatedly reviews workflow, model-skill, run, and reliability lists, I need useful filters to be remembered within the correct scope so that I can continue investigations without re-entering common criteria.

**Why this priority**: Saved filters improve repeated operational work, but they must be scoped carefully so they do not leak tenant context, stale authorization, or confusing page state.

**Independent Test**: Can be fully tested by applying filters on filterable admin pages, leaving and returning to those pages within the same admin scope, switching scope, and confirming only authorized, scope-appropriate filters are restored.

**Acceptance Scenarios**:

1. **Given** an admin page supports filtering, **When** an administrator applies filter criteria and later returns to the same page in the same scope, **Then** useful filter criteria are restored or offered for quick reuse.
2. **Given** an administrator switches active tenant scope, **When** they open a filterable page, **Then** filters from another tenant are not applied unless they are safe and meaningful for the new scope.
3. **Given** a saved filter references a destination, status, workflow, model, run, or reliability item that is no longer authorized, **When** the filter is restored, **Then** unauthorized criteria are removed or ignored and the decision is auditable when access is evaluated.
4. **Given** a page has no meaningful filters, **When** the administrator uses that page, **Then** the shell does not add unnecessary saved-filter controls.

---

### User Story 5 - Review Delivery Evidence (Priority: P5)

As a maintainer reviewing the feature, I need coverage evidence, documentation, PR review notes, testing instructions, and README guidance so that I can verify and operate the admin shell after merge.

**Why this priority**: The shell touches shared administrative behavior and authorization. Reviewers need clear evidence that navigation, scope, failure states, audit behavior, and documentation are complete.

**Independent Test**: Can be fully tested by reviewing the submitted delivery package and confirming that code coverage, docs, PR notes, testing instructions, and README updates cover the required admin shell behavior.

**Acceptance Scenarios**:

1. **Given** the feature is submitted for review, **When** maintainers inspect the delivery materials, **Then** coverage evidence demonstrates at least 90 percent coverage for submitted code.
2. **Given** the feature is submitted for review, **When** maintainers read PR review notes, **Then** the notes call out scope handling, authorization, denied navigation, audit coverage, safe messages, route preservation, saved filters, and known risks.
3. **Given** reviewers follow testing instructions, **When** they exercise the feature, **Then** they can verify platform-admin behavior, tenant-admin behavior, tenant switching, authorization-aware menus, direct-route denial, audit records, breadcrumbs, shared states, safe flash messages, saved filters, and links to existing admin pages.
4. **Given** an administrator reads the README update, **When** they need to use the console shell, **Then** the guidance explains scope display, navigation groups, saved filters, common states, safe messaging, and where existing admin pages appear.

### Edge Cases

- A user has no admin role; the shell denies access, shows no protected navigation, and audits the denied attempt.
- A user has both platform-admin and tenant-admin authority; the shell distinguishes platform scope from tenant scope and requires an explicit active scope for tenant-scoped actions.
- A tenant administrator belongs to multiple tenants; saved filters, breadcrumbs, flash messages, and navigation remain bound to the selected tenant scope.
- A selected tenant is suspended, archived, deleted, or no longer authorized while the user is active; the shell clears the invalid scope, blocks tenant-scoped destinations, and prompts for a permitted scope when one exists.
- Authorization data is missing, stale, or unavailable; navigation and direct destination access fail closed and audit the unavailable-decision category.
- Audit persistence is unavailable when an admin access decision is computed; the shell fails closed, shows a safe unavailable state, blocks protected navigation or actions, and emits operational log and metric evidence.
- A user follows an old bookmark or typed URL for an existing admin route; the route remains available only if authorized and protected by the same access decisions as shell navigation.
- A user changes or forges a `tenant_id` query parameter; the shell validates the tenant scope server-side, fails closed when unauthorized or invalid, clears unsafe scope-dependent state, and audits the decision.
- A cached or stale navigation item points to a destination that the user can no longer access; the direct request is denied safely and audited.
- A breadcrumb segment references a resource outside the active scope; the segment is redacted, omitted, or replaced with a safe unavailable label.
- A list is empty because no records exist; the empty state must not imply records exist in another tenant or hidden scope.
- A list is empty because filters are too narrow; the empty state offers safe filter-reset guidance rather than a misleading no-records message.
- A flash message is generated from user input, validation errors, or operational failures; unsafe content is removed or summarized before display.
- An unexpected error occurs during a shared shell component; the page shows a safe error state and does not disclose stack traces, secrets, tenant data, or protected identifiers.
- A saved filter references data that was deleted, archived, or no longer authorized; the filter is not allowed to reveal protected labels or counts.
- A saved filter contains a malformed, expired, unsupported, or forged criterion; the shell rejects or drops that criterion server-side before applying the filter and records any access evaluation.
- An admin page has no meaningful filters; the shell leaves it unmodified rather than forcing saved-filter behavior.
- Delivery materials omit coverage evidence, PR review notes, testing instructions, docs, or README guidance; the feature is not considered review-ready.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST provide a shared admin console shell that can organize existing administrative pages without replacing their routes or removing direct access paths that remain authorized.
- **FR-001a**: The first shell delivery MUST wrap all existing server-rendered `web_admin` UI pages for workflow administration, model-skill configuration and history, run inspection and replay, and reliability controls; original UI routes MUST remain direct and authorized.
- **FR-002**: The shell MUST preserve the underlying purpose and route identity of existing workflow administration pages while making them reachable from shared navigation.
- **FR-003**: The shell MUST preserve the underlying purpose and route identity of existing model-skill configuration, history, and run-provenance pages while making them reachable from shared navigation.
- **FR-004**: The shell MUST preserve the underlying purpose and route identity of existing run inspection, run detail, and replay pages while making them reachable from shared navigation.
- **FR-005**: The shell MUST preserve the underlying purpose and route identity of existing reliability control, breaker, and dead-letter pages while making them reachable from shared navigation.
- **FR-006**: The shell MUST expose explicit platform-admin behavior, including platform scope identification, platform-level navigation, and tenant-entry navigation only when the user is authorized.
- **FR-007**: The shell MUST expose explicit tenant-admin behavior, including active tenant scope identification, tenant-scoped navigation, and tenant-scoped action availability only when the user is authorized for the selected tenant.
- **FR-008**: The shell MUST clearly display the active administrative scope on every shell-wrapped page, distinguishing platform scope from tenant scope.
- **FR-009**: Authorized users with access to multiple tenant scopes MUST be able to identify and select the active tenant scope before performing tenant-scoped actions.
- **FR-009a**: Shell links and form submissions for tenant-scoped admin pages MUST carry the active tenant scope as a validated `tenant_id` query parameter; platform-scope admin pages MUST omit `tenant_id`.
- **FR-009b**: The shell MUST validate any supplied `tenant_id` on the server against the administrator's current authority before rendering tenant-scoped content, restoring filters, showing scope-bound messages, or performing tenant-scoped actions.
- **FR-010**: Navigation groups and menu items MUST be authorization-aware and MUST only appear as available when the user is permitted to access the destination in the active scope.
- **FR-011**: Direct requests to admin destinations MUST enforce the same authorization decisions as shell navigation and MUST fail closed when access is denied, unavailable, or indeterminate.
- **FR-012**: Navigation visibility decisions MUST be auditable as one record per request and active scope with item-level navigation outcomes; direct destination access, scope selection, and saved-filter restoration decisions MUST each create separate auditable records with actor, role context, active scope, destination or action, outcome, reason category, and time.
- **FR-012a**: If required access-decision audit evidence cannot be persisted, the shell MUST fail closed, show a safe unavailable state, block the destination or action, and emit operational log and metric evidence.
- **FR-013**: The shell MUST provide a common page layout for admin pages, including primary navigation, active scope display, breadcrumbs, message area, main content region, and consistent page actions when actions are available.
- **FR-014**: The shell MUST provide breadcrumbs that reflect the current admin area, active scope, and page context without exposing unauthorized resource names or identifiers.
- **FR-015**: The shell MUST provide shared empty states that distinguish no records, filter mismatch, unavailable data, and authorization-limited visibility.
- **FR-016**: The shell MUST provide shared error states for denied access, missing resources, validation failures, unavailable dependencies, and unexpected failures using safe, actionable summaries.
- **FR-017**: Flash messages shown through the shell MUST use safe summaries and MUST NOT reveal raw secrets, credential values, protected prompt content, unauthorized memory content, protected run content, stack traces, or cross-tenant details.
- **FR-018**: Flash messages MUST remain associated with the correct user and active scope so that a message generated in one scope is not displayed as confirmation or evidence in another unauthorized scope.
- **FR-019**: Filterable workflow, model-skill, run inspection, and reliability pages SHOULD support saved filters when the filters are useful for repeated administrative work.
- **FR-020**: Saved filters MUST be persisted server-side, scoped to the user, admin area, and active tenant or platform scope, and MUST NOT apply criteria that the user is no longer authorized to use.
- **FR-020a**: Saved-filter creation, update, and restoration MUST validate every criterion server-side before persistence or use; unsupported, malformed, expired, unauthorized, or scope-mismatched criteria MUST be rejected or dropped safely.
- **FR-021**: Saved filters MUST be optional for pages where filters are not meaningful or would create confusing behavior.
- **FR-022**: The shell MUST keep the admin experience usable when optional client-side enhancements are unavailable by providing server-rendered navigation, scope display, breadcrumbs, messages, and page content.
- **FR-023**: The shell MUST include admin links or navigation entries for workflow administration, model-skill configuration and history, run inspection and replay, and reliability controls, limited by authorization and active scope.
- **FR-024**: The delivered feature MUST include coverage evidence showing at least 90 percent coverage for submitted code related to the shell, navigation, scope handling, authorization behavior, audit decisions, shared states, safe messages, breadcrumbs, and saved filters.
- **FR-025**: The delivered feature MUST include docs covering admin shell concepts, supported scopes, navigation groups, common states, safe messages, saved filters, audit expectations, and how existing admin pages are organized by the shell.
- **FR-026**: The delivered feature MUST include PR review notes covering platform-admin behavior, tenant-admin behavior, route preservation, fail-closed denied navigation, access-decision auditing, safe flash messages, shared states, saved filters, testing evidence, and known risks.
- **FR-027**: The delivered feature MUST include reviewer testing instructions that verify platform-admin navigation, tenant-admin navigation, tenant switching, authorization-aware menu visibility, direct-route denial, audit records, breadcrumbs, empty and error states, safe flash messages, saved filters, and links to existing admin pages.
- **FR-028**: The delivered feature MUST update the README with administrator-facing guidance for using the shared shell, understanding active scope, locating existing admin pages, interpreting common states, and using saved filters.

### Key Entities

- **Admin Console Shell**: The shared administrative frame that organizes navigation, scope display, breadcrumbs, messages, common states, page actions, and existing admin destinations.
- **Admin Principal**: The signed-in administrative actor, including role context, tenant memberships, and platform or tenant authority used for access decisions.
- **Administrative Scope**: The current scope in which the administrator is operating, either platform scope with no `tenant_id` or a specific tenant scope carried by a validated `tenant_id` query parameter on shell links and forms.
- **Navigation Item**: A link or menu entry for an administrative destination, including its required authority, destination area, active-state behavior, and visibility outcome.
- **Existing Admin Destination**: A pre-existing server-rendered `web_admin` UI page for workflow, model-skill, run inspection, or reliability administration that remains available through its original route while being organized by the shell.
- **Page Layout Context**: The shared information needed to render a shell-wrapped page, including title, scope, navigation state, breadcrumbs, actions, messages, and content state.
- **Breadcrumb**: A safe navigation trail segment that communicates page location and scope without leaking unauthorized resource details.
- **Flash Message**: A short, user-visible status message tied to a user and scope, with safe summarized content.
- **Common State**: A reusable empty, denied, unavailable, missing, validation, partial, or unexpected-error state used across shell-wrapped pages.
- **Saved Filter**: A server-persisted, user-, admin-area-, and scope-bound set of validated filter criteria for a filterable admin page, restored only when safe and meaningful.
- **Access Decision Audit Record**: An auditable record of allow, deny, unavailable, or indeterminate decisions; navigation visibility is recorded once per request and active scope with item-level outcomes, while direct destination access, scope selection, and filter restoration are recorded as separate decisions.
- **Delivery Evidence**: Coverage, docs, PR review notes, testing instructions, and README updates required to prove the shell is ready for review and operation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of tested platform-admin, tenant-admin, multi-tenant-admin, and unauthorized-user sessions show the correct active scope state and permitted navigation for that user.
- **SC-001a**: 100 percent of tested tenant-scoped shell links, form submissions, and bookmarked admin URLs preserve scope with a validated `tenant_id` query parameter, while platform-scope URLs omit `tenant_id`.
- **SC-002**: 100 percent of denied, unavailable, or indeterminate navigation and direct-destination access attempts fail closed without exposing protected tenant, workflow, run, reliability, model, skill, prompt, memory, or secret details.
- **SC-003**: 100 percent of evaluated admin access decisions in acceptance testing create audit evidence using the required granularity: one itemized navigation-visibility record per request and active scope, plus separate records for direct destination access, scope selection, and saved-filter restoration.
- **SC-003a**: 100 percent of tested audit-persistence failures fail closed with a safe unavailable state, blocked protected destination or action, and operational log and metric evidence.
- **SC-004**: Authorized administrators can reach existing workflow, model-skill, run inspection, and reliability pages from the shell in three navigation actions or fewer during acceptance testing.
- **SC-005**: 100 percent of existing server-rendered `web_admin` UI routes for workflow, model-skill, run inspection, and reliability administration render inside the shared shell and remain directly reachable for authorized users under their original route identity.
- **SC-006**: At least 90 percent of administrators in acceptance testing can identify whether they are operating in platform scope or a tenant scope within 5 seconds of opening a shell-wrapped page.
- **SC-007**: 100 percent of shell-wrapped pages in acceptance testing include consistent navigation, active scope display, breadcrumbs, message area, main content region, and safe common states when those states apply.
- **SC-008**: 100 percent of tested flash messages and shared error states reveal zero raw secrets, credentials, protected prompt content, unauthorized memory content, stack traces, or cross-tenant details.
- **SC-009**: 100 percent of saved filters tested for filterable admin pages persist server-side, restore only within the correct user and scope context, and reject or drop unsupported, malformed, expired, unauthorized, or scope-mismatched criteria.
- **SC-010**: Submitted shell behavior demonstrates at least 90 percent coverage for submitted code.
- **SC-011**: Docs, PR review notes, testing instructions, and README guidance are present and sufficient for a maintainer to verify and operate the feature without additional verbal explanation.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover platform-admin sessions, tenant-admin sessions, multi-tenant scope switching, unauthorized users, authorization-aware menu visibility, direct route access, denied-route fail-closed behavior, access-decision audit records, audit-persistence failure behavior, breadcrumbs, common empty states, common error states, safe flash messages, saved filters, optional enhancement failure, and links to workflow, model-skill, run inspection, and reliability pages.
- **PR Review Guidance**: PR notes must call out platform-admin behavior, tenant-admin behavior, active scope display, tenant switching, route preservation, authorization source of truth, denied navigation, fail-closed behavior, audit completeness, safe messaging, shared states, saved-filter scoping, documentation, coverage, and known limitations.
- **Documentation Impact**: The feature requires docs and README updates that explain the shared admin shell, platform and tenant scopes, navigation groups, existing page organization, breadcrumbs, common states, safe flash messages, saved filters, audit expectations, and troubleshooting for denied or unavailable destinations.

## Constitution Impact

- **Tenant Isolation And Fair Scheduling**: Scope display, navigation, route access, saved filters, breadcrumbs, and messages must enforce tenant boundaries and fail closed when authorization is denied or unavailable.
- **Security With Practical Development Ergonomics**: Platform-admin and tenant-admin authority must be explicit, authorization decisions must be auditable, and safe messages must avoid sensitive or unauthorized data.
- **Operability Is A Product Requirement**: The shell improves administrator orientation and access to existing workflow, model-skill, run inspection, and reliability operational pages.
- **Spec-Driven Delivery**: Planning and tasks must trace shell behavior, shared states, audit expectations, review evidence, documentation, and README updates back to this specification.
- **Test And Documentation Discipline**: Submitted code requires at least 90 percent coverage plus reviewer testing instructions, PR notes, docs, and README guidance.
- **Clear Ownership And Small Safe Changes**: The shell organizes existing admin destinations without replacing routes, allowing incremental adoption across admin pages.
- **Secret Hygiene And Controlled Tool Access**: Flash messages, errors, breadcrumbs, audit summaries, and saved filters must not reveal raw secrets, credentials, protected prompts, unauthorized memory, protected run content, or cross-tenant details.

## Assumptions

- Existing authentication and authorization behavior can distinguish platform administrators, tenant administrators, multi-tenant administrators, and unauthorized users.
- Existing admin pages for workflows, model-skill configuration, run inspection, and reliability remain the authoritative destinations; this feature organizes and wraps them rather than redefining their core workflows.
- Tenant scope is required for tenant-scoped admin actions; platform scope is required for platform-level actions.
- Saved filters are useful for filterable list and investigation pages, but not every admin page needs filter persistence.
- The admin experience remains primarily server-rendered, with optional client-side enhancements limited to improving interactions rather than becoming required for access or navigation.
- Detailed file placement, template composition, and enhancement implementation choices are deferred to planning while preserving the existing admin application structure.
