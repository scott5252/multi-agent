# UI Contract: React Skill Registry And Tool Execution Lifecycle

## Route

- React route: `/admin/app/skills`
- Backend HTML wrapper: `GET /admin/app/skills`
- Primary JSON bootstrap: `GET /admin/app/skills/bootstrap.json`
- Existing Jinja/admin routes remain available:
  - `/admin/skill-registry/ui/packages`
  - `/admin/skill-registry/ui/installations`
  - `/admin/skill-execution/ui/diagnostics`

## Navigation

The page uses backend-provided section metadata and authorized links:

- Publish
- Discover
- Installations
- Credentials
- Readiness
- Binding
- Diagnostics
- Audit

React must not invent hidden protected destinations or infer cross-tenant availability from absent data.

## Required States

- Loading bootstrap data.
- Empty package candidate state.
- Empty tenant discovery state.
- Denied unauthenticated or unauthorized route.
- Cross-tenant safe problem response.
- Package candidate validation failed, blocked, ready, stale, and published.
- Package version published, superseded, quarantined, withdrawn, and unavailable.
- Tenant installation not installed, ready, blocked, degraded, stale conflict, upgrade available, quarantined, and withdrawn.
- Credential reference missing, invalid, unavailable, denied, and ready.
- Smoke-test queued, running, passed, failed, skipped, timed out, and blocked by policy.
- Connector diagnostic ready, degraded, failed, unavailable, and staging-probe pending.
- Binding preview allowed, denied, missing requirements, and unavailable.
- Audit timeline empty, filtered-empty, partial, and unavailable.

## Safety Requirements

- Render only safe labels, summaries, digests, fingerprints, status badges, artifact/evidence references, revision tokens, and authorized links.
- Never render raw secrets, resolved credentials, authorization headers, provider tokens, raw manifests, private messages, memory contents, connector request/response payloads, raw tool outputs, stack traces, local paths, or unauthorized tenant labels.
- User-facing errors come from safe problem details or safe mutation results.
- Manifest candidates are summarized after submit; upload takes precedence over paste.
- Smoke tests, diagnostics, and eligibility previews are explicit actions and do not run as hidden background work.

## Expected Interactions

- Platform admin opens Publish, submits a deterministic manifest fixture, reviews safe validation findings, and publishes an immutable package version.
- Platform admin reviews tenant grants, quarantine, withdrawal, and audit evidence.
- Tenant admin opens Discover, sees granted packages only, and installs a deterministic package.
- Tenant admin configures credential references from authorized choices only.
- Tenant admin runs or refreshes smoke-test/readiness evidence and reviews connector readiness for calendar, Gmail, news, weather, and commute connectors.
- Tenant admin previews binding eligibility for backend-owned workflow/profile contexts.
- Admin opens Diagnostics, reviews SkillExecutionGateway policy decisions and safe connector attempt summaries.
- Admin opens Audit, filters lifecycle timeline records, and follows authorized links.

## Accessibility And Responsiveness

- Wizard step navigation must be keyboard accessible.
- Status badges and icon buttons must have text or aria labels.
- Form errors must be associated with their fields.
- Tables/lists must remain readable on mobile through stacked rows or responsive constraints.
- Queued/running states must preserve button dimensions and not shift surrounding content.
- Confirmation and stale-conflict recovery must be reachable by keyboard.
