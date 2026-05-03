Generate ordered, test-first tasks for the operations
console. Include tests for health aggregation, dependency status mapping,
worker/queue metrics, DB pool pressure display, model provider status
display, Telegram status display, reliability state links, usage
throughput panels, log filtering by
trace/run/tenant/component/severity/time, redaction, export
authorization, tenant-scope denial, platform-admin access, auditor
read-only access, UI rendering, and performance of bounded time-range
queries. Include implementation tasks under operations/,
api/routers/admin_operations.py, api/schemas/operations.py, optional
db/models/operations.py and repositories, web_admin/templates/operations,
auth policy entries, docs, PR review notes, testing instructions, and
README updates.
