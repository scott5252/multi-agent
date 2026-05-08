from __future__ import annotations

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"

QA058_ROUTE_PROBE_PATHS = (
    "/admin/app/migration/live-data-inventory.json",
    "/admin/app/workflows/registry.json",
    "/admin/app/governance/bootstrap.json",
    "/admin/app/skills/bootstrap.json",
    "/admin/app/test-bench/bootstrap.json",
    "/admin/app/memberships/bootstrap.json",
    "/admin/app/channels/bootstrap.json",
    "/admin/app/usage/bootstrap.json",
    "/admin/app/operations.json",
)

QA058_FORBIDDEN_RESPONSE_MARKERS = (
    "qa058-secret-value",
    "raw prompt",
    "raw completion",
    "private message",
    "raw tool payload",
    "raw test transcript",
    "/Users/",
    "Globex unauthorized",
)
