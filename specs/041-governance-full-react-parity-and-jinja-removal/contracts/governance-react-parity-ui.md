# UI Contract: Governance Full React Parity And Jinja Removal

## React Routes

- `/admin/app/governance`: React governance dashboard and default setup view.
- `/admin/app/governance/providers`: provider list/catalog/readiness view.
- `/admin/app/governance/providers/new`: provider create state.
- `/admin/app/governance/providers/{provider_id}`: provider detail state.
- `/admin/app/governance/providers/{provider_id}/edit`: provider edit state.
- `/admin/app/governance/providers/{provider_id}/test-results`: provider test/probe history.
- `/admin/app/governance/prompts`: prompt list state.
- `/admin/app/governance/prompts/{prompt_lineage_id}`: prompt detail state.
- `/admin/app/governance/prompts/{prompt_lineage_id}/edit`: prompt edit state.
- `/admin/app/governance/prompts/{prompt_lineage_id}/history`: prompt history state.
- `/admin/app/governance/prompts/{prompt_lineage_id}/preview`: safe prompt preview state.
- `/admin/app/governance/profiles`: profile list state.
- `/admin/app/governance/profiles/{profile_id}`: profile detail state.
- `/admin/app/governance/profiles/{profile_id}/edit`: profile edit state.
- `/admin/app/governance/profiles/{profile_id}/history`: profile history state.
- `/admin/app/governance/profiles/{profile_id}/resolve`: profile resolution state.
- `/admin/app/governance/routing`: read-only routing preview state.
- `/admin/app/governance/history`: policy and model-skill config history state.
- `/admin/app/governance/provenance/{run_id}`: run provenance state.

## JSON Contracts

- `GET /admin/app/governance/bootstrap.json`
- `GET /admin/app/governance/providers.json`
- `GET /admin/app/governance/providers/{provider_id}.json`
- `POST /admin/app/governance/providers/{provider_id}/probe`
- `POST /admin/app/governance/providers/{provider_id}/credential-reference`
- `GET /admin/app/governance/prompts.json`
- `POST /admin/app/governance/prompts/{prompt_lineage_id}/save`
- `POST /admin/app/governance/prompts/{prompt_lineage_id}/preview`
- `GET /admin/app/governance/profiles.json`
- `POST /admin/app/governance/profiles/{profile_id}/save`
- `POST /admin/app/governance/profiles/{profile_id}/resolve`
- `POST /admin/app/governance/routing/preview`
- `GET /admin/app/governance/history.json`
- `GET /admin/app/governance/provenance/{run_id}.json`
- `GET /admin/app/governance/legacy-routes.json`

## Legacy Browser Redirects

- `/admin/model-providers` redirects to `/admin/app/governance/providers`.
- `/admin/model-providers/new` redirects to `/admin/app/governance/providers/new`.
- `/admin/model-providers/catalog` redirects to `/admin/app/governance/providers`.
- `/admin/model-providers/{provider_id}` redirects to `/admin/app/governance/providers/{provider_id}`.
- `/admin/model-providers/{provider_id}/edit` redirects to `/admin/app/governance/providers/{provider_id}/edit`.
- `/admin/prompt-runtime/prompts` redirects to `/admin/app/governance/prompts`.
- `/admin/prompt-runtime/prompts/new` redirects to `/admin/app/governance/prompts/new`.
- `/admin/prompt-runtime/prompts/versions/{prompt_version_id}` redirects to `/admin/app/governance/prompts/versions/{prompt_version_id}`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/edit`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/history` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/history`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/preview`.
- `/admin/prompt-runtime/profiles` redirects to `/admin/app/governance/profiles`.
- `/admin/prompt-runtime/profiles/new` redirects to `/admin/app/governance/profiles/new`.
- `/admin/prompt-runtime/profiles/versions/{profile_version_id}` redirects to `/admin/app/governance/profiles/versions/{profile_version_id}`.
- `/admin/prompt-runtime/profiles/{profile_id}/edit` redirects to `/admin/app/governance/profiles/{profile_id}/edit`.
- `/admin/prompt-runtime/profiles/{profile_id}/history` redirects to `/admin/app/governance/profiles/{profile_id}/history`.
- `/admin/prompt-runtime/profiles/resolve` redirects to `/admin/app/governance/profiles/resolve`.
- `/admin/config/ui` redirects to `/admin/app/governance/routing`.
- `/admin/config/ui/history` redirects to `/admin/app/governance/history`.
- `/admin/config/ui/runs/{workflow_run_id}/provenance` redirects to `/admin/app/governance/provenance/{workflow_run_id}` when a safe run id is present.

## Required States

- Loading.
- Empty authorized section.
- Denied unauthenticated or unauthorized route.
- Cross-tenant safe problem.
- Provider missing credential, invalid credential, degraded, breaker-open, probe failed, probe unavailable.
- Prompt preview rendered, summarized, blocked, denied, unavailable.
- Profile resolution allowed, fallback, denied, unavailable.
- Routing preview allowed, fallback, denied, unavailable.
- Policy/history/provenance bounded filters and empty states.
- Legacy route redirected, converted, gone, retained with blocker.

## Safety Requirements

- Render only safe labels, summaries, fingerprints, status badges, artifact references, and authorized links.
- Never render raw secrets, resolved credentials, provider tokens, authorization headers, provider request/response bodies, raw prompts, raw completions, private messages, memory, connector payloads, stack traces, local paths, or unauthorized tenant labels.
- Prompt previews are safe before React receives them.
- Routing/profile previews are read-only.
- Provider probes are explicit mocked-safe actions in QA.
