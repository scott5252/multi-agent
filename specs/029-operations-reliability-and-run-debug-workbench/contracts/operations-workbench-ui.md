# React Operations Workbench UI Contract

## Route

The React route is `/admin/app/operations`.

Users should enter through local login during QA:

```text
/auth/local-login?redirect_to=/admin/app/operations
```

## Primary View

The first viewport must show:

- React Admin shell context.
- Active platform or tenant scope.
- Workbench heading.
- Last-60-minutes time range.
- Highest-severity degraded card.
- Health/dependency summary.
- Queue/database pressure summary.
- Reliability summary.
- Safe links to existing Jinja fallback pages.

## Platform Operator Journey

The platform operator view shows platform-wide:

- Dependencies.
- Capacity.
- Queue pressure.
- Database pool pressure.
- Provider health.
- Channel status.
- Connector readiness.
- Reliability state.
- Latency, throughput, and error-rate trend cards.
- Redacted log summaries.
- Run debug links.
- Safe export action.

No raw log line, prompt, completion, credential value, provider payload, tool
payload, Telegram update, private message, stack trace, local path, or secret
value may appear.

## Tenant Admin Journey

The tenant admin view shows only explicitly authorized tenant-scoped:

- Tenant run health.
- Tenant delivery status.
- Tenant-visible safe run timeline summaries.
- Tenant-safe reliability categories where policy allows.
- Authorized fallback links.

Platform-only provider, queue, dependency, and shared pool details are hidden
or denied.

## Run Debug Drawer Or Panel

The run debug view shows:

- Run status and safe title.
- Timeline events.
- Graph branches.
- Join decisions.
- Gateway attempts.
- Governed tool calls.
- Channel deliveries.
- Lineage and replay links.
- Safe audit references.

The view must use plain-language labels for waiting, joined, failed, paused,
replayed, retried, and blocked states.

## Reliability Recovery Panel

The recovery panel shows:

- Breaker state.
- Retry backlog.
- Dead-letter count.
- Compensation backlog.
- Quota/lease pressure.
- Confirmation prompts for state-affecting remediation.
- Safe links to Jinja reliability fallbacks.

## Export Panel

The export panel shows:

- Export status.
- Artifact reference ID.
- Redaction summary.
- Scope.
- Expiry.
- Audit reference.

It does not show raw exported contents or filesystem paths.

## States

The UI must render:

- Loading.
- Empty.
- Filtered empty.
- Denied.
- Partial data.
- Dependency unavailable.
- Export complete.
- Export failed with safe reason.

## Screenshots Required

- Denied route.
- Platform workbench.
- Tenant-limited workbench.
- Run debug view.
- Safe export result.

## Accessibility And Layout

- Controls are keyboard reachable.
- Tables use stable columns and responsive constraints.
- Dense cards remain readable without overlapping.
- Buttons use icons where a standard icon exists.
- No in-app text explains keyboard shortcuts or implementation details.
