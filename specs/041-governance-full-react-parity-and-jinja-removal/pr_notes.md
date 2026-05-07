# PR Notes: Spec 041 Governance React Parity And Jinja Removal

## Summary

Spec 041 moves governance browser journeys for providers, prompts, runtime
profiles, model-skill routing, policy history, and run provenance into the
React admin workspace at `/admin/app/governance`. The old governance browser
URLs now issue authenticated redirects to stable React routes, while JSON APIs
and legacy form posts remain backend-owned for authorization, tenancy,
validation, stale-state behavior, and redaction.

## Deleted

- `src/multi_agent_platform/web_admin/templates/model_providers/index.html`
- `src/multi_agent_platform/web_admin/templates/model_providers/detail.html`
- `src/multi_agent_platform/web_admin/templates/model_providers/edit.html`
- `src/multi_agent_platform/web_admin/templates/model_providers/catalog.html`
- `src/multi_agent_platform/web_admin/templates/model_providers/test_results.html`
- `src/multi_agent_platform/web_admin/templates/prompts/index.html`
- `src/multi_agent_platform/web_admin/templates/prompts/detail.html`
- `src/multi_agent_platform/web_admin/templates/prompts/edit.html`
- `src/multi_agent_platform/web_admin/templates/prompts/history.html`
- `src/multi_agent_platform/web_admin/templates/prompts/preview.html`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/index.html`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/detail.html`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/history.html`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html`
- `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html`
- `src/multi_agent_platform/web_admin/templates/model_skill_config/history.html`
- `src/multi_agent_platform/web_admin/templates/model_skill_config/run_provenance.html`

## Redirected Or Converted

- `/admin/model-providers` redirects to `/admin/app/governance/providers`.
- `/admin/model-providers/new` redirects to `/admin/app/governance/providers/new`.
- `/admin/model-providers/catalog` redirects to `/admin/app/governance/providers`.
- `/admin/model-providers/{connection_id}` redirects to `/admin/app/governance/providers/{connection_id}`.
- `/admin/model-providers/{connection_id}/edit` redirects to `/admin/app/governance/providers/{connection_id}/edit`.
- `/admin/prompt-runtime/prompts` redirects to `/admin/app/governance/prompts`.
- `/admin/prompt-runtime/prompts/new` redirects to `/admin/app/governance/prompts/new`.
- `/admin/prompt-runtime/prompts/versions/{prompt_version_id}` redirects to `/admin/app/governance/prompts/versions/{prompt_version_id}`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/edit`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/history` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/history`.
- `/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview` redirects to `/admin/app/governance/prompts/{prompt_lineage_id}/preview`.
- `/admin/prompt-runtime/profiles` redirects to `/admin/app/governance/profiles`.
- `/admin/prompt-runtime/profiles/new` redirects to `/admin/app/governance/profiles/new`.
- `/admin/prompt-runtime/profiles/versions/{agent_profile_version_id}` redirects to `/admin/app/governance/profiles/versions/{agent_profile_version_id}`.
- `/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/edit` redirects to `/admin/app/governance/profiles/{agent_runtime_profile_id}/edit`.
- `/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/history` redirects to `/admin/app/governance/profiles/{agent_runtime_profile_id}/history`.
- `/admin/prompt-runtime/profiles/resolve` redirects to `/admin/app/governance/profiles/resolve` and preserves safe tenant, agent key, and agent kind query values.
- `/admin/config/ui` redirects to `/admin/app/governance/routing`.
- `/admin/config/ui/history` redirects to `/admin/app/governance/history`.
- `/admin/config/ui/runs/{workflow_run_id}/provenance` redirects to `/admin/app/governance/provenance/{workflow_run_id}`.
- Legacy provider, prompt, and profile form posts still execute backend services and then redirect to React destinations or return safe HTTP problems.

## Retained With Evidence

- `src/multi_agent_platform/api/ui/model_providers.py`
- `src/multi_agent_platform/api/ui/prompts.py`
- `src/multi_agent_platform/api/ui/agent_profiles.py`
- `src/multi_agent_platform/api/ui/model_skill_config.py`

These helper modules remain because they are still covered by historical view
model tests, fixture compatibility, or migration inventory evidence used by
later Jinja infrastructure work. No active Spec 041 browser router imports them
to render governance templates.

## React Parity Evidence

- Governance dashboard contracts now include a backend-owned legacy route mapping ledger.
- React governance renders provider readiness, credential references, prompt previews, runtime profile resolution, routing preview, policy history, run provenance, and legacy redirect evidence.
- The React SPA fallback accepts `/admin/app/governance` child routes so old direct links can land on stable React destinations.
- Admin navigation, workflow builder reference links, operations links, and docs point at React governance destinations.
- Backend tests cover old route redirects, form-post compatibility, schema redaction, route scanners, and React contract shape.
- Frontend tests and the production React build cover the governance page and component rendering.

## Review Focus

- Confirm no governance-owned template file remains under `model_providers`, `prompts`, `agent_profiles`, or `model_skill_config`.
- Confirm old governance browser routes return 303 redirects or safe HTTP problems, not TemplateResponse.
- Confirm legacy query preservation only keeps safe tenant, filter, status, revision, agent, config kind, and run id values.
- Confirm platform-admin-only provider mutations remain denied for tenant principals.
- Confirm tenant principals can still read authorized governance summaries without seeing cross-tenant data.
- Confirm screenshots, logs, QA docs, and route responses contain no raw secrets, credential values, raw prompts, raw completions, raw provider payloads, stack traces, local filesystem paths, or unauthorized tenant labels.

## Rollback

If React governance parity fails, restore only the affected governance templates
and the matching browser route handlers from git, keep the React JSON APIs
intact, and mark the affected inventory entries retained with blockers. Do not
restore shared shell templates, unrelated admin templates, or global Jinja
infrastructure as part of the Spec 041 rollback.
