# UI Contract: React Agent And Workflow Test Bench

## Route

- React route: `/admin/app/test-bench`
- Backend HTML wrapper: `GET /admin/app/test-bench`
- Primary JSON bootstrap: `GET /admin/app/test-bench/bootstrap.json`
- Existing fallback route remains available: `/admin/agent-tests/ui`

## Navigation

Backend section metadata drives Suites, Cases, Runs, Diagnostics, Artifacts, Publish gates, and Audit. React must not infer unavailable targets, execution modes, or cross-tenant links from absent data.

## Required Views

- Dashboard summary and gate alerts.
- Suite list with filters and latest run state.
- Suite detail with cases, target binding, run launcher, recent runs, and publish-gate panel.
- Suite form with guided target and safe-mode defaults.
- Case form with fixture summary, contract shape summary, assertion builder, evaluator reference, and threshold controls.
- Run list and run detail.
- Trace and diagnostics panels.
- Artifact metadata panel.
- Publish-gate evidence panel.
- Audit timeline.

## Required States

- Loading bootstrap data.
- Empty suites.
- Empty cases.
- Denied unauthenticated route.
- Cross-tenant safe problem response.
- Suite validation error.
- Case validation error.
- Stale suite revision.
- Stale target revision.
- Run queued, running, passed, failed, canceled, timed out, and unavailable.
- Artifact ready, expired, denied, and unavailable.
- Gate missing, stale, running, failing, passing, and unavailable.
- Redaction unavailable and audit unavailable.

## Safety Requirements

- Render only safe labels, summaries, status badges, revision tokens, evidence references, artifact metadata, redaction classes, usage summaries, latency summaries, and authorized links.
- Never render raw secrets, credential values, authorization headers, provider tokens, raw prompts, raw completions, private channel messages, memory contents, connector request/response payloads, raw tool outputs, raw transcripts, stack traces, local paths, storage paths, or unauthorized tenant labels.
- User-facing errors come from safe problem details or safe mutation results.
- Mock execution is the default local mode.
- Real dependency probes require explicit policy-approved evidence.
- Publish gates use current target revision evidence only.

## Expected Interactions

- Tenant admin creates a suite for a workflow draft target.
- Tenant admin adds a fixture-backed case with assertions.
- Tenant admin launches a mock-mode run.
- Tenant admin watches backend-owned run progress.
- Tenant admin opens passing and failing diagnostics.
- Tenant admin reviews artifact references.
- Tenant admin reviews stale and current publish-gate evidence.
- Tenant admin verifies another tenant cannot see suite, run, target, artifact, or gate detail.
- Platform admin can review platform-visible suite and gate summaries without tenant-private transcripts.

## Accessibility And Responsiveness

- Forms must have labels and associated field errors.
- Assertion builder controls must be keyboard accessible.
- Run status and gate status must use text plus status badge.
- Tables/lists must remain readable on mobile through stacked rows or responsive constraints.
- Queued/running states must preserve button dimensions and avoid layout shift.
- Stale conflict recovery and confirmation states must be reachable by keyboard.
