# Feature Specification: Jinja Surface Inventory And Deletion Plan

**Feature Branch**: `codex/038-jinja-surface-inventory-and-deletion-plan`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Jinja Surface Inventory and Deletion Plan. The platform has React primary routes from Specs 026 through 037, but Jinja templates and fallback route handlers still exist. The goal is to produce a deletion-grade inventory of every Jinja template, template include, template view model, TemplateResponse route, legacy static JavaScript/CSS asset, direct-link URL, form action, export, upload, filter, SSE/progress surface, mutation, denied state, and replacement React path. The output must classify each item as React parity proven, React parity missing, redirectable, non-Jinja compatibility needed, safe to delete, or blocked with reason."

## Clarifications

### Session 2026-05-05

- Q: Which inventory sources are in scope? → A: Include all repository Jinja templates, web_admin legacy static assets, TemplateResponse/Jinja2Templates usage, template view-model helpers, route declarations, and docs/QA direct links. (autopilot)
- Q: What qualifies as deletion-grade parity? → A: Replacement evidence must cover safe journeys, denied states, tenant scope, redaction, direct links, filters, mutations, exports, uploads, SSE/progress, artifacts, dual-auth tests, Playwright evidence, and reviewer signoff. (autopilot)
- Q: Are user-facing `/runs` pages and auth/local-login in scope? → A: Yes; inventory includes `/runs`, auth/local-login, the React app host, shell utilities, admin domain pages, and fallback browser routes. (autopilot)
- Q: How should redirects and deprecation be planned? → A: Prefer authenticated redirects that preserve state for safe direct links, require non-Jinja compatibility responses when redirects cannot preserve behavior, and require explicit reviewer signoff before deletion. (autopilot)
- Q: Where should evidence live and is static Vite HTML allowed? → A: Store deterministic inventory and QA evidence under the active spec artifacts and migration dashboard projection; static Vite HTML is allowed because the removal target is server-side Jinja rendering. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Complete Jinja Surface Inventory (Priority: P1)

Platform operators and reviewers need one authoritative inventory of every server-rendered Jinja surface, linked legacy asset, route handler, form/action URL, direct-link URL, and proposed React or non-Jinja replacement before any deletion work starts.

**Why this priority**: Complete inventory is the deletion gate for all later Jinja removal specs; without it, route retirement could break support links, user-facing run flows, auth utilities, exports, uploads, or denied-state behavior.

**Independent Test**: Run the inventory scanner and open the React migration dashboard inventory section, then compare the generated evidence against template files, static legacy assets, TemplateResponse routes, route names, and known direct links from docs/QA.

**Acceptance Scenarios**:

1. **Given** the repository contains Jinja templates and fallback route handlers, **When** the scanner runs, **Then** every template file, include relationship, TemplateResponse usage, Jinja2Templates import, template view-model helper, route name, and legacy static asset appears in the machine-readable inventory with source location and owner category.
2. **Given** a reviewer opens `/admin/app/migration`, **When** they inspect the Jinja inventory section, **Then** they can see counts and grouped records for templates, routes, static assets, direct links, actions, exports, uploads, filters, SSE/progress surfaces, mutations, denied states, and replacement paths.
3. **Given** a route or template has incomplete discovery data, **When** the inventory classifies it, **Then** the item is marked blocked or React parity missing with a reason rather than safe to delete.

---

### User Story 2 - Classify Deletion Readiness And Replacement Path (Priority: P2)

React migration reviewers need every legacy surface classified as React parity proven, React parity missing, redirectable, non-Jinja compatibility needed, safe to delete, or blocked with reason, including the planned removal spec and evidence references.

**Why this priority**: Later Specs 039 through 047 must delete only bounded surfaces with proof; consistent readiness states prevent accidental removal of fallback behavior or protected data paths.

**Independent Test**: Review the generated inventory JSON and migration dashboard readiness table, then verify a sample from each category has replacement path, evidence references, direct-link behavior, owner, planned removal spec, and blocker notes.

**Acceptance Scenarios**:

1. **Given** a legacy admin browser route has a React equivalent and documented dual-auth QA evidence, **When** the inventory is generated, **Then** it records the React path, evidence references, redirectability decision, and planned removal spec.
2. **Given** a user-facing `/runs` or auth/local-login surface exists, **When** the inventory is generated, **Then** it is included and classified even when it is not yet safe to delete.
3. **Given** a legacy static asset may still be loaded by Jinja or React, **When** the inventory is generated, **Then** it records usage evidence and avoids marking the asset safe to delete unless usage is proven obsolete.

