# QA058 UI Walkthrough: Live-Only UI Decommission Gate

## Goal

Use the browser to prove the migration live-data inventory panel is backed by
the QA058 gate state and does not show backend-generated fixture rows as if
they were production data.

## How To Use This Guide

Follow this guide after the QA058 database has been migrated and seeded. Keep
browser evidence in `output/playwright/qa058_ui`, and save reviewer notes under
`/tmp/qa058-ui-notes.md` if a manual reviewer needs a scratch file.

What is happening: the browser signs in with a local-principal platform admin.

Why this matters: the UI should show backend-owned live-only gate evidence, not
client-side fixture replacements.

## Environment Setup

Copy the QA env file:

```bash
cp specs/058-live-only-ui-decommission-gate/.env.qa058 .env
```

Expected: `.env.qa058` is the active environment file.

Start dependencies:

```bash
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_live_only_gate_qa058.py
```

Expected: seed output includes `Seeded QA058 live-only gate records`.

Start the app:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

## Browser Walkthrough

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration`.
2. Choose the `platform-admin` local principal.
3. Wait for the migration dashboard to load.
4. Locate the `Live-data guardrails` panel.
5. Confirm the panel eyebrow reads `Live-only gate`.
6. Confirm CI status is visible.
7. Confirm `Blocking` count is zero.
8. Confirm `Mapped/deferred` count is one.
9. Confirm `Route targets` are listed.
10. Confirm `qa058-live-only-source-scan` appears in evidence.
11. Confirm the next step mentions Spec 059 for the transitional bootstrap marker.
12. Capture a screenshot.

Expected: `Live-data guardrails` is visible.

Expected: `Live-only gate` is visible.

Expected: `qa058-live-only-source-scan` is visible.

Expected: `Route targets` is visible.

Expected: the UI does not show `/Users/`.

Expected: the UI does not show raw prompts, raw completions, or private messages.

What is happening: the migration dashboard loads backend JSON and renders the
embedded live-data inventory projection.

Why this matters: the panel must stay useful even when the full source scan is
performed separately by API validation.

## Source Scan API Spot Check

Use the browser address bar or a terminal:

```bash
curl --fail --silent -H 'X-Local-Principal: platform-admin' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?ci_mode=true'
```

Expected: response includes `qa058-live-only-gate`.

Expected: response includes `"blocking_findings":0`.

Expected: response includes `"mapped_legacy_findings":1`.

What is happening: the source scan endpoint performs the production scanner path.

Why this matters: the UI projection and source scan must agree on zero blockers.

## Tenant Projection Spot Check

Run:

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?tenant_id=11111111-1111-1111-1111-111111111111&source_scan=false'
```

Expected: response includes `qa058-live-only-gate`.

Expected: response excludes `Globex`.

What is happening: tenant mode verifies scoped access.

Why this matters: a live-only gate cannot leak another tenant while proving mock-data removal.

## Cross-Tenant Negative Walkthrough

Run:

```bash
status=$(curl --silent --output /tmp/qa058-ui-cross-tenant.json --write-out '%{http_code}' \
  -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?tenant_id=22222222-2222-2222-2222-222222222222')
printf '%s\n' "$status"
```

Expected: status is `403`.

Expected: `/tmp/qa058-ui-cross-tenant.json` does not include `Globex`.

What is happening: the backend rejects a mismatched tenant request.

Why this matters: route probes must prove authorization, not only source cleanup.

## Required Automated Evidence

Run Playwright:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml --start-processes
```

Expected: screenshot `output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png` exists.

Run document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/058-live-only-ui-decommission-gate
```

Expected: QA document validation passes.

Run backend validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml
```

Expected: source scan, projected scan, cross-tenant denial, and verifier commands pass.

Run quality commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all four quality commands pass.

## UI Evidence Checklist

- Screenshot shows the migration dashboard.
- Screenshot shows `Live-data guardrails`.
- Screenshot shows `Live-only gate`.
- Screenshot shows `Route targets`.
- Screenshot shows `qa058-live-only-source-scan`.
- Reviewer notes include the browser URL.
- Reviewer notes include the active principal.
- Reviewer notes include the zero-blocker summary.
- Reviewer notes include the Spec 059 deferred marker note.
- Reviewer notes include the screenshot path.

Expected: no screenshot exposes a local filesystem path.

Expected: no screenshot exposes raw secret, prompt, completion, message, or tool payload text.

## Acceptance Notes Template

```text
QA058 UI route: /admin/app/migration
QA058 principal: platform-admin
QA058 visible panel: Live-data guardrails
QA058 visible evidence: qa058-live-only-source-scan
QA058 visible route section: Route targets
QA058 screenshot: output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png
QA058 redaction: pass
QA058 tenant isolation: pass
```

Expected: acceptance notes use repository-relative evidence paths.

## Troubleshooting

- If login fails, confirm `AUTH_MODE=local_principal`.
- If the migration page is unavailable, check `/tmp/qa058-api.log`.
- If the panel is missing, verify `/admin/app/migration/bootstrap.json` returns `live_data_inventory`.
- If evidence text is stale, rerun the frontend build and generated type check.
- If source scan is slow, confirm it is scanning only configured production roots.
- If cross-tenant denial includes another tenant label, stop and fix the route guard.

Expected: troubleshooting stays within QA058 local resources.

## Related Files

- `specs/058-live-only-ui-decommission-gate/.env.qa058`
- `specs/058-live-only-ui-decommission-gate/qa058.md`
- `specs/058-live-only-ui-decommission-gate/qa058_user_guide.md`
- `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`
- `output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png`
