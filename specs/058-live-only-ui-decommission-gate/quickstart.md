# Quickstart: Live-Only UI Decommission Gate

## Purpose

Use this quickstart to validate that production admin UI routes no longer
return backend-generated deterministic fixture/demo data. The gate must prove
both truthful empty states and seeded live-data behavior before Spec 058 can be
marked complete.

## Current Inventory Baseline

The implementation starts from these live-only gate files:

- `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
  owns source scanning, route targets, marker policy, computed-metadata
  allowlists, and missed-route detection.
- `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`
  owns the migration dashboard summary, route decisions, rollback guidance, and
  embedded live-data inventory projection.
- `src/multi_agent_platform/api/routers/admin_react.py` owns the admin
  migration JSON routes and currently exposes `/admin/app/migration/live-data-inventory.json`.
- `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`
  renders live-data guardrail counts, findings, route targets, and evidence.
- `tests/unit/admin/test_live_data_inventory_scanner.py` and
  `tests/integration/api/test_admin_live_data_inventory_routes.py` are the
  primary scanner and route-response guardrail tests.

Read-only analysis before implementation reported zero blocking scanner
findings, zero missed static admin JSON routes, and one mapped transitional
bootstrap QA marker deferred to Spec 059.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   npm --prefix frontend/admin install
   ```

2. Apply migrations to the active QA database through the Spec QA runner rather
   than manually dropping unrelated databases.

3. Use the Spec 058 QA environment file:

   ```bash
   cp specs/058-live-only-ui-decommission-gate/.env.qa058 .env
   ```

## Expected QA Artifacts

- `specs/058-live-only-ui-decommission-gate/.env.qa058`
- `specs/058-live-only-ui-decommission-gate/qa058.md`
- `specs/058-live-only-ui-decommission-gate/qa058_ui.md`
- `specs/058-live-only-ui-decommission-gate/qa058_user_guide.md`
- `specs/058-live-only-ui-decommission-gate/pr_notes.md`
- `.data/qa058-artifacts/`
- `output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png`
- `.data/curl_test_runs/qa058-after-spec/`

## Validation Commands

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/058-live-only-ui-decommission-gate
```

Run Spec QA:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml
```

Run Playwright UI validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml --start-processes
```

Run post-UI verification:

```bash
uv run python scripts/qa/verify_live_only_gate_qa058.py
```

Run the post-spec curl regression:

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa058-after-spec
```

## Manual Review Checklist

- The live-data inventory reports zero blocking production-reachable findings.
- Route targets cover the production admin UI surfaces converted in Specs 050
  through 057.
- Empty-state probes do not invent domain rows.
- Seeded-state probes trace representative rows to persisted QA data or allowed
  computed metadata.
- Built production assets do not include user-visible fake domain rows.
- Test fixtures and QA seed markers are present only in allowed test, QA, docs,
  validation, or historical-spec boundaries.
- Reviewer notes explain deleted/disconnected surfaces and rollback guidance.

## Rollback Guidance

If the gate exposes a false positive, narrow the scanner policy to the specific
safe boundary and rerun the source scan, built-asset scan, route response scan,
Playwright validation, post-UI verifier, and curl regression. Do not reintroduce
production fixture data or a runtime demo-data flag as rollback.
