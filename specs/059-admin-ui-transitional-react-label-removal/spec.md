# Feature Specification: Admin UI Transitional React Label Removal

**Feature Branch**: `codex/059-admin-ui-transitional-react-label-removal`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Admin UI Transitional React Label Removal. After the browser UI migration and live-data decommission are complete, the production admin interface must stop exposing implementation-era \"React\" wording to users. The system must remove \"React\" from visible navigation, breadcrumbs, shell titles, page headings, document titles, command/search labels, redirect/fallback copy, empty/error states, QA-visible screenshots, and route labels unless the page is an explicitly developer-only migration evidence view. Examples: `/admin/app` must show \"Admin\" rather than \"React Admin\", and navigation labels such as \"Skill tools Diagnostics React\" must become \"Skill tools Diagnostics\"."

## Clarifications

### Session 2026-05-08

- Q: Which surfaces count as user-facing UI for the transitional label cleanup? → A: Production-visible text from backend page contracts, frontend-rendered pages, fallback HTML, redirects, navigation, breadcrumbs, document titles, command/search labels, route labels, empty/error states, and QA-visible screenshots is in scope; source identifiers, generated contracts, package names, tests, historical specs, and build artifacts are out of scope unless rendered into production UI text (autopilot).
- Q: May the migration evidence page remain available and mention "React"? → A: Yes. Developer-only migration evidence may remain available to platform reviewers and may use "React" only as implementation context; ordinary product navigation, headings, and shell copy must still use product terminology (autopilot).
- Q: How should compatibility redirect and fallback copy be worded? → A: Redirects and fallbacks should describe the destination as "Admin" or a domain-specific admin page without saying "React"; old-link compatibility behavior must not change (autopilot).
- Q: How should docs and QA artifacts handle terminology? → A: User-facing docs and QA guides should call the product "Admin" while using "React" only when explaining implementation context, generated assets, historical migration evidence, or technical validation details (autopilot).
- Q: How should automated scanning treat internal or generated "React" strings? → A: Treat internal and generated occurrences as allowed implementation references unless they are surfaced to users through production route responses, browser-visible text, screenshots, redirect copy, or fallback states (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin UI Uses Product Terminology (Priority: P1)

Platform and tenant administrators use the production admin experience without
seeing implementation-era "React" labels in navigation, headings, browser
titles, breadcrumbs, route labels, command/search results, empty states, or
error states.

**Why this priority**: This is the primary user-facing cleanup. The admin
product should read as a stable product surface, not as a migration artifact.

**Independent Test**: Open the production admin entry point and representative
admin workspaces as authorized platform and tenant users, then verify visible
text uses "Admin" or domain-specific labels and no transitional "React"
wording appears.

**Acceptance Scenarios**:

1. **Given** an authorized platform administrator, **When** they open the main admin entry point, **Then** the shell title, browser title, breadcrumbs, navigation labels, and search labels describe the product as "Admin" without transitional "React" copy.
2. **Given** an authorized tenant administrator, **When** they open representative tenant-scoped admin pages, **Then** page headings, empty states, and error states avoid transitional "React" copy while preserving the correct domain terms.
3. **Given** a retained compatibility redirect or fallback route, **When** a user follows it, **Then** the redirect or fallback copy describes the destination without exposing migration-era implementation wording.

---

### User Story 2 - Technical Context Remains Bounded (Priority: P2)

Platform reviewers and developers can still understand the implementation
context where it is genuinely needed, while regular product surfaces and
QA-visible screenshots remain product-oriented.

**Why this priority**: Some historical or developer-only artifacts need
technical precision. Removing every internal occurrence would create churn and
could make evidence harder to review.

**Independent Test**: Review developer-only migration evidence, QA guides, and
historical artifacts to confirm "React" appears only when it identifies
implementation context, not as product-facing UI copy.

**Acceptance Scenarios**:

1. **Given** a developer-only migration evidence page, **When** a platform reviewer opens it, **Then** any remaining "React" wording is clearly implementation context and not navigation/product labeling.
2. **Given** QA guides or PR notes, **When** a reviewer reads them, **Then** the user-facing product is called "Admin" while "React" is limited to implementation context and historical references.
3. **Given** generated contracts, package names, source code identifiers, or historical spec names, **When** they are scanned, **Then** they are not treated as user-facing copy unless rendered into production UI text.

---

### User Story 3 - Transitional Label Regressions Are Prevented (Priority: P3)

Release reviewers have automated evidence that production-visible admin text no
longer exposes banned transitional "React" labels outside the explicit
developer-only allowlist.

**Why this priority**: The cleanup should stay complete after future route,
navigation, or copy changes.

**Independent Test**: Run the visible-text scanner and browser validation over
authenticated admin routes; the check fails for banned "React" labels in
production-visible text and passes with only approved developer-only evidence.

**Acceptance Scenarios**:

1. **Given** the visible-text scanner runs against production admin route responses, **When** a banned transitional "React" label is present, **Then** the scanner reports a blocking finding with the route and text location.
2. **Given** the scanner finds an allowed developer-only implementation reference, **When** the reference is classified, **Then** the report explains why it is allowed and which reviewer policy owns it.
3. **Given** Playwright captures representative admin pages, **When** screenshots are reviewed, **Then** the visible browser UI shows product terminology and no banned transitional labels.

### Edge Cases

- Empty, denied, unauthorized, not-found, stale, and unavailable states must be checked because these often use separate copy paths.
- Compatibility redirects and legacy fallback pages must avoid transitional wording even when they are not part of the main navigation.
- Generated metadata, source identifiers, package names, and historical spec references may contain "React" without being user-facing product copy.
- Developer-only migration evidence may mention "React" when the implementation detail is the evidence being reviewed.
- QA screenshots and docs must not normalize transitional labels by accident.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The production admin shell MUST use product-facing labels such as "Admin" instead of transitional "React Admin" wording in visible titles, breadcrumbs, navigation, and command/search labels.
- **FR-002**: Representative domain admin pages MUST remove transitional "React" wording from visible headings, summaries, empty states, error states, action labels, and route labels.
- **FR-003**: Compatibility redirects, fallback pages, and retained old-link notices MUST describe the destination without exposing migration-era "React" copy to users.
- **FR-004**: The system MUST preserve "React" wording only in explicitly allowed developer-only implementation context, historical artifacts, generated/internal identifiers, package names, and technical QA context.
- **FR-005**: Any allowed visible developer-only "React" wording MUST have an explicit rationale, owner, and reviewer-facing policy note.
- **FR-006**: The system MUST provide automated visible-text evidence that authenticated production admin routes no longer expose banned transitional "React" labels.
- **FR-007**: The visible-text evidence MUST cover platform and tenant-shaped access, empty states, seeded states, denied states, compatibility redirects, and representative domain pages.
- **FR-008**: QA-visible screenshots MUST demonstrate the main admin entry point and representative domain pages with product-facing terminology.
- **FR-009**: Documentation and QA guides MUST call the product "Admin" while using "React" only as implementation context where needed.
- **FR-010**: The cleanup MUST preserve authorization, tenant isolation, redaction, audit behavior, live-data contracts, and compatibility route behavior.

### Key Entities

- **Visible Text Surface**: A production-reachable UI label, heading, breadcrumb, title, command/search result, state message, redirect notice, or route label that a user can see.
- **Transitional Label Finding**: A scanner result identifying banned "React" wording, its surface, severity, route or artifact reference, and remediation owner.
- **Allowed Implementation Reference**: A bounded occurrence of "React" that remains valid because it appears in developer-only migration evidence, internal identifiers, generated artifacts, historical specs, or technical QA context.
- **QA059 Evidence Set**: The documents, screenshots, route responses, scanner report, and validation artifacts proving the transitional label cleanup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The authenticated production admin entry point and representative domain pages show zero banned transitional "React" labels in visible user-facing text.
- **SC-002**: The visible-text scanner reports zero blocking findings and documents every allowed implementation reference.
- **SC-003**: Platform and tenant route tests prove the cleanup under authorized, empty, seeded, denied, and compatibility-route states.
- **SC-004**: Playwright evidence includes screenshots for the main admin entry point and representative domain pages with product-facing terminology.
- **SC-005**: QA documents, user guide, and PR notes contain the cleanup policy, reviewer allowlist, validation commands, screenshots, and no unresolved terminology exceptions.

## Assumptions

- The product-facing name for the browser admin surface is "Admin" unless a domain-specific page label is clearer.
- "React" remains an acceptable implementation term in source code, package names, generated type names, historical spec directories, and developer-only evidence.
- The migration evidence workspace may remain visible to platform reviewers when it is clearly technical evidence rather than ordinary product navigation.
- Existing authorization, tenant scoping, redaction, live-data, and compatibility behavior must be preserved.
- No commit is required between Spec 059 phases; validated prior-spec changes remain in the dirty worktree until the user commits the completed roadmap.
