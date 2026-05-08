# Research: Admin UI Transitional React Label Removal

## Decision: Define User-Facing Text By Rendered Surface

**Rationale**: The roadmap explicitly allows React as an implementation detail
but removes it from production-visible product copy. The clean boundary is
whether a user can see the string through a route response, browser page,
fallback state, redirect notice, screenshot, or user-facing guide.

**Alternatives considered**:

- Ban every repository occurrence of "React". Rejected because source code,
generated contracts, package names, and historical specs legitimately use the
framework name.
- Only scan frontend source. Rejected because backend page contracts,
navigation, breadcrumbs, fallback HTML, and redirect copy also render visible
text.

## Decision: Preserve Developer-Only Migration Evidence

**Rationale**: Platform reviewers need implementation evidence while the
ordinary product surface should say "Admin". Developer-only migration evidence
can mention React when the implementation detail is the subject of review.

**Alternatives considered**:

- Remove the migration evidence page. Rejected because QA and release review
still need final evidence.
- Rename every migration reference. Rejected because historical and technical
context would become less precise.

## Decision: Add A Visible-Text Gate

**Rationale**: Spec 058 proves live-only behavior. Spec 059 needs a different
gate: rendered product terminology. The scanner should classify blocking
visible labels separately from allowed implementation references.

**Alternatives considered**:

- Rely only on Playwright screenshots. Rejected because screenshots are useful
review evidence but are not complete route coverage.
- Rely only on source search. Rejected because source search cannot distinguish
rendered product copy from internal identifiers.

## Decision: Keep Compatibility Behavior Stable

**Rationale**: The spec is a copy and terminology cleanup, not a route removal.
Old links, redirects, and retained fallback behavior must continue to work while
their visible copy stops saying React.

**Alternatives considered**:

- Delete compatibility routes. Rejected as out of scope and risky for users.
- Hide fallback pages from validation. Rejected because they are user-visible
when old links are used.

## Decision: QA Docs Say Admin, Implementation Notes May Say React

**Rationale**: QA documents are partly user-facing and partly technical. They
should model product terminology in instructions while allowing precise
implementation context in validation explanations, artifact names, and
historical references.

**Alternatives considered**:

- Remove React from all QA documents. Rejected because validation needs to
explain the implementation-era label being removed.
- Leave docs unchanged. Rejected because screenshots and manual QA should
verify the final user-facing terminology.
