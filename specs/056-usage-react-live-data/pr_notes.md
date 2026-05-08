# Reviewer Notes: Spec 056 Usage React Live Data

## Scope

Spec 056 replaces deterministic usage analytics React payloads with live
repository and service-backed projections for usage totals, trend buckets,
rollups, event drilldowns, confidence states, tenant labels, and durable export
request evidence.

## Implementation Notes

- Usage dashboard builders now require `UsageRepository` and
  `UsageAnalyticsService` inputs and no longer carry production `USAGE_EVENTS`
  fixture rows.
- Usage routes now construct live dependencies from the request session and
  application container before calling async builders.
- Repository helpers provide bounded recent export listings and authorized
  tenant label lookups for live rollups.
- Export creation now persists `usage_export_requests` rows through
  `UsageAnalyticsService.create_csv_export()` and returns `usage-export:<id>`
  references instead of storage URLs.
- QA056 seed data persists Acme usage and export rows while leaving Globex
  empty for isolation checks.
- Scanner guardrails now treat old usage fixture markers as blocking
  regressions in production usage surfaces.

## QA Notes

- QA environment: `specs/056-usage-react-live-data/.env.qa056`
- Seed script: `scripts/qa/seed_usage_qa056.py`
- Post-UI verifier: `scripts/qa/verify_usage_qa056.py`
- Main browser route: `/admin/app/usage`
- Playwright action: sign in as `tenant-admin-acme`, click `Export CSV`, verify
  a completed `usage-export:` artifact reference, and confirm the verifier sees
  a new completed export row with checksum metadata.

## Safety Notes

- No real provider calls are used.
- No external connectors or Telegram calls are used.
- QA secrets use the `qa056/` static reference prefix.
- Browser and API output must not include raw prompts, raw completions, memory
  payloads, authorization headers, credential values, storage file URIs, local
  filesystem paths, stack traces, or unauthorized tenant usage rows.

## Commit Notes

No intermediate commit is required for this spec. The autopilot is intentionally
continuing in the dirty worktree until the full remove-mock-data sequence is
complete and the user commits.