---

### User Story 3 - Prove Safe Direct-Link, Denied-State, And Redaction Coverage (Priority: P3)

Security reviewers need spot checks and documentation proving that legacy direct links, denied states, tenant scope, safe breadcrumbs, redacted evidence, and static documentation references are accounted for before route retirement begins.

**Why this priority**: Jinja removal must not weaken authentication, tenant isolation, audit evidence, or redaction, and route retirement must preserve safe support links or return non-Jinja compatibility responses.

**Independent Test**: Run backend route tests and Playwright local-principal checks for the inventory projection, then inspect QA docs and redaction sweep evidence for local-principal, Auth0-shaped, denied, and cross-tenant cases.

**Acceptance Scenarios**:

1. **Given** an unauthenticated or unauthorized principal requests inventory data, **When** the backend route handles the request, **Then** it fails closed without revealing unauthorized tenant labels, raw secrets, private payloads, stack traces, or local filesystem details.
2. **Given** a legacy direct link contains route parameters or query filters, **When** the inventory records its retirement plan, **Then** it documents whether an authenticated redirect can preserve those values or whether a non-Jinja compatibility response is required.
3. **Given** docs or QA guides reference old Jinja browser URLs, **When** the scanner runs, **Then** those references are listed so later specs can update or prove compatibility.

### Edge Cases

- A template is referenced only through an include or inheritance chain and has no direct route.
- A TemplateResponse call builds the template name indirectly or through a container template provider.
- A static JavaScript or CSS asset is loaded by both Jinja and a React shell compatibility path.
- A route has a JSON API path with the same prefix as a browser-rendered path.
- A legacy route supports exports, uploads, or POST mutations that cannot be redirected as a simple GET.
- A user-facing `/runs` flow includes SSE/progress behavior, callback/subscription links, approvals, artifacts, or results.
- A denied-state page must not reveal whether an unauthorized tenant, run, workflow, provider, skill, prompt, or membership exists.
- A direct link cannot preserve tenant scope or filters without ambiguity.
- A documentation reference points to a legacy URL that is intentionally retained for a later removal spec.
- A scanner finding has no safe owner or planned removal spec.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate a deterministic, machine-readable inventory of every Jinja template under the repository runtime template directory, including include or inheritance relationships when discoverable.
- **FR-002**: The system MUST discover legacy static JavaScript and CSS assets under the Jinja web admin static tree and classify whether each asset is Jinja-only, shared, unknown, or blocked pending evidence.
- **FR-003**: The system MUST discover FastAPI TemplateResponse usage, Jinja2Templates imports, template provider references, and template view-model helper references with source file and line evidence.
- **FR-004**: The system MUST discover browser route paths, route names, methods, and direct-link candidates that render Jinja or depend on Jinja-only pages.
- **FR-005**: The system MUST scan docs and QA artifacts for direct-link references to legacy browser URLs that require redirect, alias, update, or compatibility planning.
- **FR-006**: The inventory MUST include user-facing `/runs` pages, auth/local-login pages, the current React app host, admin shell utilities, saved filters, unavailable/error pages, admin domain pages, and all remaining fallback browser routes.
- **FR-007**: Each inventory item MUST be classified as exactly one of React parity proven, React parity missing, redirectable, non-Jinja compatibility needed, safe to delete, or blocked with reason.
- **FR-008**: Each inventory item MUST include replacement path or response plan, owner category, planned removal spec, evidence references, blocker references when applicable, and the reason the current classification was selected.
- **FR-009**: The system MUST avoid marking any template, route, helper, static asset, dependency, or browser behavior safe to delete unless deletion-grade parity evidence is present.
- **FR-010**: The React migration dashboard MUST expose a redaction-safe inventory projection with summary counts, grouped readiness sections, blocker lists, planned removal spec groupings, and evidence links.
- **FR-011**: Inventory API responses MUST be backend-owned contracts and MUST NOT rely on browser-only logic for authorization, tenant scope, redaction, replacement decisions, or deletion readiness.
- **FR-012**: Protected inventory routes MUST validate Auth0-shaped principals in backend tests and local-principal behavior in browser QA.
- **FR-013**: Direct-link planning MUST preserve tenant id, route parameters, query filters, saved-filter intent, safe breadcrumbs, and authentication requirements where a redirect is marked feasible.
- **FR-014**: Direct-link planning MUST require a non-Jinja compatibility or documented retirement response when a safe redirect cannot preserve behavior.
- **FR-015**: The inventory MUST include denied-state, cross-tenant, redaction, export, upload, mutation, filter, SSE/progress, artifact, callback, and subscription coverage fields where those behaviors apply.
- **FR-016**: QA artifacts MUST document how reviewers regenerate the inventory, inspect the migration dashboard, verify blocked classifications, run redaction sweeps, and perform tenant-isolation spot checks.
- **FR-017**: The feature MUST NOT delete Jinja templates, remove Jinja dependencies, disable fallback route handlers, or change legacy browser-route behavior in Spec 038.
- **FR-018**: The system MUST produce reviewer or PR notes explaining retained Jinja surfaces, blocked items, removal sequence, rollback assumptions, and handoff expectations for Specs 039 through 047.
- **FR-019**: The inventory MUST require explicit reviewer signoff before any later spec may treat an item as deletion-approved.
- **FR-020**: The inventory MUST treat static Vite HTML and built React assets as allowed non-Jinja browser delivery surfaces while still tracking any Jinja-only app host or static assets that remain.

