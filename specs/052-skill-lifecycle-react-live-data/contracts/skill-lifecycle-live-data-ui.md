# UI Contract: Skill Lifecycle React Live Data

## Route Family

- `GET /admin/app/skills`
- `GET /admin/app/skills/bootstrap.json`
- `GET /admin/app/skills/legacy-routes.json`
- `POST /admin/app/skills/packages/candidates`
- `POST /admin/app/skills/packages/candidates/{candidate_id}/validate`
- `POST /admin/app/skills/packages/candidates/{candidate_id}/publish`
- `POST /admin/app/skills/packages/{package_id}/grants`
- `POST /admin/app/skills/packages/{package_id}/quarantine`
- `POST /admin/app/skills/packages/{package_id}/withdraw`
- `GET /admin/app/skills/discovery.json`
- `GET /admin/app/skills/installations.json`
- `POST /admin/app/skills/installations/{installation_id}/install`
- `POST /admin/app/skills/installations/{installation_id}/credentials`
- `POST /admin/app/skills/installations/{installation_id}/smoke-tests`
- `GET /admin/app/skills/diagnostics.json`
- `POST /admin/app/skills/diagnostics/run`
- `POST /admin/app/skills/eligibility/preview`
- `POST /admin/app/skills/installations/{installation_id}/eligibility/preview`
- `GET /admin/app/skills/audit.json`

## Response Provenance

Every JSON response must allow the UI and QA reviewers to identify one of these states:

- `live_repository`: data came from authorized durable skill lifecycle records.
- `computed_system`: data is computed from route inventory, generated contracts, or runtime metadata and is not fake domain data.
- `empty`: no authorized live records exist for the active scope.
- `denied`: the principal cannot access the requested scope or action.
- `blocked`: a package, install, credential, policy, quarantine, or withdrawal state prevents progress.
- `stale`: a submitted revision token does not match the durable current revision.
- `unavailable`: the evidence has not been generated or cannot be safely summarized.

## Empty-State Contract

Fresh QA databases must show no package, candidate, grant, discovery, installation, credential, readiness, diagnostic, eligibility, quarantine, withdrawal, or audit rows unless those records have been seeded through documented flows. Empty panels must include a short title, summary, and optional safe setup action.

## Safe Detail Contract

Skill lifecycle details may render:

- package and version identifiers
- safe manifest summaries and digests
- validation status and safe findings
- artifact reference ids
- credential reference ids and fingerprints
- smoke-test status and safe summaries
- connector readiness and policy summaries
- lifecycle state and audit references

Skill lifecycle details must not render:

- raw manifests
- credential values
- provider authorization headers
- raw connector request or response payloads
- raw tool outputs
- raw validation or smoke-test transcripts
- private tenant labels
- local filesystem paths
- stack traces

## Safe Mutation Contract

Safe skill lifecycle mutations must return:

- status (`accepted`, `completed`, `validation_error`, `stale_conflict`, `rejected`, `unavailable`, `denied`, or `blocked`)
- safe summary
- persisted revision, package id, installation id, job id, or audit reference when applicable
- backend-owned refresh target
- safe field errors for invalid input
- no raw manifest, credential, connector payload, test transcript, or local path

## Playwright Contract

The QA052 Playwright flow must:

1. Log in with a local principal that is authorized for the chosen safe action.
2. Open `/admin/app/skills`.
3. Verify an honest empty state or live seeded records.
4. Perform one safe user-visible skill lifecycle action that persists through backend services.
5. Verify the saved state is visible after refresh or through a backend result.
6. Capture a screenshot under `output/playwright/qa052_ui/`.

Post-UI verification must query a backend skill lifecycle API first and use a direct QA database query only for redaction-safe persistence evidence.
