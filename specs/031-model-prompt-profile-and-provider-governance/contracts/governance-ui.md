# UI Contract: Model, Prompt, Profile, And Provider Governance

## Route

- React route: `/admin/app/governance`
- Backend HTML fallback wrapper: `GET /admin/app/governance`
- Primary JSON bootstrap: `GET /admin/app/governance/bootstrap.json`
- Existing Jinja/admin routes remain available until Spec 037.

## Navigation

The page uses backend-provided section metadata and authorized links:

- Setup
- Providers
- Prompts
- Profiles
- Routing
- Provenance

The section order may differ visually when the backend marks blockers, but React must not invent hidden protected destinations.

## Required States

- Loading bootstrap data.
- Empty authorized section.
- Denied unauthenticated or unauthorized route.
- Cross-tenant safe problem response.
- Provider degraded, unavailable, breaker-open, missing credential, invalid credential, and explicit probe failed.
- Prompt preview rendered, summarized, blocked, and unavailable.
- Profile resolution allowed, fallback, denied, and unavailable.
- Routing preview allowed, fallback, denied, and unavailable.
- History/provenance filtered with bounded results.
- Partial data when optional diagnostics are unavailable.
- Platform-only action hidden or disabled for tenant principals by backend action metadata.

## Safety Requirements

- Render only safe labels, summaries, fingerprints, status badges, artifact references, and authorized links.
- Never render raw secrets, resolved credentials, provider tokens, authorization headers, raw provider payloads, raw prompts, raw completions, private messages, memory, connector payloads, stack traces, local paths, or unauthorized tenant labels.
- User-facing errors come from safe problem details or safe mutation results.
- Prompt previews are fixture-backed and safe before React receives them.
- Routing/profile previews are read-only; provider probes are explicit actions.

## Expected Interactions

- Platform admin opens Setup and sees provider/prompt/profile/routing readiness.
- Platform admin opens Providers, reviews credential reference status, and runs an explicit deterministic probe.
- Tenant admin opens Providers and sees only authorized catalog readiness with mutation controls unavailable.
- Admin opens Prompts, selects a deterministic prompt fixture, runs safe preview, and sees blocked/summarized unsafe preview evidence.
- Admin opens Profiles, reviews bindings, and runs read-only resolution preview.
- Admin opens Routing, submits a read-only routing preview, and receives policy reasons and remediation hints.
- Admin opens Provenance, filters policy history and run provenance, and follows authorized links.

## Accessibility And Responsiveness

- Section navigation must be keyboard accessible.
- Status badges and icon buttons must have text or aria labels.
- Tables/lists must remain readable on mobile through stacked rows or horizontal constraints.
- Loading and action states must not shift critical controls unexpectedly.
