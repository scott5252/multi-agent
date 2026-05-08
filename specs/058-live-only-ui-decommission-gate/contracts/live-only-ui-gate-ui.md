# UI Contract: Live-Only UI Decommission Gate

## Surface

The migration hardening workspace exposes the live-only gate through the
existing migration dashboard and live-data inventory panels.

## Required Views

- **Summary**: Shows total findings, blocking findings, mapped legacy findings,
  allowed computed metadata, route target count, empty/seeded route probe count,
  and CI status.
- **Route Classifications**: Lists each production admin UI target with method,
  path, principal scope, empty-state requirement, seeded-state requirement,
  computed metadata flag, and replacement spec.
- **Findings**: Lists blocking, warning, and info findings with marker kind,
  reachability, source path, affected route, owner/replacement spec, safe
  excerpt, and durable source.
- **Allowlist**: Lists narrow computed-metadata/test-only policy entries with
  reason, owner, derivation source, and optional expiration spec.
- **Evidence**: Lists scanner, route response scan, backend route test,
  frontend test, Playwright, QA doc, reviewer note, and curl evidence.
- **States**: Shows blocking or warning problems with safe next actions.

## States

- **Pass**: No blocking findings and no mapped legacy findings remain.
- **Warning**: No blocking findings remain, but allowed or mapped cleanup
  context is still visible for review.
- **Fail**: At least one production-reachable blocking finding remains.
- **Empty**: A fresh database has no live rows for a route and the route shows
  an explicit empty, denied, unavailable, redirect-only, or computed metadata
  state.
- **Unavailable**: A dependency cannot be checked safely and the UI names the
  unavailable evidence without inventing data.

## Interaction Requirements

- Users can navigate to the migration dashboard and live-data inventory without
  using legacy or Jinja routes.
- The Playwright flow must exercise the UI by opening the live-data inventory
  panel and verifying live-only summary text plus at least one evidence or route
  classification row.
- The UI must not expose raw secrets, credentials, prompt/completion content,
  memory contents, raw run payloads, private channel messages, raw tool
  payloads, raw test transcripts, local filesystem paths, stack traces, or
  unauthorized tenant labels.

## Accessibility And Responsiveness

- Summary metrics must fit within their containers on mobile and desktop.
- Findings and route classifications must remain readable with long route paths
  and source paths.
- Status indicators must include text labels, not color alone.
