# PR Notes: Spec 031 - Model, Prompt, Profile, And Provider Governance

## Summary

Implemented the React governance page at `/admin/app/governance`.

Added backend-owned governance contracts for provider setup, credential references, prompt summaries, safe prompt previews, runtime profiles, profile resolution, routing previews, policy history, and run provenance.

Added generated TypeScript contracts and React client helpers for governance data and mutations.

Added React panels for setup and health, credential diagnostics, prompt safe previews, runtime profile resolution, routing preview, policy history, and provenance.

Preserved existing Jinja/model, prompt, profile, provider, and configuration routes.

## Safety Notes

No live provider, Telegram, credential-store, or connector calls are used by QA031.

Provider probes are explicit mocked actions and remain platform-admin only.

Credential diagnostics render safe secret-reference metadata and fingerprints only.

Tenant admins receive provider readiness without provider mutation actions.

Prompt preview output is summarized before React rendering when unsafe fixture content is requested.

Routing previews are read-only policy evaluations and preserve ModelGateway-only execution evidence.

Cross-tenant requests fail closed before rendering governance data.

Raw secrets, resolved credential values, authorization headers, provider tokens, raw prompts, raw completions, provider payloads, private messages, memory contents, connector payloads, stack traces, and local paths are blocked by schema validation and are not rendered in React fixtures.

## Focused Validation

- `uv run python scripts/frontend/generate_admin_react_types.py --check` - passed.
- `uv run pytest --no-cov tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_service.py tests/performance/governance/test_governance_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` - passed, 30 tests.
- `cd frontend/admin && npm run typecheck` - passed.
- `cd frontend/admin && npm run test` - passed, 44 tests.
- `cd frontend/admin && npm run build` - passed.
- `uv run ruff check src/multi_agent_platform/api/schemas/admin_governance.py src/multi_agent_platform/admin/governance.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/auth/policy.py tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_service.py tests/performance/governance/test_governance_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` - passed.
- `uv run mypy src` - passed.

## Full Validation

- QA documents: `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/031-model-prompt-profile-and-provider-governance` - passed.
- Spec QA: `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml` - passed.
- Playwright UI validation: `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml --start-processes` - passed.
- Screenshot and artifact safety scan: `rg -i "qa031-secret-value|authorization header|provider token|raw prompt|raw completion|raw provider|/Users/|Globex" /tmp/qa031-*.json output/playwright/qa031_ui || true` - no matches.
- Screenshot evidence:
  - `output/playwright/qa031_ui/qa031-react-governance-denied.png`
  - `output/playwright/qa031_ui/qa031-react-governance-platform.png`
  - `output/playwright/qa031_ui/qa031-react-governance-tenant.png`
  - `output/playwright/qa031_ui/qa031-react-governance-prompt-preview.png`
  - `output/playwright/qa031_ui/qa031-react-governance-profile-routing.png`
  - `output/playwright/qa031_ui/qa031-react-governance-cross-tenant.png`
