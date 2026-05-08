# Live Data Inventory Contract

## Endpoint

`GET /admin/app/migration/live-data-inventory.json`

## Purpose

Return a redaction-safe inventory of production React admin fixture/mock data findings, computed metadata allowlist entries, route response scan targets, and validation evidence for Spec 048.

## Authorization

- Platform admins may view all inventory groups.
- Tenant admins may view tenant-safe route targets and global computed metadata summaries.
- Tenant users are denied unless existing migration shell policy grants user-safe visibility.
- Cross-tenant access fails closed with safe problem details.

## Response Shape

```json
{
  "page_id": "qa048-live-data-inventory",
  "generated_at": "2026-05-07T12:00:00Z",
  "summary": {
    "total_findings": 42,
    "blocking_findings": 0,
    "mapped_legacy_findings": 42,
    "allowed_computed_metadata": 4,
    "test_only_markers": 0,
    "route_targets": 18,
    "empty_state_scans": 18,
    "seeded_state_scans": 18,
    "ci_status": "warning",
    "next_step": "Use replacement specs 049 through 058 to remove mapped legacy findings."
  },
  "findings": [],
  "allowlist": [],
  "route_targets": [],
  "evidence": [],
  "states": []
}
```

## Safety Rules

- The response must not include raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, private channel messages, raw run payloads, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, full Telegram identifiers, link tokens after creation, or unauthorized tenant labels.
- Source paths must be repository-relative.
- The endpoint must return scanner-derived evidence, computed metadata, or truthful unavailable states only.

## Error Behavior

- `401`: missing or invalid principal.
- `403`: unauthorized role or cross-tenant access.
- `404`: React admin disabled.
- `503`: scanner unavailable, with safe problem details and no stack trace.