### Key Entities *(include if feature involves data)*

- **Jinja Inventory Item**: A discovered template, route, helper, static asset, direct link, action, export, upload, filter, SSE/progress surface, mutation, denied state, or replacement behavior requiring deletion readiness classification.
- **Inventory Evidence Reference**: A safe reference to a test, QA guide, screenshot, generated contract, source location, docs link, or parity record that supports a classification without exposing sensitive payloads.
- **Replacement Plan**: The React path, authenticated redirect, alias, non-Jinja compatibility response, documented retirement response, or blocker that explains how a legacy browser surface will be handled.
- **Deletion Readiness Classification**: The state assigned to an inventory item: React parity proven, React parity missing, redirectable, non-Jinja compatibility needed, safe to delete, or blocked with reason.
- **Planned Removal Spec**: The later roadmap spec, from 039 through 047, responsible for deletion or conversion of a bounded surface after parity evidence is complete.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of runtime Jinja template files and legacy web admin static JavaScript/CSS files appear in the generated inventory with classification and source path evidence.
- **SC-002**: 100% of TemplateResponse usages, Jinja2Templates imports, and template provider references in `src/multi_agent_platform` appear in the generated inventory or blocked scanner notes.
- **SC-003**: 100% of inventory items include one classification, planned removal spec, owner category, replacement path or response plan, and evidence or blocker reference.
- **SC-004**: 0 inventory items are classified safe to delete without explicit parity evidence, reviewer signoff requirement, and planned removal spec.
- **SC-005**: The React migration dashboard renders inventory summary, blocker, and readiness sections for platform-admin and tenant-admin-acme local-principal QA without raw secrets, private payloads, local filesystem paths, stack traces, or unauthorized tenant labels.
- **SC-006**: Backend tests prove protected inventory APIs enforce Auth0-shaped authentication, authorization, tenant isolation, and redaction behavior for allowed, denied, and cross-tenant cases.
- **SC-007**: Playwright evidence proves local-principal reviewers can open `/admin/app/migration`, inspect Jinja inventory readiness, and capture redaction-safe screenshots.
- **SC-008**: QA docs and reviewer notes provide enough evidence for a reviewer to determine which surfaces are retained, blocked, redirectable, or candidates for later deletion within 10 minutes.

## Assumptions

- The active removal target is server-side Jinja rendering; static Vite HTML and built React assets remain allowed.
- Spec 038 is inventory-only and may add scanners, API projections, React dashboard sections, tests, docs, and generated evidence, but it does not delete runtime Jinja files.
- Existing Specs 026 through 037 remain the source of React parity evidence and migration dashboard patterns.
- Local QA uses deterministic local principals and mocked-safe dependencies, while production Auth0 behavior is represented by backend route tests.
- Generated inventory evidence is stored in repository docs/spec artifacts or deterministic generated JSON, with screenshots and QA output under spec-specific evidence locations.
- Later specs 039 through 047 own bounded deletion and conversion work based on this inventory.
