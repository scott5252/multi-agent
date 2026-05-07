# Research: Test Bench Full React Parity And Jinja Removal

## Decision: Redirect Legacy Browser Routes Into React

**Rationale**: The remaining test-bench templates are under `web_admin/templates/agent_tests` and are reached through `/admin/agent-tests/ui...` browser handlers. React already owns the replacement workspace at `/admin/app/test-bench`, so old GET routes should redirect with tenant id, ids, filters, saved-filter intent, breadcrumbs, and conflict state when those values are safe.

**Alternatives considered**: Keeping templates as fallback was rejected because this roadmap requires removal, not additive React primary behavior. Returning 410 for all old links was rejected because safe direct-link continuity is required where route parameters can be preserved.

## Decision: Keep JSON Agent-Test APIs

**Rationale**: `/admin/agent-tests/suites`, `/runs`, and `/publish-gates/evaluate` are API routes with Pydantic response models, not Jinja browser surfaces. They remain useful for tests and clients while the browser UI moves fully to React.

**Alternatives considered**: Removing JSON APIs together with UI templates was rejected because the spec only authorizes removal of browser-rendering Jinja surfaces and would break existing contract tests.

## Decision: Use Backend-Owned Bounded Polling For Progress

**Rationale**: The current React test bench already consumes backend-owned run detail snapshots. Bounded polling or manual refresh is sufficient for deletion parity, and React must not infer terminal state from timers or local UI state.

**Alternatives considered**: Adding a new SSE progress stream was deferred because it would expand runtime behavior and validation surface without being required for safe template removal.

## Decision: Artifacts Stay Metadata-Only

**Rationale**: Artifact payloads can contain transcripts, prompts, completions, connector payloads, or storage paths. React and redirects should expose only artifact reference id, label, checksum, size, retention state, access status, redaction class, and authorized metadata links.

**Alternatives considered**: Inline artifact previews and direct downloads were rejected for this spec because the roadmap explicitly bans raw test transcripts, local paths, and raw tool/provider payloads from browser surfaces and QA artifacts.

## Decision: Gate Evidence Must Be Target-Revision Bound

**Rationale**: Workflow publication must accept only current passing evidence for the selected target revision. Missing, stale, running, failing, audit-unavailable, redaction-unavailable, copied, or cross-target evidence must be explicit blockers.

**Alternatives considered**: Showing only a pass/fail summary was rejected because it would hide stale evidence risk and weaken publish-gate safety.

## Decision: Unsafe Legacy Requests Return Safe Problems

**Rationale**: Some old URLs may include unsafe redirects, cross-tenant ids, unknown tenant scope, stale saved-filter state, or route parameters that cannot be authorized. These must fail closed without revealing protected object existence.

**Alternatives considered**: Best-effort redirects were rejected because they could leak object existence or preserve unsafe destinations.
