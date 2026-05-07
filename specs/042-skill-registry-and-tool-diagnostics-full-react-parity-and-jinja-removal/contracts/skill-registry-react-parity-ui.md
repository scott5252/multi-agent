# UI Contract: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## React Routes

- `/admin/app/skills`: React skill lifecycle dashboard and default publish/discover view.
- `/admin/app/skills/packages`: package list and publication overview.
- `/admin/app/skills/packages/new`: package create state.
- `/admin/app/skills/packages/{package_slug}`: package detail state.
- `/admin/app/skills/packages/{package_slug}/candidate`: manifest candidate and validation findings state.
- `/admin/app/skills/packages/{package_slug}/versions/{semantic_version}`: package version detail state.
- `/admin/app/skills/packages/{package_slug}/versions/{semantic_version}/grants`: tenant grant state.
- `/admin/app/skills/available-versions`: tenant available versions and install entry state.
- `/admin/app/skills/installations`: tenant installation list state.
- `/admin/app/skills/installations/{installation_id}`: installation detail, readiness, smoke, binding, and audit state.
- `/admin/app/skills/installations/{installation_id}/credentials`: credential configure state.
- `/admin/app/skills/installations/{installation_id}/smoke-tests`: smoke-test history and explicit refresh state.
- `/admin/app/skills/installations/{installation_id}/eligibility-preview`: binding eligibility preview state.
- `/admin/app/skills/diagnostics`: SkillExecutionGateway diagnostics state.
- `/admin/app/skills/audit`: lifecycle audit timeline state.

## JSON Contracts

- `GET /admin/app/skills/bootstrap.json`
- `GET /admin/app/skills/packages.json`
- `GET /admin/app/skills/packages/{package_slug}.json`
- `POST /admin/app/skills/packages`
- `POST /admin/app/skills/packages/candidates`
- `POST /admin/app/skills/packages/candidates/{candidate_id}/validate`
- `POST /admin/app/skills/packages/candidates/{candidate_id}/publish`
- `POST /admin/app/skills/packages/{package_slug}/versions/{semantic_version}/grants`
- `POST /admin/app/skills/packages/{package_slug}/versions/{semantic_version}/lifecycle`
- `GET /admin/app/skills/available-versions.json`
- `POST /admin/app/skills/installations`
- `GET /admin/app/skills/installations.json`
- `GET /admin/app/skills/installations/{installation_id}.json`
- `POST /admin/app/skills/installations/{installation_id}/credentials`
- `POST /admin/app/skills/installations/{installation_id}/readiness`
- `POST /admin/app/skills/installations/{installation_id}/smoke-tests`
- `POST /admin/app/skills/installations/{installation_id}/eligibility-preview`
- `POST /admin/app/skills/diagnostics/run`
- `GET /admin/app/skills/audit.json`
- `GET /admin/app/skills/legacy-routes.json`

## Legacy Browser Redirects

- `/admin/skill-registry/ui/packages` redirects to `/admin/app/skills/packages`.
- `/admin/skill-registry/ui/packages/new` redirects to `/admin/app/skills/packages/new`.
- `/admin/skill-registry/ui/packages/{package_slug}` redirects to `/admin/app/skills/packages/{package_slug}`.
- `/admin/skill-registry/ui/packages/{package_slug}/candidate` redirects to `/admin/app/skills/packages/{package_slug}/candidate`.
- `/admin/skill-registry/ui/packages/{package_slug}/versions/{semantic_version}` redirects to `/admin/app/skills/packages/{package_slug}/versions/{semantic_version}`.
- `/admin/skill-registry/ui/packages/{package_slug}/versions/{semantic_version}/grants` redirects to `/admin/app/skills/packages/{package_slug}/versions/{semantic_version}/grants`.
- `/admin/skill-registry/ui/available-versions` redirects to `/admin/app/skills/available-versions`.
- `/admin/skill-registry/ui/installations` redirects to `/admin/app/skills/installations`.
- `/admin/skill-registry/ui/installations/{installation_id}` redirects to `/admin/app/skills/installations/{installation_id}`.
- `/admin/skill-registry/ui/installations/{installation_id}/credentials` redirects to `/admin/app/skills/installations/{installation_id}/credentials`.
- `/admin/skill-registry/ui/installations/{installation_id}/smoke-tests` redirects to `/admin/app/skills/installations/{installation_id}/smoke-tests`.
- `/admin/skill-registry/ui/installations/{installation_id}/eligibility-preview` redirects to `/admin/app/skills/installations/{installation_id}/eligibility-preview`.
- `/admin/skill-execution/ui/diagnostics` redirects to `/admin/app/skills/diagnostics`.

## Required States

- Loading.
- Empty authorized package list, available versions, installation list, diagnostics, and audit states.
- Denied unauthenticated or unauthorized route.
- Cross-tenant safe problem.
- Package candidate saved, validation blocked, validation ready, publish confirmation required, stale conflict, published.
- Package version published, superseded, quarantined, withdrawn, runtime blocked, unavailable.
- Tenant grant enabled, disabled, denied, stale conflict, unavailable.
- Installation ready, blocked, degraded, stale conflict, upgrade available, quarantined, withdrawn, cross-tenant unavailable.
- Credential reference missing, invalid, denied, unavailable, ready.
- Smoke-test queued, running, passed, failed, skipped, timed out, blocked by policy.
- Connector diagnostic ready, degraded, failed, unavailable, blocked by policy.
- Binding preview allowed, denied, missing requirements, unavailable.
- Legacy route redirected, converted, gone, retained with blocker.

## Safety Requirements

- Render only safe labels, summaries, digests, fingerprints, status badges, artifact references, revision tokens, audit ids, and authorized links.
- Never render raw secrets, resolved credentials, authorization headers, provider tokens, raw manifests after submit, private messages, memory contents, connector request/response payloads, raw tool outputs, raw smoke transcripts, stack traces, local paths, or unauthorized tenant labels.
- Manifest candidates are summarized after submit; upload takes precedence over paste.
- Smoke tests, diagnostics, and eligibility previews are explicit actions and do not run as hidden background work.
- User-facing errors come from safe problem details, safe mutation results, or React common states.

## Accessibility And Responsiveness

- Section navigation and stale-conflict recovery must be keyboard accessible.
- Status badges and icon buttons must have text or aria labels.
- Form errors must be associated with fields.
- Tables and card lists must remain readable on mobile through stacked rows or responsive constraints.
- Queued/running action states must preserve button dimensions and avoid layout shift.
