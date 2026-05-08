# Quickstart: Admin UI Transitional React Label Removal

## Goal

Verify Spec 059 removes implementation-era React wording from production-visible
admin UI copy while preserving allowed implementation context.

## Expected Artifacts

- `specs/059-admin-ui-transitional-react-label-removal/.env.qa059`
- `specs/059-admin-ui-transitional-react-label-removal/qa059.md`
- `specs/059-admin-ui-transitional-react-label-removal/qa059_ui.md`
- `specs/059-admin-ui-transitional-react-label-removal/qa059_user_guide.md`
- `specs/059-admin-ui-transitional-react-label-removal/pr_notes.md`
- `.data/qa059-artifacts/transitional-label-gate-report.json`
- `output/playwright/qa059_ui/qa059-admin-entry.png`
- `output/playwright/qa059_ui/qa059-domain-pages.png`
- `.data/curl_test_runs/qa059-after-spec/`

## Setup

```bash
cp specs/059-admin-ui-transitional-react-label-removal/.env.qa059 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa059 && createdb -U postgres multi_agent_platform_qa059'
uv run alembic upgrade head
uv run python scripts/qa/seed_transitional_labels_qa059.py
```

## Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/059-admin-ui-transitional-react-label-removal
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml --start-processes
uv run python scripts/qa/verify_transitional_labels_qa059.py
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa059-after-spec
```

## Manual Review

1. Open `/admin/app` as a platform administrator.
2. Confirm the shell title, browser title, breadcrumbs, navigation, and command
   labels use product terminology.
3. Open representative tenant pages.
4. Confirm empty, unavailable, denied, and error states do not expose
   transitional product labels.
5. Open migration evidence as a platform reviewer.
6. Confirm any remaining implementation wording is explicitly technical
   evidence and not ordinary product copy.

## Baseline Inventory Recorded During Implementation

- `src/multi_agent_platform/api/routers/admin_react.py`: fallback HTML,
  shell breadcrumbs, bootstrap version metadata, disabled-route copy, and audit
  error strings previously exposed implementation-era wording.
- `src/multi_agent_platform/api/schemas/admin_react.py` and
  `src/multi_agent_platform/api/schemas/admin_patterns.py`: safe validation
  errors previously named implementation contracts.
- `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`:
  the final mapped live-only marker was owned by Spec 059 and is now retired.
- `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`:
  route parity, rollback, performance, and state evidence now uses Admin
  product terminology while retaining historical evidence ids.
- `frontend/admin/src/App.tsx`, `frontend/admin/src/main.tsx`, and
  `frontend/admin/src/api/client.ts`: unavailable and request-failure states now
  use Admin terminology.
- `frontend/admin/src/components/`: shell, sidebar, migration hardening,
  workflow creation, user-run, and test-bench compatibility messages now avoid
  product-label leakage.
- `frontend/admin/src/test/`: QA-visible fixture labels now match the Admin
  terminology expected in screenshots and component tests.
