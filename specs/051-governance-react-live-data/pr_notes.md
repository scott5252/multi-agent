# PR Notes: QA051 Governance React Live Data

## Summary

- Replaced deterministic governance React builders with live repository-backed provider, prompt, profile, routing, policy, provenance, empty-state, and unavailable-state projections.
- Added nullable governance dashboard fields, live provenance metadata, empty-state metadata, and generated TypeScript contract updates.
- Wired governance routes to async provider, prompt, profile, and model-skill repositories with safe provider probe, credential metadata, prompt preview, prompt save, profile save, profile resolve, and routing preview actions.
- Updated governance React panels to render live, empty, unavailable, and mutation result states without assuming fixed QA031 rows.
- Added QA051 seed and verification scripts so Playwright performs a real prompt save and post-UI validation proves the persisted revision.

## Validation

- `uv run ruff check src/multi_agent_platform/admin/governance.py src/multi_agent_platform/api/schemas/admin_governance.py src/multi_agent_platform/api/routers/admin_react.py scripts/frontend/generate_admin_react_types.py scripts/qa/seed_governance_qa051.py scripts/qa/verify_governance_qa051.py tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_service.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/governance/test_governance_queries.py`
- `uv run ruff format --check src/multi_agent_platform/admin/governance.py src/multi_agent_platform/api/schemas/admin_governance.py src/multi_agent_platform/api/routers/admin_react.py scripts/frontend/generate_admin_react_types.py scripts/qa/seed_governance_qa051.py scripts/qa/verify_governance_qa051.py tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_service.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/governance/test_governance_queries.py`
- `uv run mypy src/multi_agent_platform/admin/governance.py src/multi_agent_platform/api/schemas/admin_governance.py src/multi_agent_platform/api/routers/admin_react.py`
- `uv run pytest tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_service.py tests/integration/test_admin_react_routes.py::test_react_admin_governance_platform_tenant_and_auth0_are_safe tests/integration/test_admin_react_routes.py::test_react_admin_governance_actions_are_safe_and_scoped tests/contract/test_admin_react_contract.py tests/unit/admin/test_live_data_inventory_scanner.py tests/performance/governance/test_governance_queries.py -q --no-cov`
- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `npm run --prefix frontend/admin typecheck`
- `npm run --prefix frontend/admin test -- --run src/components/governance/GovernancePage.test.tsx src/components/governance/ProviderGovernancePanel.test.tsx src/components/governance/PromptGovernancePanel.test.tsx src/components/governance/ProfileGovernancePanel.test.tsx src/components/governance/RoutingPreviewPanel.test.tsx src/components/governance/ProvenancePanel.test.tsx`
- `npm run --prefix frontend/admin build`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/051-governance-react-live-data`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml --start-processes`
- `uv run python scripts/qa/verify_governance_qa051.py`
- `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa051-after-spec`

## Reviewer Focus

- Confirm platform and tenant governance routes return live persisted data or truthful empty states.
- Confirm prompt save and preview actions return safe backend evidence and never raw prompt or completion text.
- Confirm Globex cannot see Acme seeded prompt evidence.
- Confirm scanner guardrails fail on governance QA031 markers outside test-only or historical spec paths.
- Confirm the dirty worktree is intentionally preserved for the multi-spec autopilot run and no commit is required between specs.
