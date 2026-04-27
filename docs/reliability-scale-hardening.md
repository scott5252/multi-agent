# Reliability Scale Hardening

This guide covers the reliability controls added for tenant-aware admission,
quotas, fair scheduling, worker recovery, retries, circuit breakers,
compensation, dead letters, artifact throughput, and safe operational
inspection.

## Inspecting State

Operators inspect current state through `/admin/reliability/dashboard` and the
bounded list endpoints for admission decisions, policies, retries, breakers,
compensations, and dead letters. Tenant operators must keep `tenant_id` scoped
to their tenant. Auditors can inspect authorized scopes but cannot mutate
controls.

## Backpressure And Quotas

Admission outcomes are explicit: accepted, queued, delayed, throttled,
rejected, or retry-eligible. Quota exhaustion and database pool pressure are
recorded with safe reason codes so incident responders can distinguish tenant
budget pressure from shared-capacity pressure.

## Recovery And Compensation

Worker recovery requires pinned bundle metadata and lease fencing tokens.
Unknown or non-repeatable side-effect state routes to operator intervention.
Declared compensation hooks are requested at most once automatically and then
tracked through retry, success, failure, timeout, or manual follow-up states.

## Breakers And Dead Letters

Circuit breakers protect dependencies and artifact operations. Open breakers
block unsafe work until cooldown and probe evidence allow half-open trial
traffic. Automated recovery stops at dead letters when retry budgets are
exhausted, recovery safety is unknown, compensation is unavailable, or artifact
evidence cannot be generated safely.

## Incident Escalation

Representative next actions:

- Queue delay from pool pressure: preserve admin reserve, inspect pool wait,
  and avoid worker scale-out until reserve recovers.
- Submitted-work quota exhausted: inspect tenant budget and either wait for the
  window to reset or apply an audited tenant policy change.
- Active-work quota full: keep new work queued and inspect long-running leases.
- Fairness burst debt: let debt repay before increasing tenant weight.
- Worker stale write: verify fencing suppression and continue with recovered
  lease owner.
- Unknown side effect: keep work paused for operator intervention.
- Retry deadline exhausted: inspect retry history and dead-letter latest state.
- Breaker open: check dependency health and only reset with reason and probe
  evidence.
- Compensation timeout: route to manual follow-up or dead letter.
- Artifact export throttled: inspect object-store breaker and partial metadata.

