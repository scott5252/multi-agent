# Feature Specification: Modern Admin Shell And Design System

**Feature Branch**: `codex/027-modern-admin-shell-and-design-system`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Create a feature specification for a modern React admin shell and design system. The shell must make the platform understandable to non-technical platform admins and tenant admins through clear navigation, scope awareness, breadcrumbs, saved filters, global search or command access where safe, contextual page actions, notifications, common loading/empty/error/denied states, and responsive layouts. It must preserve authorization-aware navigation, tenant/platform scope semantics, audit evidence, and redaction. The spec should focus on shared UI behavior and reusable components, not domain-page rewrites."

## Clarifications

### Session 2026-05-04

- Q: What remains authoritative for navigation grouping and destination visibility? -> A: The existing Python admin navigation registry and backend React bootstrap/navigation contract remain authoritative; React only renders allowed records (autopilot).
- Q: What responsive shell pattern should be used? -> A: Use a persistent left navigation on desktop and a compact authenticated drawer on mobile, with the active tenant/platform scope always visible (autopilot).
- Q: How should saved filters appear in the shared shell? -> A: Render saved filters as safe chips and a management panel fed by backend-owned filter metadata; do not let the browser create unvalidated filter destinations (autopilot).
- Q: How should global search or command access behave? -> A: Provide command/search only across authorized destinations and safe identifiers returned by the backend; omit raw run payloads, prompts, memory, private channel text, and external tool payloads (autopilot).
- Q: What accessibility and design-token standard should guide implementation? -> A: Use WCAG 2.2 AA-oriented behavior, keyboard-visible focus, reduced-motion-safe interactions, and stable local design tokens owned by the React admin workspace (autopilot).
- Q: How should React shell links coexist with Jinja fallbacks? -> A: React navigation may improve labels and grouping, but domain links continue to point to existing authorized Jinja destinations unless a later migration flag enables a React route (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate The Platform Confidently (Priority: P1)

An authorized platform or tenant administrator can open `/admin/app` and use a modern shell with clear navigation groups, active scope, breadcrumbs, safe page titles, and existing-page links that explain where each admin area lives.

**Why this priority**: The React migration only helps non-technical administrators if the first screen makes the platform easier to understand without changing domain behavior.

**Independent Test**: Can be tested by signing in as platform and tenant administrators, opening `/admin/app`, and verifying visible scope, navigation grouping, breadcrumbs, page header, and links to existing Jinja destinations.

**Acceptance Scenarios**:

1. **Given** an Auth0-backed platform administrator, **When** they open the React admin shell, **Then** they see platform scope, authorized platform navigation groups, breadcrumbs, and safe existing-page links.
2. **Given** a local-principal tenant administrator, **When** they open the React admin shell, **Then** they see tenant scope, tenant-safe navigation groups, breadcrumbs, and tenant-preserving links.
3. **Given** an unauthorized or non-admin principal, **When** they request the shell, **Then** the response fails closed and does not render shell navigation.

---

### User Story 2 - Use Shared UI Components And States (Priority: P2)

Administrators encounter consistent buttons, icon buttons, tabs, forms, filter chips, tables, status badges, panels, modals, toasts, loading states, empty states, denied states, and error states across the shell foundation.

**Why this priority**: Later domain page migrations need reusable primitives so each page does not invent one-off styling or duplicate interaction rules.

**Independent Test**: Can be tested by rendering the component catalog or shell demo states and verifying keyboard focus, accessible labels, responsive sizing, safe copy, and no overlap across desktop and mobile viewports.

**Acceptance Scenarios**:

1. **Given** a reviewer using keyboard-only navigation, **When** they tab through shell controls, **Then** focus order is visible, logical, and does not trap users outside explicit dialogs.
2. **Given** the shell receives loading, empty, denied, validation-error, dependency-unavailable, and unexpected-error states, **When** they render in React, **Then** each state uses safe copy and consistent actions without stack traces or sensitive data.
3. **Given** the browser viewport is narrow, **When** navigation collapses into the mobile shell, **Then** controls remain readable, reachable, and non-overlapping.

---

### User Story 3 - Find Authorized Destinations Safely (Priority: P3)

Administrators can use safe command/search access, saved-filter chips, contextual page actions, and notifications to move through authorized admin destinations without exposing raw internal identifiers or unauthorized content.

**Why this priority**: Search, saved filters, and actions reduce cognitive load, but they must remain backend-authorized and redaction-safe.

**Independent Test**: Can be tested by requesting search/action/filter metadata as platform, tenant, unauthorized, and cross-tenant principals, then verifying the React shell only renders authorized safe summaries.

**Acceptance Scenarios**:

1. **Given** a tenant administrator, **When** command/search opens, **Then** only tenant-authorized destinations and safe labels appear.
2. **Given** saved filters exist for an admin area, **When** the shell renders filter chips or management controls, **Then** links preserve authorized scope and omit unsafe raw criteria.
3. **Given** a backend action, notification, or search metadata source is unavailable, **When** the shell loads, **Then** the shell renders a safe unavailable or partial-data state and records reviewer-actionable evidence.

### Edge Cases

- The navigation registry contains platform-only, tenant-only, disabled, and future React destinations at the same time.
- A tenant-scoped user opens a platform-only route hint or command result.
- Saved filter metadata contains stale, unauthorized, or malformed filter criteria.
- The active tenant scope is missing, revoked, inactive, or not present in the available scope list.
- Command/search returns no matches for an authorized query.
- Command/search would match a raw identifier that should not be exposed to the current principal.
- The shell loads on mobile while navigation groups are longer than the viewport.
- A modal or drawer is opened and the user navigates entirely by keyboard.
- Motion preferences request reduced motion.
- Backend bootstrap metadata is partial because an optional safe-summary source is unavailable.
- Existing Jinja fallback links remain the only available domain page destination.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The React admin shell MUST render a modern shared layout for `/admin/app` using backend-authorized bootstrap, scope, and navigation metadata from the foundation API.
- **FR-002**: The shell MUST keep the existing Python navigation registry and backend React contract authoritative for groups, destinations, visibility, scope preservation, fallback kind, and route enablement.
- **FR-003**: The shell MUST show active tenant or platform scope persistently on desktop and mobile layouts.
- **FR-004**: The shell MUST provide breadcrumbs, page header structure, contextual page actions, and safe existing-page links for shared shell routes without rewriting domain pages.
- **FR-005**: The shell MUST include reusable React components for buttons, icon buttons, tabs, forms, filters, tables, status badges, panels, modals, toasts, common states, saved-filter chips, breadcrumbs, page headers, and scope selection.
- **FR-006**: Shared components MUST support keyboard-visible focus, accessible names, semantic landmarks, dialog focus management, and responsive layouts oriented to WCAG 2.2 AA expectations.
- **FR-007**: The shell MUST provide loading, empty, filtered-empty, denied, not-found, validation-error, dependency-unavailable, partial-data, and unexpected-error states using safe copy and authorized actions.
- **FR-008**: Saved-filter presentation MUST use backend-provided safe summaries and route-preserving links; the browser MUST NOT trust or execute unvalidated filter criteria.
- **FR-009**: Command/search access, if rendered, MUST be limited to backend-authorized destinations and safe identifiers for the current principal and scope.
- **FR-010**: Notifications and contextual actions MUST render only safe summaries and MUST NOT include raw prompts, completions, memory contents, private channel messages, raw run payloads, raw provider responses, credential values, tool payloads, stack traces, or authorization headers.
- **FR-011**: Existing Jinja admin routes MUST remain directly reachable and linked as fallbacks until later domain migration specs enable React routes.
- **FR-012**: The feature MUST validate both Auth0-backed principal behavior and `AUTH_MODE=local_principal` browser behavior for protected shell access, navigation visibility, scope display, denied states, and redaction.
- **FR-013**: The implementation MUST include component unit tests, backend contract/route tests where contracts change, keyboard/accessibility checks, mobile and desktop Playwright screenshots, QA docs, and reviewer notes.

### Key Entities *(include if feature involves data)*

- **Modern Admin Shell**: The shared React frame containing navigation, scope, breadcrumbs, page header, common states, and fallback links.
- **Design Token Set**: Stable local tokens for color, spacing, typography, focus, density, layout, status, and motion.
- **Navigation Presentation Model**: Backend-authorized grouping and destination metadata transformed into shell UI.
- **Shell State Model**: Safe common states such as loading, empty, denied, unavailable, validation error, and unexpected error.
- **Saved Filter Presentation**: Safe chip and management metadata derived from existing saved-filter records and backend validation.
- **Command/Search Result**: A safe destination or action summary authorized for the current principal and scope.
- **Shell Notification**: A safe, non-sensitive summary for status, partial-data, or action outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of platform-admin and tenant-admin shell smoke flows show the correct active scope, navigation grouping, breadcrumbs, and existing-page fallback links.
- **SC-002**: 100% of unauthorized, non-admin, and cross-tenant shell/navigation/search metadata requests fail closed without rendering restricted navigation or tenant labels.
- **SC-003**: Keyboard-only Playwright or equivalent tests can open navigation, move through controls, close drawers/modals, and reach main content without focus loss.
- **SC-004**: Mobile and desktop screenshots show no incoherent overlap, clipped labels, unreadable buttons, or hidden primary actions in the shared shell.
- **SC-005**: Component tests cover the reusable shell states and primitives required by this spec before any domain page migration depends on them.
- **SC-006**: Required QA docs, frontend checks, backend checks, and Playwright evidence pass before Spec 028 begins.

## Assumptions

- Spec 026 has already added `/admin/app`, the backend bootstrap/config/manifest routes, generated TypeScript contracts, Vite build output, and local-principal Playwright validation.
- The existing admin navigation registry remains the source of truth for shell destinations.
- Domain page rewrites remain out of scope; this spec may add placeholders, shared states, or links but must not migrate workflow, provider, skill, operations, membership, usage, Telegram, or test-bench pages.
- The initial command/search scope can be limited to authorized admin destinations and safe labels if deeper object search would require new backend search policy.
- Lucide React icons may be used for shell controls if added as a checked frontend dependency.
- Local QA uses deterministic Acme and Globex tenants and does not require real Auth0, provider, Telegram, credential, connector, or external tool calls.
