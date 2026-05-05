# PR Notes: Spec 035 React Usage And Cost Analytics

## Summary

Spec 035 adds the React usage and cost analytics workspace at `/admin/app/usage`.

The feature includes backend-owned dashboard projections, safe usage schemas, generated TypeScript contracts, React summary/trend/rollup/drilldown/export components, protected API routes, and deterministic QA035 validation evidence.

## Reviewer Focus

- Verify platform administrators can review authorized cross-tenant usage summaries.
- Verify tenant administrators see only their active tenant usage, rollups, events, and exports.
- Verify rollups cover Spec 016 dimensions plus graph node, gateway operation, physical attempt, and governed tool attribution.
- Verify event drilldowns and exports never render raw prompts, completions, memory content, secrets, provider credentials, credential internals, raw tool payloads, local paths, or unauthorized tenant data.
- Verify the existing `/admin/usage` fallback remains available.

## Validation

- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `uv run pytest --no-cov tests/unit/api/test_admin_usage_react_schema.py tests/unit/admin/usage/test_react_usage_service.py tests/performance/usage/test_react_usage_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py`
- `cd frontend/admin && npm run typecheck && npm run test && npm run build`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/035-react-usage-and-cost-analytics`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml --start-processes`

## Evidence

- API evidence writes to `/tmp/qa035-*`.
- Browser screenshots write to `output/playwright/qa035_ui`.
- Manual reviewer guidance is in `qa035_user_guide.md`.
- API and database QA guidance is in `qa035.md`.
- Browser QA guidance is in `qa035_ui.md`.
