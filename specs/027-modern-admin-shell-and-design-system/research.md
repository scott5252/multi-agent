# Research: Modern Admin Shell And Design System

## Decision 1: Component Library Scope

**Decision**: Build small local primitives for Spec 027 and add `lucide-react`
for icons instead of adopting a broad headless component library.

**Rationale**: The shell needs predictable buttons, icon buttons, dialogs,
tabs, drawers, badges, and states, but the current scope is a foundation rather
than a domain-heavy app. Local primitives keep bundle and dependency risk low,
fit the existing Vite workspace, and allow precise accessibility tests.

**Alternatives Considered**:

- Large headless UI library: deferred because it introduces broader API and
  styling decisions before domain pages prove need.
- CSS-only components: rejected because dialogs, drawers, and command/search
  need keyboard and focus behavior.

## Decision 2: Navigation Authority

**Decision**: Keep the existing Python admin navigation registry and Spec 026
React bootstrap contract authoritative for navigation visibility and fallback
links.

**Rationale**: Authorization-aware navigation already exists server-side. React
should improve presentation, not copy access rules into the browser.

**Alternatives Considered**:

- Browser-maintained route map: rejected because it risks authorization drift.
- Duplicate navigation JSON file: rejected because it creates a second source
  of truth.

## Decision 3: Command/Search Scope

**Decision**: Limit command/search to backend-authorized admin destinations and
safe labels in Spec 027.

**Rationale**: Searching runs, prompts, memory, private channel messages, or
tool outputs requires deeper redaction and tenant-specific search policy. A
safe destination command menu still improves navigation without broadening data
exposure.

**Alternatives Considered**:

- Full global object search: deferred to a later spec with explicit backend
  query policy and audit coverage.
- No command/search: rejected because the roadmap asks for safe global command
  access where possible.

## Decision 4: Saved Filter Presentation

**Decision**: Render saved filters as safe chips and a management panel using
backend-provided summaries and existing destination links.

**Rationale**: Saved filters already exist in the Jinja admin console. The
React shell can make them visible and navigable without inventing mutation
rules in the browser.

**Alternatives Considered**:

- Full React saved-filter editor: deferred because mutation parity belongs with
  domain page migrations.
- Hidden saved filters: rejected because saved filters are explicitly part of
  the shell usability target.

## Decision 5: Design Tokens

**Decision**: Define local CSS custom properties for color, spacing, type,
focus, status, density, z-index, and motion.

**Rationale**: Tokens create a stable surface for future domain pages while
remaining easy to inspect and test in the current frontend workspace.

**Alternatives Considered**:

- Hard-coded component colors: rejected because it will not scale.
- External design-token build tool: deferred until token volume or theming
  requires it.

## Decision 6: Accessibility Validation

**Decision**: Use component tests for accessible names and states, plus
Playwright keyboard/mobile flows for shell navigation, drawer behavior, and
visual screenshots.

**Rationale**: The shell is a repeated experience. Keyboard order, focus, and
responsive layout need browser-level evidence, while component tests catch
regressions quickly.

**Alternatives Considered**:

- Manual screenshots only: rejected because keyboard/focus regressions are easy
  to miss.
- Browser-only validation: rejected because components should be testable in
  isolation before domain pages reuse them.
