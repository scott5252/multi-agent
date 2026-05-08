# UI Contract: Governance React Live Data

## Route Family

- `GET /admin/app/governance`
- `GET /admin/app/governance/bootstrap.json`
- `GET /admin/app/governance/providers.json`
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

## Response Provenance

Every JSON response must allow the UI and QA reviewers to identify one of these states:

- `live_repository`: data came from authorized durable governance records.
- `computed_system`: data is computed from route inventory, generated contracts, or runtime metadata and is not fake domain data.
- `empty`: no authorized live records exist for the active scope.
- `denied`: the principal cannot access the requested scope or action.
- `unavailable`: the evidence has not been generated or cannot be safely summarized.

## Empty-State Contract

Fresh QA databases must show no provider, prompt, profile, routing, policy, diagnostic, or provenance rows unless those records have been seeded through documented flows. Empty panels must include a short title, summary, and optional safe setup action.

## Safe Mutation Contract

Safe governance mutations must return:

- status (`accepted`, `completed`, `rejected`, `unavailable`, or `conflict`)
- safe summary
- persisted revision or record id when applicable
- backend-owned refresh target
- safe audit reference when available
- field errors for invalid input
- no raw secret, prompt, completion, provider payload, or local path

## Playwright Contract

The QA051 Playwright flow must:

1. Log in as `tenant-admin-acme`.
2. Open `/admin/app/governance`.
3. Verify an honest empty state or live seeded records.
4. Perform one safe user-visible governance save action that persists through backend services.
5. Verify the saved state is visible after refresh.
6. Capture a screenshot under `output/playwright/qa051_ui/`.

Post-UI verification must query a backend governance API first and use a direct QA database query only for redaction-safe persistence evidence.
