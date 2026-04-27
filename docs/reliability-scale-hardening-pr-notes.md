# Reliability Scale Hardening PR Notes

## Scale Assumptions

The implementation is scoped to one regional PostgreSQL cluster with
application-level fair scheduling and bounded async database pools. Large
replay, load-test, and export payloads remain in object storage; PostgreSQL
stores metadata and safe summaries only.

## Guarantees

- Admission outcomes are explicit and audit-visible.
- Quotas and fairness prevent one tenant from exhausting shared capacity.
- Lease fencing suppresses stale worker writes.
- Non-repeatable ambiguous side effects require intervention.
- Retry budgets and circuit breakers stop retry storms.
- Compensation requests are unique per affected intent and hook.
- Dead letters preserve safe latest state and recommended operator actions.

## Known Limitations

Performance profiles are deterministic pytest profiles, not an external
distributed load-test service. Cross-region active-active scheduling is out of
scope for this feature.

## Evidence Placeholders

- Coverage: `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` passed with 430 tests and 90.18 percent coverage.
- Mixed lifecycle load: `tests/performance/reliability/test_mixed_lifecycle_load.py` passed with 5,000 active users across 50 tenants.
- Tenant burst fairness: `tests/performance/reliability/test_tenant_burst_fairness.py` passed with at least 95 percent compliant throughput retention.
- Resume after failure: `tests/integration/runtime/test_resume_after_failure_under_load.py` covers all required injection points.
- Breaker transition: `tests/unit/reliability/test_breakers.py` and `tests/performance/reliability/test_retry_storm_breaker.py` passed.
- Compensation and dead letter outcomes: `tests/unit/reliability/test_compensation.py`, `tests/unit/reliability/test_dead_letters.py`, and `tests/performance/reliability/test_compensation_dead_letter_load.py` passed.
- Artifact throughput: `tests/unit/storage/test_throughput.py`, `tests/integration/storage/test_artifact_throughput_controls.py`, and `tests/performance/reliability/test_artifact_export_throughput.py` passed.
- README and docs checks: reliability docs and README tests passed.
